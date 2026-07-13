from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db
from ..models import User, Save

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "username, email, and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    exists = User.query.filter((User.email == email) | (User.username == username)).first()
    if exists:
        return jsonify({"error": "Username or email already taken"}), 409

    user = User(username=username, email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.flush()  # assigns user.id before we reference it below

    db.session.add(Save(user_id=user.id))
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "token": token,
        "user": {"id": str(user.id), "username": user.username, "email": user.email},
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    # deliberately vague error — don't reveal whether the email exists
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    user.last_login_at = datetime.utcnow()
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "token": token,
        "user": {"id": str(user.id), "username": user.username, "email": user.email},
    })
