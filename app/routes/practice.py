import random
from flask import Blueprint, jsonify, request, session
from app.models import TopicProgress, ExerciseStats, ErrorLog, ReviewItem
from app.utils import load_topic_content, load_topics_list, calculate_stars
from app import db
from datetime import datetime, timezone, timedelta

practice_bp = Blueprint("practice", __name__)

STAGE_MAP = {
    1: "ru_to_en",
    2: "en_to_ru",
    3: "fill_blank",
}

STAGE_TYPE_MAP = {
    1: "ru_en",
    2: "en_ru",
    3: "fill_blank",
}


@practice_bp.route("/topics/<topic_id>/practice/<int:stage>")
def get_practice(topic_id, stage):
    """Return exercises for a specific practice stage.

    Stage 1: Russian to English translation
    Stage 2: English to Russian translation
    Stage 3: Fill in the blank
    """
    if stage not in STAGE_MAP:
        return jsonify({"error": "Invalid stage. Must be 1, 2, or 3."}), 400
        
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    # Check unlock status
    if stage > 1:
        progress = TopicProgress.query.filter_by(topic_id=topic_id, user_id=user_id).first()
        if not progress or (progress.practice_stage or 0) < stage - 1:
            return jsonify({"error": "Previous stage not completed"}), 403

    content = load_topic_content(topic_id)
    if content is None:
        return jsonify({"error": "Topic not found"}), 404

    practice_key = STAGE_MAP[stage]
    exercises = content.get("practice", {}).get(practice_key, [])

    if not exercises:
        return jsonify({"error": "No exercises found for this stage"}), 404

    # Shuffle exercise order for variety
    shuffled = list(exercises)
    random.shuffle(shuffled)

    # For security, remove correct answers from fill_blank and en_to_ru
    sanitized = []
    for i, ex in enumerate(shuffled):
        clean = dict(ex)
        clean["index"] = i
        if stage == 2:
            # en_to_ru: shuffle options but track correct
            options = list(clean["options"])
            correct_text = options[clean["correct"]]
            random.shuffle(options)
            clean["options"] = options
            # Don't send correct index — server will verify
            del clean["correct"]
            clean["_correct_text"] = correct_text  # Will be stripped
        elif stage == 3:
            # fill_blank: shuffle options
            options = list(clean["options"])
            correct_text = options[clean["correct"]]
            random.shuffle(options)
            clean["options"] = options
            del clean["correct"]
            clean["_correct_text"] = correct_text
        elif stage == 1:
            # ru_to_en: shuffle word bank
            words = list(clean["words"])
            random.shuffle(words)
            clean["words"] = words
            # Don't send answer to client
            clean.pop("answer", None)
            clean.pop("accepted_answers", None)
            
        sanitized.append(clean)

    # Store correct answers in session-like mechanism
    # Actually, we'll verify on server side each time
    # Remove internal markers
    for ex in sanitized:
        ex.pop("_correct_text", None)

    # Weighted ordering based on ErrorLog
    error_counts = {}
    errors = ErrorLog.query.filter_by(user_id=user_id, topic_id=topic_id, exercise_type=STAGE_TYPE_MAP[stage]).all()
    for err in errors:
        error_counts[err.prompt] = error_counts.get(err.prompt, 0) + 1
        
    sanitized.sort(key=lambda x: error_counts.get(x.get("prompt") or x.get("sentence"), 0), reverse=True)

    return jsonify({
        "stage": stage,
        "stage_name": STAGE_MAP[stage],
        "topic_id": topic_id,
        "exercises": sanitized,
        "total": len(sanitized),
    })


@practice_bp.route("/topics/<topic_id>/practice/<int:stage>/check", methods=["POST"])
def check_answer(topic_id, stage):
    """Check a single answer for correctness."""
    if stage not in STAGE_MAP:
        return jsonify({"error": "Invalid stage"}), 400

    content = load_topic_content(topic_id)
    if content is None:
        return jsonify({"error": "Topic not found"}), 404

    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "No data provided"}), 400

    practice_key = STAGE_MAP[stage]
    exercises = content.get("practice", {}).get(practice_key, [])

    user_answer = data.get("answer", "").strip()
    exercise_prompt = data.get("prompt", "").strip()

    # Find the matching exercise by prompt/sentence
    target_exercise = None
    for ex in exercises:
        if stage == 3:
            if ex.get("sentence", "").strip() == exercise_prompt:
                target_exercise = ex
                break
        else:
            if ex.get("prompt", "").strip() == exercise_prompt:
                target_exercise = ex
                break

    if target_exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    is_correct = False
    correct_answer = ""
    explanation = ""

    if stage == 1:
        # RU to EN: compare user's constructed sentence to the answer
        correct_answers = target_exercise.get("accepted_answers", [])
        if "answer" in target_exercise and not correct_answers:
             correct_answers = [target_exercise["answer"]]
        
        normalized_user = user_answer.lower().strip().rstrip(".!?")
        is_correct = any(normalized_user == ans.lower().strip().rstrip(".!?") for ans in correct_answers)
        correct_answer = correct_answers[0] if correct_answers else ""
        explanation = target_exercise.get("explanation", "")
    elif stage == 2:
        # EN to RU: compare selected option text
        correct_idx = target_exercise["correct"]
        correct_answer = target_exercise["options"][correct_idx]
        is_correct = user_answer == correct_answer
        explanation = target_exercise.get("explanation", "")
    elif stage == 3:
        # Fill blank: compare selected option
        correct_idx = target_exercise["correct"]
        correct_answer = target_exercise["options"][correct_idx]
        explanation = target_exercise.get("explanation", "")
        is_correct = user_answer == correct_answer

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    # Update statistics
    exercise_type = STAGE_TYPE_MAP[stage]
    stats = ExerciseStats.query.filter_by(
        topic_id=topic_id, exercise_type=exercise_type, user_id=user_id
    ).first()
    if not stats:
        stats = ExerciseStats(
            topic_id=topic_id, exercise_type=exercise_type, user_id=user_id,
            total_attempts=0, correct_answers=0,
        )
        db.session.add(stats)

    stats.total_attempts = (stats.total_attempts or 0) + 1
    if is_correct:
        stats.correct_answers = (stats.correct_answers or 0) + 1
    else:
        # Log error
        err = ErrorLog(user_id=user_id, topic_id=topic_id, exercise_type=exercise_type, prompt=exercise_prompt)
        db.session.add(err)
        
    # SRS Update
    review_item = ReviewItem.query.filter_by(user_id=user_id, topic_id=topic_id, exercise_type=exercise_type, prompt=exercise_prompt).first()
    if not review_item:
        review_item = ReviewItem(user_id=user_id, topic_id=topic_id, exercise_type=exercise_type, prompt=exercise_prompt, interval=1, ease_factor=2.5)
        db.session.add(review_item)
        
    if is_correct:
        review_item.interval = max(1, int(review_item.interval * review_item.ease_factor))
        review_item.ease_factor = min(2.5, review_item.ease_factor + 0.1)
    else:
        review_item.interval = 1
        review_item.ease_factor = max(1.3, review_item.ease_factor - 0.2)
        
    review_item.next_review_at = datetime.now(timezone.utc) + timedelta(days=review_item.interval)

    db.session.commit()

    return jsonify({
        "correct": is_correct,
        "correct_answer": correct_answer,
        "explanation": explanation,
    })


@practice_bp.route("/topics/<topic_id>/practice/<int:stage>/complete", methods=["POST"])
def complete_stage(topic_id, stage):
    """Mark a practice stage as completed and update progress."""
    if stage not in STAGE_MAP:
        return jsonify({"error": "Invalid stage"}), 400

    data = request.get_json(silent=True) or {}
    correct_count = data.get("correct", 0)
    total_count = data.get("total", 1)

    stars = calculate_stars(correct_count, total_count)

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    progress = TopicProgress.query.filter_by(topic_id=topic_id, user_id=user_id).first()
    if not progress:
        progress = TopicProgress(
            topic_id=topic_id, user_id=user_id, practice_stage=0, practice_score=0,
            best_score=0, stars_ru_en=0, stars_en_ru=0, stars_fill_blank=0,
        )
        db.session.add(progress)

    # Update stage progress
    if stage > (progress.practice_stage or 0):
        progress.practice_stage = stage

    # Update stars for this stage
    if stage == 1:
        progress.stars_ru_en = max(progress.stars_ru_en or 0, stars)
    elif stage == 2:
        progress.stars_en_ru = max(progress.stars_en_ru or 0, stars)
    elif stage == 3:
        progress.stars_fill_blank = max(progress.stars_fill_blank or 0, stars)

    # Update score
    # Score should track best performance
    progress.best_score = max(progress.best_score or 0, correct_count)
    progress.practice_score = progress.best_score  # Update current as best for compatibility

    # Mark topic as completed if all 3 stages done
    if (progress.practice_stage or 0) >= 3:
        progress.completed = True

    db.session.commit()

    return jsonify({
        "status": "ok",
        "stars": stars,
        "progress": progress.to_dict(),
    })


@practice_bp.route("/practice/mix", methods=["GET"])
def get_mix_practice():
    """Returns a mix of exercises from completed topics for review."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    # Get items due for review
    now = datetime.now(timezone.utc)
    due_items = ReviewItem.query.filter(ReviewItem.user_id == user_id, ReviewItem.next_review_at <= now).all()
    
    # Also get some random errors
    errors = ErrorLog.query.filter_by(user_id=user_id).order_by(db.func.random()).limit(5).all()
    
    # We need to load content to reconstruct the exercises
    topics_meta = load_topics_list()
    mix = []
    
    # Pool of prompts to include
    target_prompts = set()
    for item in due_items:
        target_prompts.add((item.topic_id, item.exercise_type, item.prompt))
    for err in errors:
        target_prompts.add((err.topic_id, err.exercise_type, err.prompt))
        
    # If no due items or errors, just pick random completed topics
    if not target_prompts:
        completed = TopicProgress.query.filter_by(user_id=user_id, completed=True).all()
        if not completed:
            return jsonify({"error": "No completed topics yet. Finish a topic to unlock mix practice."}), 400
        
        # Pick 2 random completed topics
        random_topics = random.sample(completed, min(2, len(completed)))
        for p in random_topics:
            content = load_topic_content(p.topic_id)
            if content:
                for st_type, st_key in [(1, "ru_to_en"), (2, "en_to_ru"), (3, "fill_blank")]:
                    ex_list = content.get("practice", {}).get(st_key, [])
                    if ex_list:
                        # Pick 2 random exercises from this stage
                        for ex in random.sample(ex_list, min(2, len(ex_list))):
                            prompt = ex.get("prompt") or ex.get("sentence")
                            target_prompts.add((p.topic_id, STAGE_TYPE_MAP[st_type], prompt))

    # Reconstruct exercises
    for topic_id, ex_type, prompt in target_prompts:
        content = load_topic_content(topic_id)
        if not content: continue
        
        # Find stage mapping
        stage_num = next((k for k, v in STAGE_TYPE_MAP.items() if v == ex_type), None)
        if not stage_num: continue
        
        ex_list = content.get("practice", {}).get(STAGE_MAP[stage_num], [])
        for ex in ex_list:
            ex_prompt = ex.get("prompt") or ex.get("sentence")
            if ex_prompt == prompt:
                clean = dict(ex)
                clean["topic_id"] = topic_id
                clean["stage"] = stage_num
                clean["stage_name"] = STAGE_MAP[stage_num]
                
                if stage_num == 2 or stage_num == 3:
                    options = list(clean["options"])
                    random.shuffle(options)
                    clean["options"] = options
                    clean.pop("correct", None)
                elif stage_num == 1:
                    words = list(clean["words"])
                    random.shuffle(words)
                    clean["words"] = words
                    clean.pop("answer", None)
                    clean.pop("accepted_answers", None)
                    
                mix.append(clean)
                break
                
        if len(mix) >= 15: # Limit max exercises in mix
            break
            
    random.shuffle(mix)
    
    return jsonify({
        "exercises": mix,
        "total": len(mix)
    })

@practice_bp.route("/mistakes", methods=["GET"])
def get_mistakes_stats():
    """Return top mistakes for the user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
        
    errors = ErrorLog.query.filter_by(user_id=user_id).all()
    counts = {}
    for err in errors:
        key = (err.topic_id, err.prompt)
        counts[key] = counts.get(key, 0) + 1
        
    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return jsonify({
        "mistakes": [{"topic_id": k[0], "prompt": k[1], "count": v} for k, v in top]
    })

