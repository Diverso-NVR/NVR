import time
from datetime import datetime
import sys
import driveAPI.startstop
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
                    driveAPI.startstop.start("4")
                    time.sleep(30)
                    driveAPI.startstop.stop()
                    sys.exit()
            time.sleep(1)


daemon = Daemon()
daemon.run()
