from threading import Thread
from nvrAPI.models import db, Room, Source
from calendarAPI.calendar_daemon import configDaemon, runDaemon
from calendarAPI.calendarSettings import configCalendar
from driveAPI.driveSettings import configDrive


Thread(target=runDaemon, name='calendar_daemon').start()

from nvrAPI.application import create_app
app = create_app()
with app.app_context():
    rooms = Room.query.all()
    for r in rooms:
        configCalendar(r.to_dict())
        configDrive(r.to_dict())
        configDaemon(r.to_dict())


