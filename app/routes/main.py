from flask import Blueprint, render_template, jsonify, session
from app.models import TopicProgress, ExerciseStats
from app import db

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Serve the main SPA page."""
    return render_template("index.html")


@main_bp.route("/api/stats")
def get_stats():
    """Return overall learning statistics for the current user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    all_progress = TopicProgress.query.filter_by(user_id=user_id).all()
    all_stats = ExerciseStats.query.filter_by(user_id=user_id).all()

    topics_completed = sum(1 for p in all_progress if p.completed)
    topics_started = sum(1 for p in all_progress if p.theory_completed or p.practice_stage > 0)
    total_stars = sum(p.stars_ru_en + p.stars_en_ru + p.stars_fill_blank for p in all_progress)

    total_attempts = sum(s.total_attempts for s in all_stats)
    total_correct = sum(s.correct_answers for s in all_stats)

    return jsonify({
        "topics_completed": topics_completed,
        "topics_started": topics_started,
        "total_stars": total_stars,
        "max_possible_stars": len(all_progress) * 9 if all_progress else 0,
        "total_exercises_attempted": total_attempts,
        "total_correct_answers": total_correct,
        "overall_accuracy": round(total_correct / total_attempts * 100, 1) if total_attempts > 0 else 0,
    })
