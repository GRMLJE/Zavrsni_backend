from flask import Blueprint, jsonify, request

from auth import create_token
from services import users_service

users_bp = Blueprint("users", __name__)


@users_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")

    if not first_name or not last_name or not email or not password:
        return jsonify({"error": "Sva polja su obavezna."}), 400

    try:
        user_id = users_service.register_user(first_name, last_name, email, password)
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

    return jsonify({"message": "Registracija uspješna.", "user_id": user_id}), 201


@users_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email i lozinka su obavezni."}), 400

    try:
        user = users_service.authenticate_user(email, password)
    except ValueError as e:
        return jsonify({"error": str(e)}), 401

    token = create_token(user["id"])
    return jsonify({"message": "Prijava uspješna.", "token": token, "user": user}), 200


@users_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = users_service.get_user(user_id)
    if not user:
        return jsonify({"error": "Korisnik nije pronađen."}), 404
    return jsonify(user), 200
