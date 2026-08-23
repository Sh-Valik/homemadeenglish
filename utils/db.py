"""Database models and setup for English Learner."""

import os
from datetime import datetime, timezone
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Index, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from werkzeug.security import generate_password_hash, check_password_hash

# --- Database Configuration ---
# Use external DB if configured in secrets, else local SQLite
try:
    if "DB_URL" in st.secrets:
        DB_URL = st.secrets["DB_URL"]
    else:
        DB_URL = None
except Exception:
    DB_URL = None

if not DB_URL:
    # Use an absolute path for local SQLite to avoid cwd issues
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_URL = f"sqlite:///{os.path.join(BASE_DIR, 'learner.db')}"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Models ---

class User(Base):
    """User model for authentication."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class TopicProgress(Base):
    """Tracks user progress through each topic."""
    __tablename__ = "topic_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    topic_id = Column(String(100), nullable=False)
    theory_completed = Column(Boolean, default=False)
    # 0 = not started, 1 = ru_en done, 2 = en_ru done, 3 = fill_blank done
    practice_stage = Column(Integer, default=0)
    practice_score = Column(Integer, default=0)
    best_score = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    # Stars earned: 0-3
    stars_ru_en = Column(Integer, default=0)
    stars_en_ru = Column(Integer, default=0)
    stars_fill_blank = Column(Integer, default=0)
    updated_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_user_topic"),
    )


class ExerciseStats(Base):
    """Tracks statistics for exercise attempts."""
    __tablename__ = "exercise_stats"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    topic_id = Column(String(100), nullable=False)
    exercise_type = Column(String(20), nullable=False)  # ru_en, en_ru, fill_blank
    total_attempts = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    updated_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", "exercise_type", name="uq_user_topic_exercise"),
    )


class ErrorLog(Base):
    """Logs individual errors for the 'My Mistakes' feature."""
    __tablename__ = "error_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    topic_id = Column(String(100), nullable=False)
    exercise_type = Column(String(20), nullable=False)
    prompt = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_user_topic_prompt", "user_id", "topic_id", "prompt"),
    )


class ReviewItem(Base):
    """Spaced Repetition System (SRS) review queue."""
    __tablename__ = "review_queue"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    topic_id = Column(String(100), nullable=False)
    exercise_type = Column(String(20), nullable=False)
    prompt = Column(Text, nullable=False)
    
    next_review_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    interval = Column(Integer, default=1)  # Interval in days
    ease_factor = Column(Float, default=2.5) # SM-2 ease factor
    
    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", "exercise_type", "prompt", name="uq_review_item"),
    )


def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db_session():
    """Context manager for DB sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
