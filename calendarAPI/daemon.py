import time
from datetime import datetime
from driveapi import startstop
from calendarAPI.calendarSettings import getEvents, parseDate


def events():
    dates = []
    for room in ["P505", "P500", "C401"]:
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

class Daemon():
    def run(self):
        while True:
            dates = events()
            today = datetime.now()
            print(today)
            for i in range(len(dates)):
                if dates[i] == {}:
                    continue
                startt = parseDate(dates[i]['start'].get(
                    'dateTime', dates[i]['start'].get('date')))
                end = parseDate(dates[i]['end'].get(
                    'dateTime', dates[i]['end'].get('date')))
                if startt == datetime.strftime(today, "%Y-%m-%d %H:%M"):
                    startstop.start(str(i + 1))
                    time.sleep(duration(end) - duration(startt))
                    startstop.stop()
            time.sleep(1)


daemon = Daemon()
daemon.run()
