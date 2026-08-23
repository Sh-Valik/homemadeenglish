from datetime import datetime, timezone
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """User model for authentication."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class TopicProgress(db.Model):
    """Tracks user progress through each topic."""

    __tablename__ = "topic_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.String(100), nullable=False)
    theory_completed = db.Column(db.Boolean, default=False)
    # 0 = not started, 1 = ru_en done, 2 = en_ru done, 3 = fill_blank done
    practice_stage = db.Column(db.Integer, default=0)
    practice_score = db.Column(db.Integer, default=0)
    best_score = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    # Stars earned: 0-3
    stars_ru_en = db.Column(db.Integer, default=0)
    stars_en_ru = db.Column(db.Integer, default=0)
    stars_fill_blank = db.Column(db.Integer, default=0)
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "topic_id", name="uq_user_topic"),
    )

    def to_dict(self):
        return {
            "topic_id": self.topic_id,
            "theory_completed": self.theory_completed,
            "practice_stage": self.practice_stage,
            "practice_score": self.practice_score,
            "best_score": self.best_score,
            "completed": self.completed,
            "stars_ru_en": self.stars_ru_en,
            "stars_en_ru": self.stars_en_ru,
            "stars_fill_blank": self.stars_fill_blank,
        }


class ExerciseStats(db.Model):
    """Tracks statistics for exercise attempts."""

    __tablename__ = "exercise_stats"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.String(100), nullable=False)
    exercise_type = db.Column(db.String(20), nullable=False)  # ru_en, en_ru, fill_blank
    total_attempts = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "topic_id", "exercise_type", name="uq_user_topic_exercise"),
    )

    def to_dict(self):
        return {
            "topic_id": self.topic_id,
            "exercise_type": self.exercise_type,
            "total_attempts": self.total_attempts,
            "correct_answers": self.correct_answers,
            "accuracy": round(self.correct_answers / self.total_attempts * 100, 1)
            if self.total_attempts > 0
            else 0,
        }


class ErrorLog(db.Model):
    """Logs individual errors for the 'My Mistakes' feature."""

    __tablename__ = "error_log"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.String(100), nullable=False)
    exercise_type = db.Column(db.String(20), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.Index("idx_user_topic_prompt", "user_id", "topic_id", "prompt"),
    )

    def to_dict(self):
        return {
            "topic_id": self.topic_id,
            "exercise_type": self.exercise_type,
            "prompt": self.prompt,
            "created_at": self.created_at.isoformat(),
        }


class ReviewItem(db.Model):
    """Spaced Repetition System (SRS) review queue."""

    __tablename__ = "review_queue"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.String(100), nullable=False)
    exercise_type = db.Column(db.String(20), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    
    next_review_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    interval = db.Column(db.Integer, default=1)  # Interval in days
    ease_factor = db.Column(db.Float, default=2.5) # SM-2 ease factor
    
    __table_args__ = (
        db.UniqueConstraint("user_id", "topic_id", "exercise_type", "prompt", name="uq_review_item"),
    )

    def to_dict(self):
        return {
            "topic_id": self.topic_id,
            "exercise_type": self.exercise_type,
            "prompt": self.prompt,
            "next_review_at": self.next_review_at.isoformat(),
            "interval": self.interval,
        }
