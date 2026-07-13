from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import WeeklyChallenge, UserChallengeProgress, Save
from ..utils import get_week_key

challenges_bp = Blueprint("challenges", __name__)


@challenges_bp.route("/", methods=["GET"])
@jwt_required()
def get_active_challenges():
    user_id = get_jwt_identity()
    week_key = get_week_key()
    challenges = WeeklyChallenge.query.filter_by(week_key=week_key).all()

    progress_by_id = {
        p.challenge_id: p for p in UserChallengeProgress.query.filter_by(user_id=user_id).all()
    }

    result = []
    for c in challenges:
        p = progress_by_id.get(c.id)
        result.append({
            "id": c.id,
            "type": c.challenge_type,
            "targetValue": c.target_value,
            "rewardCoins": c.reward_coins,
            "description": c.description,
            "currentValue": p.current_value if p else 0,
            "completed": p.completed if p else False,
            "rewardClaimed": p.reward_claimed if p else False,
        })
    return jsonify(result)


@challenges_bp.route("/<int:challenge_id>/claim", methods=["POST"])
@jwt_required()
def claim_reward(challenge_id):
    user_id = get_jwt_identity()
    progress = UserChallengeProgress.query.filter_by(
        user_id=user_id, challenge_id=challenge_id
    ).with_for_update().first()

    if not progress or not progress.completed:
        return jsonify({"error": "Challenge not completed yet"}), 400
    if progress.reward_claimed:
        return jsonify({"error": "Reward already claimed"}), 409

    challenge = WeeklyChallenge.query.get(challenge_id)
    save = Save.query.get(user_id)

    save.coins += challenge.reward_coins
    progress.reward_claimed = True
    db.session.commit()

    return jsonify({"rewardCoins": challenge.reward_coins, "newCoinTotal": save.coins})
