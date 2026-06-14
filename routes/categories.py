from flask import Blueprint, jsonify, request

from db import get_db

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/categories", methods=["POST"])
def add_category():
    data = request.json or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "Naziv kategorije je obavezan."}), 400

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO categories (name) VALUES (%s) RETURNING id;", (name,))
            category_id = cur.fetchone()[0]

    return jsonify({"id": category_id, "name": name}), 201


@categories_bp.route("/categories", methods=["GET"])
def get_categories():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM categories;")
            rows = cur.fetchall()
    return jsonify([{"id": r[0], "name": r[1]} for r in rows])
