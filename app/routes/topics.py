from flask import Blueprint, jsonify, request, session
from app.models import TopicProgress
from app.utils import load_topics_list, load_topic_content
from app import db

topics_bp = Blueprint("topics", __name__)


@topics_bp.route("/topics")
def get_topics():
    """Return list of all topics with progress information."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    topics_meta = load_topics_list()
    progress_map = {
        p.topic_id: p.to_dict()
        for p in TopicProgress.query.filter_by(user_id=user_id).all()
    }

    result = []
    for i, topic in enumerate(topics_meta["topics"]):
        topic_id = topic["id"]
        prog = progress_map.get(topic_id, {})

        # First topic is always unlocked; others require previous topic completed
        if i == 0:
            unlocked = True
        else:
            prev_id = topics_meta["topics"][i - 1]["id"]
            prev_prog = progress_map.get(prev_id, {})
            unlocked = prev_prog.get("completed", False)

        result.append({
            "id": topic_id,
            "title": topic["title"],
            "title_ru": topic["title_ru"],
            "icon": topic["icon"],
            "level": topic.get("level", i + 1),
            "unlocked": unlocked,
            "progress": prog,
        })

    return jsonify(result)


@topics_bp.route("/topics/<topic_id>")
def get_topic(topic_id):
    """Return full topic content (theory)."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    content = load_topic_content(topic_id)
    if content is None:
        return jsonify({"error": "Topic not found"}), 404

    # Check unlock status
    topics_meta = load_topics_list()
    topic_index = next((i for i, t in enumerate(topics_meta["topics"]) if t["id"] == topic_id), -1)
    
    if topic_index > 0:
        prev_id = topics_meta["topics"][topic_index - 1]["id"]
        prev_prog = TopicProgress.query.filter_by(topic_id=prev_id, user_id=user_id).first()
        if not prev_prog or not prev_prog.completed:
            return jsonify({"error": "Topic is locked"}), 403

    progress = TopicProgress.query.filter_by(topic_id=topic_id, user_id=user_id).first()
    return jsonify({
        "topic": content,
        "progress": progress.to_dict() if progress else None,
    })


@topics_bp.route("/topics/<topic_id>/theory/complete", methods=["POST"])
def complete_theory(topic_id):
    """Mark theory as completed for a topic."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    # Check unlock status
    topics_meta = load_topics_list()
    topic_index = next((i for i, t in enumerate(topics_meta["topics"]) if t["id"] == topic_id), -1)
    
    if topic_index > 0:
        prev_id = topics_meta["topics"][topic_index - 1]["id"]
        prev_prog = TopicProgress.query.filter_by(topic_id=prev_id, user_id=user_id).first()
        if not prev_prog or not prev_prog.completed:
            return jsonify({"error": "Topic is locked"}), 403

    progress = TopicProgress.query.filter_by(topic_id=topic_id, user_id=user_id).first()
    if not progress:
        progress = TopicProgress(topic_id=topic_id, user_id=user_id)
        db.session.add(progress)

    progress.theory_completed = True
    db.session.commit()

    return jsonify({"status": "ok", "progress": progress.to_dict()})


@topics_bp.route("/progress/reset/<topic_id>", methods=["POST"])
def reset_progress(topic_id):
    """Reset all progress for a topic."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    progress = TopicProgress.query.filter_by(topic_id=topic_id, user_id=user_id).first()
    if progress:
        progress.theory_completed = False
        progress.practice_stage = 0
        progress.practice_score = 0
        progress.completed = False
        progress.stars_ru_en = 0
        progress.stars_en_ru = 0
        progress.stars_fill_blank = 0
        db.session.commit()

    return jsonify({"status": "ok"})
