import time
from datetime import datetime
from driveapi import startstop
from calendarAPI.calendarSettings import getEvents, parseDate


dates = getEvents("513MIEM")

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
            today = datetime.now()
            print(today)
            for event in dates:
                startt = parseDate(event['start'].get(
                    'dateTime', event['start'].get('date')))
                end = parseDate(event['end'].get(
                    'dateTime', event['end'].get('date')))
                if startt == datetime.strftime(today, "%Y-%m-%d %H:%M"):
                    startstop.start("4")
                    time.sleep(duration(end) - duration(startt))
                    startstop.stop()
                    return
            time.sleep(1)


daemon = Daemon()
daemon.run()
