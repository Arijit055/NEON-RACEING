from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import GameSession, Save, LeaderboardEntry, WeeklyChallenge, UserChallengeProgress
from ..services.anti_cheat import validate_run
from ..utils import get_week_key

run_bp = Blueprint("run", __name__)


@run_bp.route("/start", methods=["POST"])
@jwt_required()
def start_run():
    user_id = get_jwt_identity()
    session = GameSession(user_id=user_id)
    db.session.add(session)
    db.session.commit()
    return jsonify({"sessionId": str(session.id), "startedAt": session.started_at.isoformat()}), 201


@run_bp.route("/submit", methods=["POST"])
@jwt_required()
def submit_run():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    session_id = data.get("sessionId")
    distance = data.get("distance")
    coins_collected = data.get("coinsCollected")

    if not session_id or distance is None or coins_collected is None:
        return jsonify({"error": "sessionId, distance, and coinsCollected are required"}), 400

    session = GameSession.query.filter_by(id=session_id, user_id=user_id).with_for_update().first()
    if not session:
        return jsonify({"error": "Session not found"}), 404
    if session.submitted:
        return jsonify({"error": "Session already submitted"}), 409

    duration_seconds = max((datetime.utcnow() - session.started_at).total_seconds(), 1)

    save = Save.query.get(user_id)

    result = validate_run(
        claimed_distance=distance,
        claimed_coins=coins_collected,
        duration_seconds=duration_seconds,
        engine_level=save.engine_level,  # from DB, never from the client
    )
    valid_distance = result["distance"]
    valid_coins_earned = result["coins"]
    flagged = result["flagged"]

    save.coins += valid_coins_earned
    save.high_score = max(save.high_score, int(valid_distance))

    session.ended_at = datetime.utcnow()
    session.submitted = True

    # Weekly leaderboard — best score per user per week
    week_key = get_week_key()
    entry = LeaderboardEntry.query.filter_by(user_id=user_id, week_key=week_key).first()
    if entry:
        entry.score = max(entry.score, int(valid_distance))
    else:
        db.session.add(LeaderboardEntry(user_id=user_id, week_key=week_key, score=int(valid_distance)))
    # Global leaderboard is just saves.high_score, ordered — see leaderboard.py

    # Weekly challenge progress
    for challenge in WeeklyChallenge.query.filter_by(week_key=week_key).all():
        delta = 0
        if challenge.challenge_type == "distance":
            delta = int(valid_distance)
        elif challenge.challenge_type == "coins_collected":
            delta = valid_coins_earned
        if delta == 0:
            continue

        progress = UserChallengeProgress.query.filter_by(
            user_id=user_id, challenge_id=challenge.id
        ).first()
        if not progress:
            progress = UserChallengeProgress(user_id=user_id, challenge_id=challenge.id, current_value=0)
            db.session.add(progress)

        progress.current_value = min(progress.current_value + delta, challenge.target_value)
        progress.completed = progress.current_value >= challenge.target_value

    if flagged:
        # Log for review rather than auto-punish — false positives are possible
        print(f"[anti-cheat] flagged run user={user_id} claimed={distance}m/{coins_collected}c "
              f"in {duration_seconds:.1f}s")

    db.session.commit()

    return jsonify({
        "coins": save.coins,
        "highScore": save.high_score,
        "coinsEarned": valid_coins_earned,
        "flagged": flagged,
    })
