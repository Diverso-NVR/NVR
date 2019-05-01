from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import json
import datetime


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

with open("app/data.json", 'r') as f:
    data = json.loads(f.read())

rooms = {}

for building in data:
    for room in data[building]:
        rooms[room['auditorium']] = room['calendarAPI']


# TODO add permission by building
def addWriter(mail):
    rule = {
        'scope': {
            'type': 'user',
            'value': mail,
        },
        'role': 'writer'
    }
    for room in rooms:
        created_rule = service.acl().insert(
            calendarId=rooms[room], body=rule).execute()


# TODO when calendar is created, grant permission for it for users
def createCalendar(title):
    calendar = {
        'summary': title,
        'timeZone': 'Europe/Moscow'
    }

    created_calendar = service.calendars().insert(body=calendar).execute()
    return created_calendar["id"]


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


# TODO return all events with new data structure, separated by building
def getEvents(room):
    """
    Returns start and summary of the next 10 events on the "room" calendar.
    """
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId=rooms[room], timeMin=now,
                                          maxResults=2, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events
