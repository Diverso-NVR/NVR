import time
from datetime import datetime
from driveAPI.startstop import start, stop
from calendarAPI.api import getEvents, parseDate


dates = getEvents("513MIEM")
for event in dates:
    start = parseDate(event['start'].get(
        'dateTime', event['start'].get('date')))
    end = parseDate(event['end'].get(
        'dateTime', event['end'].get('date')))
    print(start, end, event['summary'])


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
                    start("4")
                elif end == datetime.strftime(today, "%Y-%m-%d %H:%M"):
                    stop()
            time.sleep()


daemon = Daemon()
daemon.run()
