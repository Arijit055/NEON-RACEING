import uuid
from datetime import datetime

from .extensions import db

# Uuid/JSON below are SQLAlchemy's portable generic types (SQLAlchemy 2.0+):
# they render as native UUID/JSONB on Postgres in production, and as
# CHAR/TEXT on SQLite for local dev — unlike the old postgres-dialect
# UUID/ARRAY types, which only work against a real Postgres database.


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)

    save = db.relationship("Save", backref="user", uselist=False, cascade="all, delete-orphan")


class Save(db.Model):
    __tablename__ = "saves"

    user_id = db.Column(db.Uuid(as_uuid=False), db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    coins = db.Column(db.Integer, nullable=False, default=0)
    unlocked_cars = db.Column(db.JSON, nullable=False, default=lambda: [0])
    selected_car = db.Column(db.Integer, nullable=False, default=0)
    engine_level = db.Column(db.Integer, nullable=False, default=1)
    magnet_level = db.Column(db.Integer, nullable=False, default=1)
    has_shield = db.Column(db.Boolean, nullable=False, default=False)
    high_score = db.Column(db.Integer, nullable=False, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "coins": self.coins,
            "unlockedCars": self.unlocked_cars,
            "selectedCar": self.selected_car,
            "engineLevel": self.engine_level,
            "magnetLevel": self.magnet_level,
            "hasShield": self.has_shield,
            "highScore": self.high_score,
        }


class GameSession(db.Model):
    """One row per run attempt — the anti-cheat anchor. Duration is computed
    server-side from started_at/ended_at, never trusted from the client."""

    __tablename__ = "game_sessions"

    id = db.Column(db.Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Uuid(as_uuid=False), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    submitted = db.Column(db.Boolean, default=False)


class LeaderboardEntry(db.Model):
    """Weekly leaderboard — one best score per user per week."""

    __tablename__ = "leaderboard_entries"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Uuid(as_uuid=False), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    week_key = db.Column(db.String(10), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "week_key", name="uq_user_week"),)


class WeeklyChallenge(db.Model):
    __tablename__ = "weekly_challenges"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    week_key = db.Column(db.String(10), nullable=False)
    challenge_type = db.Column(db.String(30), nullable=False)  # 'distance', 'coins_collected', ...
    target_value = db.Column(db.Integer, nullable=False)
    reward_coins = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.String(255), nullable=False)


class UserChallengeProgress(db.Model):
    __tablename__ = "user_challenge_progress"

    user_id = db.Column(db.Uuid(as_uuid=False), db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("weekly_challenges.id", ondelete="CASCADE"), primary_key=True
    )
    current_value = db.Column(db.Integer, nullable=False, default=0)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    reward_claimed = db.Column(db.Boolean, nullable=False, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
