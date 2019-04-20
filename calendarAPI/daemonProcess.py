import time
from datetime import datetime
from driveapi import startstop
from calendarAPI.calendarSettings import getEvents, parseDate
import threading
import json


with open("app/data.json", 'r') as f:
    data = json.loads(f.read())

rooms = {}

for building in data:
    rooms[building] = []
    for room in data[building]:
        rooms[building].append({"room": room['auditorium'], "event": {}})


def events():
    for building in rooms:
        for room in rooms[building]:
            try:
                i = getEvents(room["room"])
                room["event"] = i[0]
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


def run():
    while True:
        events()
        today = datetime.now()
        for building in rooms:
            for i in range(len(rooms[building])):
                if rooms[building][i]['event'] == {}:
                    continue
                startt = parseDate(rooms[building][i]['event']['start'].get(
                    'dateTime', rooms[building][i]['event']['start'].get('date')))
                end = parseDate(rooms[building][i]['event']['end'].get(
                    'dateTime', rooms[building][i]['event']['end'].get('date')))
                if startt == datetime.strftime(today, "%Y-%m-%d %H:%M"):
                    t = threading.Thread(target=record, args=(
                        i+1, building, startt, end), daemon=True)
                    t.start()
            time.sleep(1)


if __name__ == '__main__':
    run()
