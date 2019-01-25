import time
from datetime import datetime
from driveapi import startstop
from calendarAPI.calendarSettings import getEvents, parseDate


dates = getEvents("513MIEM")

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
                    time.sleep(10)
                    startstop.stop()
            time.sleep(1)


daemon = Daemon()
daemon.run()
