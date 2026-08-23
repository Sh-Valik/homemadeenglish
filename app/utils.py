import json
import os
from flask import current_app


def get_content_dir():
    """Return the path to the content directory."""
    return current_app.config["CONTENT_DIR"]


def load_topics_list():
    """Load the list of all topics with metadata."""
    topics_file = os.path.join(get_content_dir(), "topics.json")
    with open(topics_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_topic_content(topic_id):
    """Load full content for a specific topic."""
    topic_file = os.path.join(get_content_dir(), "topics", f"{topic_id}.json")
    if not os.path.exists(topic_file):
        return None
    with open(topic_file, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_stars(correct, total):
    """Calculate star rating based on accuracy.

    >= 90% = 3 stars
    >= 70% = 2 stars
    >= 50% = 1 star
    < 50% = 0 stars
    """
    if total == 0:
        return 0
    pct = correct / total * 100
    if pct >= 90:
        return 3
    elif pct >= 70:
        return 2
    elif pct >= 50:
        return 1
    return 0
