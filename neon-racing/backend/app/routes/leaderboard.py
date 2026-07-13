from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import LeaderboardEntry, Save, User
from ..utils import get_week_key

leaderboard_bp = Blueprint("leaderboard", __name__)


@leaderboard_bp.route("/weekly", methods=["GET"])
def weekly_leaderboard():
    """Top scores for a given week (defaults to the current week).
    Public endpoint — no login needed to view."""
    week_key = request.args.get("week", get_week_key())
    rows = (
        db.session.query(LeaderboardEntry.score, User.username)
        .join(User, User.id == LeaderboardEntry.user_id)
        .filter(LeaderboardEntry.week_key == week_key)
        .order_by(LeaderboardEntry.score.desc())
        .limit(50)
        .all()
    )
    return jsonify([{"username": u, "score": s} for s, u in rows])


@leaderboard_bp.route("/global", methods=["GET"])
def global_leaderboard():
    """All-time top scores, ranked by each player's best-ever run
    (saves.high_score). This is the 'global leaderboard' feature."""
    rows = (
        db.session.query(Save.high_score, User.username)
        .join(User, User.id == Save.user_id)
        .order_by(Save.high_score.desc())
        .limit(50)
        .all()
    )
    return jsonify([{"username": u, "highScore": h} for h, u in rows])
