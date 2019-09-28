from nvrAPI.application import create_app
from threading import Thread
from nvrAPI.models import db, Room, Source
from calendarAPI.calendar_daemon import run_daemon


app = create_app()

Thread(target=run_daemon, args=(app,), name='calendar_daemon').start()
