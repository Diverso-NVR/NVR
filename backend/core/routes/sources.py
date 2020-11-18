"""Api for interacting with sources"""

from flask import Blueprint, jsonify, request, g

from ..socketio import emit_event
from ..models import Room, Source
from ..decorators import auth_required, admin_or_editor_only

api = Blueprint("source_api", __name__)


@api.route("/sources/", methods=["GET"])
@auth_required
def get_sources(current_user):
    return jsonify([s.to_dict() for s in g.session.query(Source).all()]), 200


@api.route("/sources/<path:ip>", methods=["POST", "GET", "DELETE", "PUT"])
@auth_required
@admin_or_editor_only
def manage_source(current_user, ip):
    if request.method == "POST":
        data = request.get_json()
        room_name = data.get("room_name")
        if not room_name:
            return jsonify({"error": "room_name required"}), 400
        room = g.session.query(Room).filter_by(name=str(room_name)).first()
        if not room:
            return jsonify({"error": "No room found with provided room_name"}), 400

        data["room_id"] = room.id
        source = Source(ip=ip, **data)
        g.session.add(source)
        g.session.commit()

        emit_event(
            "edit_room", {"id": room.id, "sources": [s.to_dict() for s in room.sources]}
        )

        return jsonify({"message": "Added"}), 201

    for source in g.session.query(Source).all():
        if ip in source.ip:
            break
    else:
        return jsonify({"error": "No source with provided ip found"}), 400

    room_id = source.room_id

    if request.method == "GET":
        return jsonify(source.to_dict()), 200

    if request.method == "DELETE":
        g.session.delete(source)
        g.session.commit()

        emit_event(
            "edit_room",
            {
                "id": room_id,
                "sources": [
                    s.to_dict() for s in g.session.query(Room).get(room_id).sources
                ],
            },
        )

        return jsonify({"message": "Deleted"}), 200

    if request.method == "PUT":
        s = request.get_json()
        source_dict = source.to_dict()
        updated_source_dict = {**source_dict, **s}

        g.session.delete(source)

        source = Source(**updated_source_dict)
        g.session.add(source)
        g.session.commit()

        emit_event(
            "edit_room",
            {
                "id": room_id,
                "sources": [
                    s.to_dict() for s in g.session.query(Room).get(room_id).sources
                ],
            },
        )

        return jsonify({"message": "Updated"}), 200
