"""Api for interacting with sources"""


from pathlib import Path
from flask import Blueprint, jsonify, request
from .socketio import emit_event
from .models import db, Room, Source, User
from .decorators import auth_required, admin_or_editor_only

source_api = Blueprint('source_api', __name__)

@source_api.route("/sources/", methods=['GET'])
@auth_required
def get_sources(current_user):
    return jsonify([s.to_dict() for s in Source.query.all()]), 200


@source_api.route("/sources/<path:ip>", methods=['POST', 'GET', 'DELETE', 'PUT'])
@auth_required
@admin_or_editor_only
def manage_source(current_user, ip):
    if request.method == 'POST':
        data = request.get_json()
        room_name = data.get('room_name')
        if not room_name:
            return jsonify({"error": "room_name required"}), 400
        room = Room.query.filter_by(name=str(room_name)).first()
        if not room:
            return jsonify({"error": "No room found with provided room_name"}), 400

        data['room_id'] = room.id
        source = Source(ip=ip, **data)
        db.session.add(source)
        db.session.commit()

        emit_event('edit_room', {'id': room.id, 'sources': [
            s.to_dict() for s in room.sources]})

        return jsonify({'message': 'Added'}), 201

    for source in Source.query.all():
        if ip in source.ip:
            break
    else:
        return jsonify({'error': 'No source with provided ip found'}), 400

    room_id = source.room_id

    if request.method == 'GET':
        return jsonify(source.to_dict()), 200

    if request.method == 'DELETE':
        db.session.delete(source)
        db.session.commit()

        emit_event('edit_room', {'id': room_id, 'sources': [
            s.to_dict() for s in Room.query.get(room_id).sources]})

        return jsonify({'message': 'Deleted'}), 200

    if request.method == 'PUT':
        s = request.get_json()
        source_dict = source.to_dict()
        updated_source_dict = {**source_dict, **s}

        db.session.delete(source)

        source = Source(**updated_source_dict)
        db.session.add(source)
        db.session.commit()

        emit_event('edit_room', {'id': room_id, 'sources': [
            s.to_dict() for s in Room.query.get(room_id).sources]})

        return jsonify({'message': 'Updated'}), 200
