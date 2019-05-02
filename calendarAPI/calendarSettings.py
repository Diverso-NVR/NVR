from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import json
import datetime


SCOPES = 'https://www.googleapis.com/auth/calendar'
"""
Setting up calendar
"""
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
    rooms[building] = {}
    for room in data[building]:
        rooms[building][room['auditorium']] = room['calendar']


def givePermissions(building, mail):
    rule = {
        'scope': {
            'type': 'user',
            'value': mail,
        },
        'role': 'writer'
    }

    for room in rooms[building]:
        created_rule = service.acl().insert(
            calendarId=rooms[building][room], body=rule).execute()


def createCalendar(building, title):
    calendar = {
        'summary': title,
        'timeZone': 'Europe/Moscow'
    }

    created_calendar = service.calendars().insert(body=calendar).execute()

    calendars = service.calendarList().list(pageToken=None).execute()
    copyPerm = ""
    for item in calendars['items']:
        if item['summary'].split('-')[0] == building:
            copyPerm = item['id']
            break
    calendar = service.acl().list(
        calendarId=copyPerm).execute()
    for rule in calendar['items']:
        if rule['role'] == 'writer':
            created_rule = service.acl().insert(
                calendarId=created_calendar["id"], body=rule).execute()

    return created_calendar["id"]  # calendarAPI link


def deleteCalendar(calendar_id):
    service.calendars().delete(calendarId=calendar_id).execute()


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


def getEvents(building, room):
    """
    Returns start and summary of the next 3 events on the "room" calendar.
    """
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId=rooms[building][room], timeMin=now,
                                          maxResults=3, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events
