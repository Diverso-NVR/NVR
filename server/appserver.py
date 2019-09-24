"""
- creates an application instance and runs the dev server
"""

from threading import Thread
from nvrAPI.models import db, Room, Source
from calendarAPI.calendar_daemon import config_daemon, run_daemon
from calendarAPI.calendarSettings import config_calendar
from driveAPI.driveSettings import config_drive


if __name__ == "__main__":
    from nvrAPI.application import create_app
    app = create_app()
    with app.app_context():
        rooms = Room.query.all()
        for r in rooms:
            config_calendar(r.to_dict())
            config_drive(r.to_dict())
            config_daemon(r.to_dict())
    # Thread(target=run_daemon, name='calendar_daemon').start()
    app.run(host='0.0.0.0')
