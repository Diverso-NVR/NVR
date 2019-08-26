import time
from datetime import datetime
from driveAPI import startstop
from calendarAPI.calendarSettings import getEvents
from threading import Thread, local

rooms = {}


def configDaemon(room: dict) -> None:
    id = room['id']
    rooms[id] = {}
    rooms[id]['event'] = {}
    rooms[id]['name'] = room['name']
    rooms[id]['chosenSound'] = room['chosenSound']
    rooms[id]['sources'] = room['sources']


def updateDaemon(room: dict) -> None:
    rooms[room['id']]['sources'] = room['sources']


def changedSound(room: dict) -> None:
    rooms[room['id']]['chosenSound'] = room['chosenSound']

def events() -> None:
    for room in rooms:
        try:
            e = getEvents(rooms[room]["name"])
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


def parseDate(date: str) -> str:
    """
    Parses date in YYYY-MM-DD hh-mm format
    """
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    hour = date[11:13]
    minute = date[14:16]
    return "{}-{}-{} {}:{}".format(year, month, day, hour, minute)


def record(id: int, room: dict, dur: int) -> None:
    calendarId = room['event']['organizer'].get(
        'email')
    eventId = room['event']['id']
    startstop.start(id, room['name'], room['chosenSound'], room['sources'])
    time.sleep(dur)
    startstop.stop(id, calendarId, eventId)


def runDaemon() -> None:
    started = []
    while True:
        events()
        current_time = datetime.now()
        for room in rooms:
            if rooms[room]['event'] == {}:
                continue
            start = parseDate(rooms[room]['event']['start'].get('dateTime'))
            end = parseDate(rooms[room]['event']['end'].get('dateTime'))
            if rooms[room]['event']['id'] not in started and start == datetime.strftime(current_time, "%Y-%m-%d %H:%M"):
                Thread(target=record, args=(
                    room, rooms[room], duration(end) - duration(start)), daemon=True).start()
                started.append(rooms[room]['event']['id'])
        time.sleep(1)
