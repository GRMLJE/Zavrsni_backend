from flask import Blueprint, jsonify, request

from db import get_db

cities_bp = Blueprint("cities", __name__)


@cities_bp.route("/cities", methods=["POST"])
def add_city():
    data = request.json or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "Naziv grada je obavezan."}), 400

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO cities (name) VALUES (%s) RETURNING id;", (name,))
            city_id = cur.fetchone()[0]

    return jsonify({"id": city_id, "name": name}), 201


@cities_bp.route("/cities", methods=["GET"])
def get_cities():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM cities;")
            rows = cur.fetchall()
    return jsonify([{"id": r[0], "name": r[1]} for r in rows])
