from nvrAPI.application import create_app
from threading import Thread
from nvrAPI.models import db, Room, Source
from calendarAPI.calendar_daemon import config_daemon, run_daemon
from calendarAPI.calendarSettings import config_calendar
from driveAPI.driveSettings import config_drive


Thread(target=run_daemon, name='calendar_daemon').start()

app = create_app()
with app.app_context():
    rooms = Room.query.all()
    for r in rooms:
        config_calendar(r.to_dict())
        config_drive(r.to_dict())
        config_daemon(r.to_dict())
