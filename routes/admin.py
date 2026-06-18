from flask import Blueprint, jsonify, request

from auth import require_admin
from services import events_service

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/events", methods=["GET"])
@require_admin
def list_events():
    status = request.args.get("status", "pending")
    events = events_service.get_events_by_status(status)
    return jsonify(events)


@admin_bp.route("/events/<int:event_id>/approve", methods=["POST"])
@require_admin
def approve_event(event_id):
    try:
        events_service.set_event_status(event_id, "approved")
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify({"message": "Event odobren."}), 200


@admin_bp.route("/events/<int:event_id>/reject", methods=["POST"])
@require_admin
def reject_event(event_id):
    try:
        events_service.set_event_status(event_id, "rejected")
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify({"message": "Event odbijen."}), 200


@admin_bp.route("/events/<int:event_id>", methods=["DELETE"])
@require_admin
def admin_delete_event(event_id):
    try:
        events_service.admin_delete_event(event_id)
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify({"message": "Event obrisan."}), 200
