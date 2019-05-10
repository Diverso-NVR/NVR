import time
from datetime import datetime
from driveapi import startstop
from calendarAPI.calendarSettings import getEvents, parseDate
from threading import Thread
import json
import random


with open("app/data.json", 'r') as f:
    data = json.loads(f.read())

rooms = {}

for building in data:
    rooms[building] = []
    for room in data[building]:
        rooms[building].append(
            {"id": room['id'], "room": room['auditorium'], "event": {}})


def events():
    for building in rooms:
        for room in rooms[building]:
            try:
                e = getEvents(building, room["room"])
                room["event"] = e[0]
            except Exception:
                room["event"] = {}


def duration(date):
    _time = date.split()[1]
    hour = _time.split(":")[0]
    minute = _time.split(":")[1]

    hour = int(hour) * 3600
    minute = int(minute) * 60

    return hour + minute


def record(num, building, startt, end):
    startstop.start(str(num), "cam", building)
    time.sleep(duration(end) - duration(startt))
    startstop.stop(str(num), building)
    time.sleep(random.randint(0, 10))


def run():
    started = []
    while True:
        events()
        current_time = datetime.now()
        for building in rooms:
            for room in rooms[building]:
                if room['event'] == {}:
                    continue
                startt = parseDate(room['event']['start'].get(
                    'dateTime', room['event']['start'].get('date')))
                end = parseDate(room['event']['end'].get(
                    'dateTime', room['event']['end'].get('date')))
                if room['event'] not in started and startt == datetime.strftime(current_time, "%Y-%m-%d %H:%M"):
                    proc = Thread(target=record, args=(
                        room['id'], building, startt, end), daemon=True)
                    proc.start()
                    started.append(room['event'])
        time.sleep(1)


if __name__ == '__main__':
    run()
