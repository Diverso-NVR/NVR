from API.application import create_app
from threading import Thread
from calendarAPI.calendar_daemon import run_daemon


app = create_app()

Thread(target=run_daemon, args=(app,), name='calendar_daemon').start()
