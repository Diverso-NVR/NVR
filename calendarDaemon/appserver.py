"""
- creates an application instance and runs the dev server
"""

from threading import Thread
from calendarAPI.calendar_daemon import run_daemon


if __name__ == "__main__":
    from API.application import create_app
    app = create_app()

    Thread(target=run_daemon, args=(app,), name='calendar_daemon').start()
    app.run(host='0.0.0.0', port='9090')
