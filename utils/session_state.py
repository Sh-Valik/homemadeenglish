"""Session state management and database interactions."""

import streamlit as st
from datetime import datetime, timezone, timedelta
from utils.db import get_db_session, User, TopicProgress, ExerciseStats, ErrorLog, ReviewItem
from sqlalchemy import func


def init_session_state():
    """Initialize base session state keys if they don't exist."""
    defaults = {
        "user_id": None,
        "username": None,
        "practice": None,
        "mix_practice": None,
        "selected_topic_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def is_logged_in():
    return st.session_state.get("user_id") is not None


def get_progress(topic_id):
    """Get progress dict for a topic from the DB, or empty defaults."""
    if not is_logged_in():
        return {}
        
    with next(get_db_session()) as db:
        prog = db.query(TopicProgress).filter_by(
            user_id=st.session_state.user_id, topic_id=topic_id
        ).first()
        
        if prog:
            return {
                "theory_completed": prog.theory_completed,
                "practice_stage": prog.practice_stage,
                "practice_score": prog.practice_score,
                "best_score": prog.best_score,
                "completed": prog.completed,
                "stars_ru_en": prog.stars_ru_en,
                "stars_en_ru": prog.stars_en_ru,
                "stars_fill_blank": prog.stars_fill_blank,
            }
            
    return {
        "theory_completed": False,
        "practice_stage": 0,
        "practice_score": 0,
        "best_score": 0,
        "completed": False,
        "stars_ru_en": 0,
        "stars_en_ru": 0,
        "stars_fill_blank": 0,
    }


def complete_theory(topic_id):
    """Mark theory as completed."""
    if not is_logged_in():
        return
        
    with next(get_db_session()) as db:
        prog = db.query(TopicProgress).filter_by(
            user_id=st.session_state.user_id, topic_id=topic_id
        ).first()
        
        if not prog:
            prog = TopicProgress(user_id=st.session_state.user_id, topic_id=topic_id)
            db.add(prog)
            
        prog.theory_completed = True
        db.commit()


def complete_stage(topic_id, stage, correct_count, total_count, stars):
    """Mark a practice stage as completed and update progress in DB."""
    if not is_logged_in():
        return
        
    with next(get_db_session()) as db:
        prog = db.query(TopicProgress).filter_by(
            user_id=st.session_state.user_id, topic_id=topic_id
        ).first()
        
        if not prog:
            prog = TopicProgress(user_id=st.session_state.user_id, topic_id=topic_id)
            db.add(prog)

        if stage > (prog.practice_stage or 0):
            prog.practice_stage = stage

        if stage == 1:
            prog.stars_ru_en = max(prog.stars_ru_en or 0, stars)
        elif stage == 2:
            prog.stars_en_ru = max(prog.stars_en_ru or 0, stars)
        elif stage == 3:
            prog.stars_fill_blank = max(prog.stars_fill_blank or 0, stars)

        prog.best_score = max(prog.best_score or 0, correct_count)
        prog.practice_score = prog.best_score

        if (prog.practice_stage or 0) >= 3:
            prog.completed = True

        db.commit()


def is_topic_unlocked(topic_id, topics_list):
    """Check if a topic is unlocked based on sequential completion."""
    if not is_logged_in():
        return False
        
    topics = topics_list["topics"]
    for i, t in enumerate(topics):
        if t["id"] == topic_id:
            if i == 0:
                return True
            prev_id = topics[i - 1]["id"]
            with next(get_db_session()) as db:
                prev_prog = db.query(TopicProgress).filter_by(
                    user_id=st.session_state.user_id, topic_id=prev_id
                ).first()
                return prev_prog.completed if prev_prog else False
    return False


def log_exercise_result(topic_id, exercise_type, is_correct, prompt):
    """Log an exercise attempt result to DB and update SRS."""
    if not is_logged_in():
        return
        
    with next(get_db_session()) as db:
        # Update Stats
        stats = db.query(ExerciseStats).filter_by(
            user_id=st.session_state.user_id, topic_id=topic_id, exercise_type=exercise_type
        ).first()
        
        if not stats:
            stats = ExerciseStats(
                user_id=st.session_state.user_id, topic_id=topic_id, exercise_type=exercise_type,
                total_attempts=0, correct_answers=0
            )
            db.add(stats)

        stats.total_attempts = (stats.total_attempts or 0) + 1
        if is_correct:
            stats.correct_answers = (stats.correct_answers or 0) + 1
        else:
            err = ErrorLog(
                user_id=st.session_state.user_id, topic_id=topic_id, 
                exercise_type=exercise_type, prompt=prompt
            )
            db.add(err)

        # SRS update
        item = db.query(ReviewItem).filter_by(
            user_id=st.session_state.user_id, topic_id=topic_id, 
            exercise_type=exercise_type, prompt=prompt
        ).first()
        
        if not item:
            item = ReviewItem(
                user_id=st.session_state.user_id, topic_id=topic_id, 
                exercise_type=exercise_type, prompt=prompt,
                interval=1, ease_factor=2.5
            )
            db.add(item)
            
        if is_correct:
            item.interval = max(1, int(item.interval * item.ease_factor))
            item.ease_factor = min(2.5, item.ease_factor + 0.1)
        else:
            item.interval = 1
            item.ease_factor = max(1.3, item.ease_factor - 0.2)
            
        item.next_review_at = datetime.now(timezone.utc) + timedelta(days=item.interval)
        
        db.commit()


def get_stats():
    """Return overall learning statistics from DB."""
    if not is_logged_in():
        return {
            "topics_completed": 0, "topics_started": 0, "total_stars": 0,
            "max_possible_stars": 0, "total_exercises_attempted": 0,
            "total_correct_answers": 0, "overall_accuracy": 0,
        }
        
    with next(get_db_session()) as db:
        progress_items = db.query(TopicProgress).filter_by(user_id=st.session_state.user_id).all()
        stats_items = db.query(ExerciseStats).filter_by(user_id=st.session_state.user_id).all()

        topics_completed = sum(1 for p in progress_items if p.completed)
        topics_started = sum(1 for p in progress_items if p.theory_completed or (p.practice_stage or 0) > 0)
        total_stars = sum(
            (p.stars_ru_en or 0) + (p.stars_en_ru or 0) + (p.stars_fill_blank or 0)
            for p in progress_items
        )
        total_attempts = sum((s.total_attempts or 0) for s in stats_items)
        total_correct = sum((s.correct_answers or 0) for s in stats_items)

        return {
            "topics_completed": topics_completed,
            "topics_started": topics_started,
            "total_stars": total_stars,
            "max_possible_stars": len(progress_items) * 9 if progress_items else 0,
            "total_exercises_attempted": total_attempts,
            "total_correct_answers": total_correct,
            "overall_accuracy": round(total_correct / total_attempts * 100, 1) if total_attempts > 0 else 0,
        }


def get_top_mistakes(limit=10):
    """Return top repeated mistakes from DB."""
    if not is_logged_in():
        return []
        
    with next(get_db_session()) as db:
        # Group by topic_id and prompt, count occurrences
        errors = db.query(
            ErrorLog.topic_id, ErrorLog.prompt, func.count(ErrorLog.id).label('count')
        ).filter_by(user_id=st.session_state.user_id)\
         .group_by(ErrorLog.topic_id, ErrorLog.prompt)\
         .order_by(func.count(ErrorLog.id).desc())\
         .limit(limit).all()
         
        return [{"topic_id": e.topic_id, "prompt": e.prompt, "count": e.count} for e in errors]


def get_due_review_items():
    """Return SRS items due for review from DB."""
    if not is_logged_in():
        return []
        
    now = datetime.now(timezone.utc)
    with next(get_db_session()) as db:
        due = db.query(ReviewItem).filter(
            ReviewItem.user_id == st.session_state.user_id,
            ReviewItem.next_review_at <= now
        ).all()
        
        return [{"topic_id": i.topic_id, "exercise_type": i.exercise_type, "prompt": i.prompt} for i in due]


def get_error_log():
    """Return error log for the current user to be used in practice exercises priority."""
    if not is_logged_in():
        return []
        
    with next(get_db_session()) as db:
        errors = db.query(ErrorLog).filter_by(user_id=st.session_state.user_id).all()
        return [{"topic_id": e.topic_id, "exercise_type": e.exercise_type, "prompt": e.prompt} for e in errors]


def reset_all_progress():
    """Delete all progress and stats for the current user from DB."""
    if not is_logged_in():
        return
        
    with next(get_db_session()) as db:
        db.query(TopicProgress).filter_by(user_id=st.session_state.user_id).delete()
        db.query(ExerciseStats).filter_by(user_id=st.session_state.user_id).delete()
        db.query(ErrorLog).filter_by(user_id=st.session_state.user_id).delete()
        db.query(ReviewItem).filter_by(user_id=st.session_state.user_id).delete()
        db.commit()
        
    # Reset local state
    st.session_state.practice = None
    st.session_state.mix_practice = None
