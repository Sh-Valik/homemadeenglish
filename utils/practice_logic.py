"""Practice logic — exercise preparation and answer verification."""

import random
from utils.content_loader import load_topic_content, load_topics_list

STAGE_MAP = {1: "ru_to_en", 2: "en_to_ru", 3: "fill_blank"}
STAGE_TYPE_MAP = {1: "ru_en", 2: "en_ru", 3: "fill_blank"}
STAGE_LABELS = {
    1: "Переведите на английский",
    2: "Переведите на русский",
    3: "Вставьте пропущенное слово",
}


def prepare_exercises(topic_id, stage, error_log=None):
    """Load and prepare exercises for a practice stage.

    Returns a list of exercise dicts ready for the UI, or None if topic not found.
    """
    content = load_topic_content(topic_id)
    if content is None:
        return None

    practice_key = STAGE_MAP.get(stage)
    if not practice_key:
        return None

    exercises = content.get("practice", {}).get(practice_key, [])
    if not exercises:
        return None

    shuffled = list(exercises)
    random.shuffle(shuffled)

    prepared = []
    for ex in shuffled:
        clean = dict(ex)
        if stage == 1:
            words = list(clean.get("words", []))
            random.shuffle(words)
            clean["words"] = words
            # Keep answer/accepted_answers server-side only (not sent to client in Flask,
            # but here we keep them since everything is server-side)
        elif stage in (2, 3):
            options = list(clean.get("options", []))
            correct_text = options[clean["correct"]]
            random.shuffle(options)
            clean["options"] = options
            clean["_correct_text"] = correct_text
        prepared.append(clean)

    # Sort by error frequency (most-errored first)
    if error_log:
        ex_type = STAGE_TYPE_MAP[stage]
        error_counts = {}
        for err in error_log:
            if err["topic_id"] == topic_id and err["exercise_type"] == ex_type:
                error_counts[err["prompt"]] = error_counts.get(err["prompt"], 0) + 1
        prepared.sort(
            key=lambda x: error_counts.get(x.get("prompt") or x.get("sentence"), 0),
            reverse=True,
        )

    return prepared


def check_answer(topic_id, stage, exercise, user_answer):
    """Check a user's answer against the correct answer.

    Returns dict: {correct: bool, correct_answer: str, explanation: str}
    """
    content = load_topic_content(topic_id)
    if content is None:
        return {"correct": False, "correct_answer": "", "explanation": ""}

    practice_key = STAGE_MAP[stage]
    exercises = content.get("practice", {}).get(practice_key, [])

    # Find original exercise by prompt
    prompt = exercise.get("prompt") or exercise.get("sentence", "")
    target = None
    for ex in exercises:
        if stage == 3:
            if ex.get("sentence", "").strip() == prompt.strip():
                target = ex
                break
        else:
            if ex.get("prompt", "").strip() == prompt.strip():
                target = ex
                break

    if target is None:
        return {"correct": False, "correct_answer": "", "explanation": ""}

    is_correct = False
    correct_answer = ""
    explanation = target.get("explanation", "")

    if stage == 1:
        correct_answers = target.get("accepted_answers", [])
        if "answer" in target and not correct_answers:
            correct_answers = [target["answer"]]
        normalized_user = user_answer.lower().strip().rstrip(".!?")
        is_correct = any(
            normalized_user == ans.lower().strip().rstrip(".!?")
            for ans in correct_answers
        )
        correct_answer = correct_answers[0] if correct_answers else ""
    elif stage == 2:
        correct_idx = target["correct"]
        correct_answer = target["options"][correct_idx]
        is_correct = user_answer.strip() == correct_answer.strip()
    elif stage == 3:
        correct_idx = target["correct"]
        correct_answer = target["options"][correct_idx]
        is_correct = user_answer.strip() == correct_answer.strip()

    return {
        "correct": is_correct,
        "correct_answer": correct_answer,
        "explanation": explanation,
    }


def prepare_mix_exercises():
    """Prepare mixed exercises from completed topics for review."""
    from utils.session_state import get_due_review_items, get_error_log, is_logged_in
    from utils.db import get_db_session, TopicProgress
    import streamlit as st

    if not is_logged_in():
        return None

    due_items = get_due_review_items()
    error_log = get_error_log()
    random_errors = list(error_log)
    random.shuffle(random_errors)
    random_errors = random_errors[:5]

    target_prompts = set()
    for item in due_items:
        target_prompts.add((item["topic_id"], item["exercise_type"], item["prompt"]))
    for err in random_errors:
        target_prompts.add((err["topic_id"], err["exercise_type"], err["prompt"]))

    # If no due items, pick from random completed topics
    if not target_prompts:
        with next(get_db_session()) as db:
            completed_topics = db.query(TopicProgress).filter_by(
                user_id=st.session_state.user_id, completed=True
            ).all()
            completed = [p.topic_id for p in completed_topics]
            
        if not completed:
            return None
        random_topics = random.sample(completed, min(2, len(completed)))
        for tid in random_topics:
            content = load_topic_content(tid)
            if content:
                for st_num, st_key in [(1, "ru_to_en"), (2, "en_to_ru"), (3, "fill_blank")]:
                    ex_list = content.get("practice", {}).get(st_key, [])
                    if ex_list:
                        for ex in random.sample(ex_list, min(2, len(ex_list))):
                            p = ex.get("prompt") or ex.get("sentence")
                            target_prompts.add((tid, STAGE_TYPE_MAP[st_num], p))

    mix = []
    for topic_id, ex_type, prompt in target_prompts:
        content = load_topic_content(topic_id)
        if not content:
            continue
        stage_num = next((k for k, v in STAGE_TYPE_MAP.items() if v == ex_type), None)
        if not stage_num:
            continue
        ex_list = content.get("practice", {}).get(STAGE_MAP[stage_num], [])
        for ex in ex_list:
            ex_prompt = ex.get("prompt") or ex.get("sentence")
            if ex_prompt == prompt:
                clean = dict(ex)
                clean["topic_id"] = topic_id
                clean["stage"] = stage_num
                if stage_num in (2, 3):
                    options = list(clean["options"])
                    random.shuffle(options)
                    clean["options"] = options
                elif stage_num == 1:
                    words = list(clean["words"])
                    random.shuffle(words)
                    clean["words"] = words
                mix.append(clean)
                break
        if len(mix) >= 15:
            break

    random.shuffle(mix)
    return mix if mix else None
