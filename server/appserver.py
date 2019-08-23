"""
- creates an application instance and runs the dev server
"""

from threading import Thread
from nvrAPI.models import db, Room, Source
from calendarAPI.calendar_daemon import configDaemon, runDaemon
from calendarAPI.calendarSettings import configCalendar
from driveAPI.driveSettings import configDrive


if __name__ == "__main__":
    from nvrAPI.application import create_app
    app = create_app()
    with app.app_context():
        rooms = Room.query.all()
        for r in rooms:
            configCalendar(r.to_dict())
            configDrive(r.to_dict())
            configDaemon(r.to_dict())
    Thread(target=runDaemon, name='calendar_daemon').start()
    app.run(host='0.0.0.0')
