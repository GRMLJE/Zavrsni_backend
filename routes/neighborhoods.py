from flask import Blueprint, jsonify, request

from db import get_db

neighborhoods_bp = Blueprint("neighborhoods", __name__)


@neighborhoods_bp.route("/neighborhoods", methods=["POST"])
def add_neighborhood():
    data = request.json or {}
    name = data.get("name")
    city_id = data.get("city_id")
    if not name or not city_id:
        return jsonify({"error": "Naziv i grad su obavezni."}), 400

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO neighborhoods (name, city_id) VALUES (%s, %s) RETURNING id;",
                (name, city_id),
            )
            neighborhood_id = cur.fetchone()[0]

    return jsonify({"id": neighborhood_id, "name": name, "city_id": city_id}), 201


@neighborhoods_bp.route("/neighborhoods", methods=["GET"])
def get_neighborhoods():
    city_id = request.args.get("city_id")
    with get_db() as conn:
        with conn.cursor() as cur:
            if city_id:
                cur.execute("SELECT id, name FROM neighborhoods WHERE city_id = %s;", (city_id,))
            else:
                cur.execute("SELECT id, name FROM neighborhoods;")
            rows = cur.fetchall()
    return jsonify([{"id": r[0], "name": r[1]} for r in rows])
