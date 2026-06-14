from flask import Blueprint, g, jsonify, request

from auth import require_auth
from services import events_service

events_bp = Blueprint("events", __name__)


@events_bp.route("/events", methods=["POST"])
@require_auth
def add_event():
    data = request.json or {}
    title = data.get("title")
    description = data.get("description")
    event_date = data.get("event_date")
    category_id = data.get("category_id")
    neighborhood_id = data.get("neighborhood_id")
    address = data.get("address")

    if not title or not event_date or not category_id or not neighborhood_id:
        return jsonify({"error": "Naslov, datum, kategorija i kvart su obavezni."}), 400

    try:
        event_id = events_service.create_event(
            title, description, event_date, category_id, neighborhood_id,
            g.user_id, address
        )
    except LookupError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify({"message": "Event uspješno dodan.", "id": event_id}), 201


@events_bp.route("/events", methods=["GET"])
def get_events():
    events = events_service.get_events(
        viewer_user_id=request.args.get("viewer_user_id"),
        city_id=request.args.get("city_id"),
        neighborhood_id=request.args.get("neighborhood_id"),
        category_id=request.args.get("category_id"),
        user_id=request.args.get("user_id"),
    )
    return jsonify(events)


@events_bp.route("/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    event = events_service.get_event(
        event_id,
        viewer_user_id=request.args.get("viewer_user_id"),
    )
    if not event:
        return jsonify({"error": "Event nije pronađen."}), 404
    return jsonify(event)


@events_bp.route("/events/<int:event_id>/join", methods=["POST"])
@require_auth
def join_event(event_id):
    try:
        events_service.join_event(event_id, g.user_id)
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    return jsonify({"message": "Uspješno si se prijavio na event."}), 200


@events_bp.route("/events/<int:event_id>/join", methods=["DELETE"])
@require_auth
def leave_event(event_id):
    try:
        events_service.leave_event(event_id, g.user_id)
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify({"message": "Odustao si od dolaska na event."}), 200


@events_bp.route("/events/<int:event_id>", methods=["DELETE"])
@require_auth
def delete_event(event_id):
    try:
        events_service.delete_event(event_id, g.user_id)
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    return jsonify({"message": "Event je obrisan."}), 200
