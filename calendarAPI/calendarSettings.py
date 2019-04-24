from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import json

with open("app/data.json", 'r') as f:
    data = json.loads(f.read())

rooms = {}

for building in data:
    for room in data[building]:
        rooms[room['auditorium']] = room['calendarAPI']


def parseDate(date):
    """
    Parses date in YYYY-MM-DD hh-mm format
    """
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    hour = date[11:13]
    minute = date[14:16]
    return "{}-{}-{} {}:{}".format(year, month, day, hour, minute)


def getEvents(room):
    """
    Returns start and summary of the next 10 events on the "room" calendar.
    """
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId=rooms[room], timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events


# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'
"""
Setting up calendar
"""
# The file tokenCalendar.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
store = file.Storage('tokenCalendar.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))
