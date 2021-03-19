"""Api for interacting with merging"""


from datetime import datetime

from flask import Blueprint, jsonify, request, g

from ..socketio import emit_room
from ..models import Room, Record, User, UserRecord
from ..decorators import json_data_required, auth_required, admin_or_editor_only


api = Blueprint("merger_api", __name__)


@api.route("/montage-event/<room_id>", methods=["POST"])
@auth_required
@json_data_required
def create_montage_event(current_user, room_id):
    json = request.get_json()

    event_name = json.get("event_name")
    date = json.get("date")
    start_time = json.get("start_time")
    end_time = json.get("end_time")
    user_email = json.get("user_email", current_user.email)

    room = g.session.query(Room).get(room_id)
    if not room:
        return jsonify({"error": "No room found"}), 400

    user = g.session.query(User).filter_by(email=str(user_email)).first()
    if not user:
        return jsonify({"error": "No user found with given user_email"}), 400

    if not date:
        return jsonify({"error": "'date' required"}), 400
    if not start_time:
        return jsonify({"error": "'start_time' required"}), 400
    if not end_time:
        return jsonify({"error": "'end_time' required"}), 400

    date_time_start = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
    date_time_end = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")

    start_timestamp = int(date_time_start.timestamp())
    end_timestamp = int(date_time_end.timestamp())

    if start_timestamp >= end_timestamp:
        return jsonify({"error": "Неверный промежуток времени"}), 400

    record = Record(
        event_name=event_name,
        date=date,
        start_time=start_time,
        end_time=end_time,
    )
    record.room = room
    g.session.add(record)
    g.session.commit()

    user_record = UserRecord(user_id=user.id, record_id=record.id)
    g.session.add(user_record)
    g.session.commit()

    return jsonify({"message": f"Merge event '{event_name}' added to queue"}), 201


@api.route("/auto-control/<room_id>", methods=["POST"])
@auth_required
@admin_or_editor_only
@json_data_required
def auto_control(current_user, room_id):
    data = request.get_json()

    auto_control = data.get("auto_control")
    if auto_control is None:
        return jsonify({"error": "Boolean value not provided"}), 400

    room = g.session.query(Room).get(room_id)
    if not room:
        return jsonify({"error": "Room not found"}), 404

    room.auto_control = auto_control
    g.session.commit()

    emit_room(
        "auto_control_change",
        {"id": room.id, "auto_control": room.auto_control, "room_name": room.name},
        current_user.organization_id,
    )

    return (
        jsonify(
            {
                "message": f"Automatic control within room {room.name} \
                    has been set to {auto_control}"
            }
        ),
        200,
    )
