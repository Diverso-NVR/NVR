"""Api for interacting with google"""


from threading import Thread
from pathlib import Path

from flask import Blueprint, jsonify, request, current_app, g

from ..apis.calendar_api import create_calendar, create_event_
from ..apis.drive_api import create_folder, get_folders_by_name, upload
from ..models import Session, Room, Source, User, Record
from ..decorators import json_data_required, auth_required, admin_or_editor_only


api = Blueprint('google_api', __name__)

VIDS_PATH = str(Path.home()) + '/vids/'


@api.route('/gcalendar-event/<room_name>', methods=['POST'])
@auth_required
@admin_or_editor_only
@json_data_required
def create_calendar_event(current_user, room_name):
    data = request.get_json()

    start_time = data.get('start_time')

    if not start_time:
        return jsonify({"error": "Start time required"}), 400

    end_time = data.get('end_time')
    summary = data.get('summary', '')

    try:
        event_link = create_event_(
            room_name=str(room_name), start_time=start_time,
            end_time=end_time, summary=summary)
    except ValueError:
        return jsonify({'error': 'Format error: date format should be YYYY-MM-DDTHH:mm'}), 400
    except NameError:
        return jsonify({'error': f"No room found with name '{room_name}'"}), 400

    return jsonify({'message': f"Successfully created event: {event_link}"}), 201


@api.route('/gdrive-upload/<room_name>', methods=['POST'])
@auth_required
@admin_or_editor_only
def upload_video_to_drive(current_user, room_name):
    if not request.files:
        return {"error": "No file provided"}, 400

    room = g.session.query(Room).filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": f"Room '{room_name}' not found"}), 400

    file = request.files['file']
    file_name = file.filename
    file.save(VIDS_PATH + file_name)

    try:
        date = file_name.split('_')[0]
        time = file_name.split('_')[1].split('.')[0]
    except:
        return {"error": "Incorrect file name"}, 400

    folder = ''

    # TODO можно наверно через mimetype в функции но мне так лень и времени нет хочу сдохнуть
    date_folders = get_folders_by_name(date)
    time_folders = get_folders_by_name(time)
    for folder_id, folder_parent_id in date_folders.items():
        if folder_parent_id == room.drive.split('/')[-1]:
            for f_id, fp_id in time_folders.items():
                if fp_id == folder_id:
                    folder = f_id
    if not folder:
        folder = room.drive.split('/')[-1]

    Thread(target=upload, args=(VIDS_PATH + file_name,
                                folder)).start()

    return jsonify({"message": "Upload to disk started"}), 200


@api.route('/gconfigure/<string:room_name>', methods=['POST'])
@auth_required
@admin_or_editor_only
def create_drive_and_calendar(current_user, room_name):
    drive = create_folder(room_name)
    calendar = create_calendar(room_name)
    return jsonify({"drive": drive, "calendar": calendar}), 201
