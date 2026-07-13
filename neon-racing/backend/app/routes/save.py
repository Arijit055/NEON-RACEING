from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import Save

save_bp = Blueprint("save", __name__)


@save_bp.route("/", methods=["GET"])
@jwt_required()
def get_save():
    user_id = get_jwt_identity()
    save = Save.query.get(user_id)
    if not save:
        return jsonify({"error": "No save found for this user"}), 404
    return jsonify(save.to_dict())


@save_bp.route("/", methods=["POST"])
@jwt_required()
def update_save():
    """Updates non-currency save state: car unlocks, selected car, upgrade
    levels, shield ownership. coins and highScore are intentionally NOT
    accepted here — those only ever move through /api/run/submit, where
    they're validated against server-tracked play time (see anti_cheat.py).
    Accepting them here would let a client just POST {"coins": 999999}."""
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    save = Save.query.get(user_id)
    if not save:
        return jsonify({"error": "No save found for this user"}), 404

    if "unlockedCars" in data:
        save.unlocked_cars = data["unlockedCars"]
    if "selectedCar" in data:
        save.selected_car = data["selectedCar"]
    if "engineLevel" in data:
        save.engine_level = data["engineLevel"]
    if "magnetLevel" in data:
        save.magnet_level = data["magnetLevel"]
    if "hasShield" in data:
        save.has_shield = data["hasShield"]

    db.session.commit()
    return jsonify(save.to_dict())


# Car unlock cost matches the frontend's `(i+1)*30` formula in index.html —
# keep these in sync if the car roster or pricing changes there.
def _car_cost(car_id):
    return (car_id + 1) * 30


@save_bp.route("/purchase", methods=["POST"])
@jwt_required()
def purchase():
    """Server-authoritative coin spending. The client tells us *what* it wants
    to buy, never how many coins to deduct — we look up the cost and the
    player's current coin balance ourselves. This is the only way coins
    should ever decrease; it keeps a client from just POSTing an inflated
    coin total (see the note in update_save above)."""
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    action = data.get("action")

    save = Save.query.filter_by(user_id=user_id).with_for_update().first()
    if not save:
        return jsonify({"error": "No save found for this user"}), 404

    if action == "unlockCar":
        car_id = data.get("carId")
        if not isinstance(car_id, int) or car_id < 0:
            return jsonify({"error": "Invalid carId"}), 400
        if car_id in save.unlocked_cars:
            return jsonify({"error": "Car already unlocked"}), 409
        cost = _car_cost(car_id)
        if save.coins < cost:
            return jsonify({"error": "Not enough coins"}), 400
        save.coins -= cost
        save.unlocked_cars = [*save.unlocked_cars, car_id]

    elif action == "upgradeEngine":
        cost = save.engine_level * 50
        if save.coins < cost:
            return jsonify({"error": "Not enough coins"}), 400
        save.coins -= cost
        save.engine_level += 1

    elif action == "upgradeMagnet":
        cost = save.magnet_level * 150
        if save.coins < cost:
            return jsonify({"error": "Not enough coins"}), 400
        save.coins -= cost
        save.magnet_level += 1

    elif action == "buyShield":
        if save.has_shield:
            return jsonify({"error": "Shield already active"}), 409
        cost = 100
        if save.coins < cost:
            return jsonify({"error": "Not enough coins"}), 400
        save.coins -= cost
        save.has_shield = True

    else:
        return jsonify({"error": "Unknown action"}), 400

    db.session.commit()
    return jsonify(save.to_dict())

