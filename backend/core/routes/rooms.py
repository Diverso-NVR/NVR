"""Api for interacting with rooms"""


from threading import Thread

from flask import Blueprint, jsonify, request, g

from ..socketio import emit_room
from ..apis.calendar_api import create_calendar, delete_calendar
from ..apis.drive_api import create_folder
from ..apis.ruz_api import get_room_ruzid
from ..models import Session, Room
from ..decorators import json_data_required, auth_required, admin_or_editor_only


api = Blueprint("rooms_api", __name__)


@api.route("/rooms", methods=["POST"])
@auth_required
@admin_or_editor_only
@json_data_required
def create_room(current_user):
    data = request.get_json()
    room_name = data.get("name")
    if not room_name:
        return jsonify({"error": "Room name required"}), 400

    room = Room(name=room_name, organization_id=current_user.organization_id)
    room.sources = []

    emit_room("add_room", {"room": room.to_dict()}, current_user.organization_id)

    Thread(target=config_room, args=(room.id)).start()
    g.session.add(room)
    g.session.commit()

    return jsonify({"message": f"Started creating '{room_name}'"}), 204


def config_room(room_id):
    session = Session()

    room = session.query(Room).filter_by(name=room_id).first()
    room.drive = create_folder(room.name)
    room.calendar = create_calendar(room.name)
    room.ruz_id = get_room_ruzid(room.name)

    session.commit()
    session.close()


@api.route("/rooms", methods=["GET"])
@auth_required
def get_rooms(current_user):
    rooms = g.session.query(Room).filter(
        Room.organization_id == current_user.organization_id
    )
    rooms = sorted(rooms, key=lambda room: len(room.sources), reverse=True)

    return (
        jsonify([room.to_dict() for room in rooms]),
        200,
    )


@api.route("/rooms/<room_id>", methods=["GET"])
@auth_required
def get_room(current_user, room_id):
    room = g.session.query(Room).get(room_id)
    if not room or room.organization_id != current_user.organization_id:
        return jsonify({"error": "No room found with given id"}), 400

    return jsonify(room.to_dict()), 200


@api.route("/rooms/<room_id>", methods=["DELETE"])
@auth_required
@admin_or_editor_only
def delete_room(current_user, room_id):
    room = g.session.query(Room).get(room_id)
    if not room or room.organization_id != current_user.organization_id:
        return jsonify({"error": "No room found"}), 400

    Thread(target=delete_calendar, args=(room.calendar,)).start()

    g.session.delete(room)
    g.session.commit()

    emit_room(
        "delete_room", {"id": room.id, "name": room.name}, current_user.organization_id
    )

    return jsonify({"message": "Room deleted"}), 200
