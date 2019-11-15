import time
from datetime import datetime
from calendarAPI.calendarSettings import get_events
from threading import Thread, local
import requests
from API.models import nvr_db_context, Room
import os

started = []

NVR_API_URL = os.environ.get('NVR_API_URL')
NVR_API_KEY = os.environ.get('NVR_API_KEY')

nvr_querystring = {"key": NVR_API_KEY}


def events(app) -> None:
    for room in rooms:
        try:
            e = get_events(app, room['id'])
            room["event"] = e
        except Exception as e:
            room["event"] = {}


def duration(date: str) -> int:
    _time = date.split()[1]
    hour = _time.split(":")[0]
    minute = _time.split(":")[1]

    hour = int(hour) * 3600
    minute = int(minute) * 60

    return hour + minute


def parse_date(date: str) -> str:
    """
    Parses date in YYYY-MM-DD hh-mm format
    """
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    hour = date[11:13]
    minute = date[14:16]
    return "{}-{}-{} {}:{}".format(year, month, day, hour, minute)


@nvr_db_context
def record(app, room: dict, dur: int) -> None:
    event_id = room['event']['id']

    room = Room.query.get(room['id'])
    res = requests.post(f'{NVR_API_URL}/start-record',
                        json={
                            'id': room.id
                        },
                        headers=nvr_querystring
                        )
    time.sleep(dur)
    started.remove(event_id)
    requests.post(f'{NVR_API_URL}/stop-record',
                  json={
                      'id': room.id,
                      'calendar_id': room.calendar,
                      'event_id': event_id
                  },
                  headers=nvr_querystring
                  )


def run_daemon(app) -> None:
    with app.app_context():
        global rooms
        rooms = [
            {'id': room.id} for room in Room.query.all()
        ]

    while True:
        events(app)
        current_time = datetime.now()
        for room in rooms:
            if room['event'] == {}:
                continue
            start = parse_date(room['event']['start'].get('dateTime'))
            end = parse_date(room['event']['end'].get('dateTime'))
            if room['event']['id'] not in started and start == datetime.strftime(current_time, "%Y-%m-%d %H:%M"):
                Thread(target=record,
                       args=(app, app, room, duration(end) - duration(start))).start()
                started.append(room['event']['id'])
        time.sleep(10)
