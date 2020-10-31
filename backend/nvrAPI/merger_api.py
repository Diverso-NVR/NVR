merger_api = Blueprint('merger_api', __name__)

@api.route('/calendar-notifications/', methods=["POST"])
def gcalendar_webhook():
    calendar_id = request.headers['X-Goog-Resource-Uri'].split('/')[6]
    calendar_id = calendar_id.replace('%40', '@')
    events = get_events(calendar_id)

    room = Room.query.filter_by(calendar=calendar_id).first()
    records = Record.query.filter(
        Record.room_name == room.name,
        Record.event_id != None).all()
    calendar_events = set(events.keys())
    db_events = {record.event_id for record in records}

    new_events = calendar_events - db_events
    deleted_events = db_events - calendar_events
    events_to_check = calendar_events & db_events

    for event_id in deleted_events:
        record = Record.query.filter_by(event_id=event_id).first()
        if record.done or record.processing:
            continue

        db.session.delete(record)

    for event_id in new_events:
        event = events[event_id]
        start_date = event['start']['dateTime'].split('T')[0]
        end_date = event['end']['dateTime'].split('T')[0]

        if start_date != end_date:
            continue

        new_record = Record()
        new_record.update_from_calendar(**event, room_name=room.name)
        db.session.add(new_record)

    for event_id in events_to_check:
        event = events[event_id]
        if date.today().isoformat() != event['updated'].split('T')[0]:
            continue

        record = Record.query.filter_by(event_id=event_id).first()
        if record.done or record.processing:
            continue

        record.update_from_calendar(**event, room_name=room.name)

    db.session.commit()
    db.session.close()

    return jsonify({"message": "Room calendar events patched"}), 200


@api.route('/montage-event/<room_name>', methods=["POST"])
@auth_required
@json_data_required
def create_montage_event(current_user, room_name):
    json = request.get_json()

    event_name = json.get("event_name")
    date = json.get("date")
    start_time = json.get("start_time")
    end_time = json.get("end_time")
    user_email = json.get("user_email", current_user.email)

    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given room_name"}), 400

    if not date:
        return jsonify({"error": "'date' required"}), 400
    if not start_time:
        return jsonify({"error": "'start_time' required"}), 400
    if not end_time:
        return jsonify({"error": "'end_time' required"}), 400

    date_time_start = datetime.strptime(
        f'{date} {start_time}', '%Y-%m-%d %H:%M')
    date_time_end = datetime.strptime(
        f'{date} {end_time}', '%Y-%m-%d %H:%M')

    start_timestamp = int(date_time_start.timestamp())
    end_timestamp = int(date_time_end.timestamp())

    if start_timestamp >= end_timestamp:
        return jsonify({"error": "Неверный промежуток времени"}), 400

    record = Record(event_name=event_name, room_name=room.name, date=date,
                    start_time=start_time, end_time=end_time, user_email=user_email)

    db.session.add(record)
    db.session.commit()
    db.session.close()

    return jsonify({'message': f"Merge event '{event_name}' added to queue"}), 201


@api.route('/tracking/<room_name>', methods=['POST'])
@auth_required
@admin_or_editor_only
@json_data_required
def tracking_manage(current_user, room_name):
    post_data = request.get_json()

    command = post_data.get('command')

    if not command:
        return jsonify({"error": "Command required"}), 400
    if command not in ['start', 'stop', 'status']:
        return jsonify({'error': "Incorrect command"}), 400

    if command == 'status':
        res = requests.get(f'{TRACKING_URL}/status', timeout=5)
        return jsonify(res.json()), 200

    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given room_name"}), 400

    if not room.tracking_source:
        return jsonify({"error": "No tracking cam selected in requested room"}), 400

    command = command.lower()
    try:
        if command == 'start':
            res = requests.post(f'{TRACKING_URL}/track', json={
                'ip': room.tracking_source}, timeout=5)
        else:
            res = requests.delete(f'{TRACKING_URL}/track')

        room.tracking_state = True if command == 'start' else False
        db.session.commit()

        emit_event('tracking_state_change', {
            'id': room.id, 'tracking_state': room.tracking_state, 'room_name': room.name})

        return jsonify(res.json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/streaming-start/<room_name>', methods=['POST'])
@auth_required
@json_data_required
def streaming_start(current_user, room_name):
    data = request.get_json()

    sound_ip = data.get('sound_ip')
    camera_ip = data.get('camera_ip')
    title = data.get('title')

    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": f"Room {room_name} not found"}), 404
    if room.stream_url:
        return jsonify({"error": f"Stream is already running on {room.stream_url}"}), 409

    if not sound_ip:
        return jsonify({"error": "Sound source ip not provided"}), 400
    if not camera_ip:
        return jsonify({"error": "Camera ip not provided"}), 400

    sound_source = Source.query.filter_by(ip=sound_ip).first()
    camera_source = Source.query.filter_by(ip=camera_ip).first()

    try:
        response = requests.post(f"{STREAMING_URL}/streams/{room_name}", json={
            "camera_ip": camera_source.rtsp,
            "sound_ip": sound_source.rtsp,
            'title': title
        }, headers={'X-API-KEY': STREAMING_API_KEY})
        url = response.json()['url']
        room.stream_url = url
        db.session.commit()
    except:
        return jsonify({"error": "Unable to start stream"}), 500

    return jsonify({"message": "Streaming started", 'url': url}), 200


@api.route('/streaming-stop/<room_name>', methods=['POST'])
@auth_required
@json_data_required
def streaming_stop(current_user, room_name):
    data = request.get_json()

    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": f"Room {room_name} not found"}), 404
    if not room.stream_url:
        return jsonify({"error": f"Stream is not running"}), 400

    try:
        response = requests.delete(
            f'{STREAMING_URL}/streams/{room_name}',
            headers={'X-API-KEY': STREAMING_API_KEY})
    except:
        return jsonify({"error": "Unable to stop stream"}), 500
    finally:
        room.stream_url = None
        db.session.commit()

    return jsonify({"message": "Streaming stopped"}), 200


@api.route('/auto-control/<room_name>', methods=['POST'])
@auth_required
@admin_or_editor_only
@json_data_required
def auto_control(current_user, room_name):
    data = request.get_json()

    auto_control = data.get('auto_control')

    if auto_control is None:
        return jsonify({"error": "Boolean value not provided"}), 400

    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": f"Room {room_name} not found"}), 404

    room.auto_control = auto_control
    db.session.commit()

    emit_event('auto_control_change', {
        'id': room.id, 'auto_control': room.auto_control, 'room_name': room.name})

    return jsonify({"message": f"Automatic control within room {room_name} \
                    has been set to {auto_control}"}), 200


@api.route('/records/<user_email>', methods=['GET'])
@auth_required
def get_urls(current_user, user_email):
    records = Record.query.filter(
        Record.user_email == user_email).all()
    return jsonify([rec.to_dict() for rec in records]), 200