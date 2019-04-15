import time
from datetime import datetime
from driveapi import startstop
from calendarAPI.calendarSettings import getEvents, parseDate, rooms
import threading


def events():
    dates = []
    for room in rooms:
        try:
            i = getEvents(room)
            dates.append(i[0])
        except IndexError:
            dates.append({})
    return dates


def duration(date):
    _time = date.split()[1]
    hour = _time.split(":")[0]
    minute = _time.split(":")[1]

    hour = int(hour) * 3600
    minute = int(minute) * 60

    return hour + minute


def record(num, startt, end):
    startstop.start(str(num), "cam")
    time.sleep(duration(end) - duration(startt))
    startstop.stop(str(num))


def run():
    dates = events()
    while True:
        today = datetime.now()
        for i in range(len(dates)):
            if dates[i] == {}:
                continue
            startt = parseDate(dates[i]['start'].get(
                'dateTime', dates[i]['start'].get('date')))
            end = parseDate(dates[i]['end'].get(
                'dateTime', dates[i]['end'].get('date')))
            if startt == datetime.strftime(today, "%Y-%m-%d %H:%M"):
                t = threading.Thread(target=record, args=(
                    i+1, startt, end), daemon=True)
                t.start()
                dates = events()
        time.sleep(1)


if __name__ == '__main__':
    run()
