import time
from datetime import datetime
from driveAPI import startstop
from calendarAPI.calendarSettings import get_events
from threading import Thread, local
import requests
import os

API_URL = os.environ.get('NVR_API_URL')
rooms = {}
started = []


def config_daemon(room: dict) -> None:
    id = room['id']
    rooms[id] = {}
    rooms[id]['event'] = {}
    rooms[id]['name'] = room['name']
    rooms[id]['chosenSound'] = room['chosenSound']
    rooms[id]['sources'] = room['sources']


def update_daemon(room: dict) -> None:
    rooms[room['id']]['sources'] = room['sources']


def changed_sound(room: dict) -> None:
    rooms[room['id']]['chosenSound'] = room['chosenSound']


def events() -> None:
    for room in rooms:
        try:
            e = get_events(rooms[room]["name"])
            rooms[room]["event"] = e
        except Exception:
            rooms[room]["event"] = {}


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


def record(room_id: int, room: dict, dur: int) -> None:
    calendar_id = room['event']['organizer'].get(
        'email')
    event_id = room['event']['id']
    startstop.start(room_id, room['name'],
                    room['chosenSound'], room['sources'])
    requests.post(url=f'{API_URL}/daemonStartRec', json={'id': room_id})
    time.sleep(dur)
    started.remove(event_id)
    startstop.stop(room_id, calendar_id, event_id)
    requests.post(url=f'{API_URL}/daemonStopRec', json={'id': room_id})


def run_daemon() -> None:
    while True:
        events()
        current_time = datetime.now()
        for room in rooms:
            if rooms[room]['event'] == {}:
                continue
            start = parse_date(rooms[room]['event']['start'].get('dateTime'))
            end = parse_date(rooms[room]['event']['end'].get('dateTime'))
            if rooms[room]['event']['id'] not in started and start == datetime.strftime(current_time, "%Y-%m-%d %H:%M"):
                Thread(target=record, args=(
                    room, rooms[room], duration(end) - duration(start))).start()
                started.append(rooms[room]['event']['id'])
        time.sleep(1)
