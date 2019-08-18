from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from driveAPI.driveSettings import driveService
from oauth2client import file, client, tools
import json
import datetime

from threading import RLock

lock = RLock()

SCOPES = 'https://www.googleapis.com/auth/calendar'
"""
Setting up calendar
"""
store = file.Storage('.creds/tokenCalendar.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('.creds/credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
calendarService = build('calendar', 'v3', http=creds.authorize(Http()))


rooms = {}


def configCalendar(room: dict) -> None:
    rooms[room['name']] = room['calendar']


def add_attachment(calendarId: str, eventId: str, fileId: str) -> None:
    file = driveService.files().get(fileId=fileId).execute()
    event = calendarService.events().get(calendarId=calendarId,
                                         eventId=eventId).execute()

    attachments = event.get('attachments', [])
    file_url = 'https://drive.google.com/a/auditory.ru/file/d/' + \
        file['id'] + '/view?usp=drive_web'
    attachments.append({
        'fileUrl': file_url,
        'mimeType': file['mimeType'],
        'title': file['name']
    })
    changes = {
        'attachments': attachments
    }
    calendarService.events().patch(calendarId=calendarId, eventId=eventId,
                                   body=changes,
                                   supportsAttachments=True).execute()


def givePermissions(building: str, mail: str) -> None:
    rule = {
        'scope': {
            'type': 'user',
            'value': mail,
        },
        'role': 'writer'
    }

    for room in rooms:
        created_rule = calendarService.acl().insert(
            calendarId=rooms[room], body=rule).execute()


# def deletePermissions(building, mail):
#     calendars = calendarService.calendarList().list(pageToken=None).execute()
#     copyPerm = ""
#     for item in calendars['items']:
#         if item['summary'].split('-')[0] == building:
#             copyPerm = item['id']
#             break
#     calendar = calendarService.acl().list(
#         calendarId=copyPerm).execute()

#     # calendarService.acl().delete(calendarId='primary', ruleId='ruleId').execute()


def createCalendar(building: str, room: str) -> None:
    calendar_metadata = {
        'summary': building + "-" + room,
        'timeZone': 'Europe/Moscow'
    }

    calendars = calendarService.calendarList().list(pageToken=None).execute()
    copyPerm = ""
    for item in calendars['items']:
        if item['summary'].split('-')[0] == building:
            copyPerm = item['id']
            break
    calendar = calendarService.acl().list(
        calendarId=copyPerm).execute()

    created_calendar = calendarService.calendars().insert(
        body=calendar_metadata).execute()

    for rule in calendar['items']:
        if rule['role'] == 'writer':
            new_rule = calendarService.acl().insert(
                calendarId=created_calendar["id"], body=rule).execute()

    return created_calendar["id"]  # calendarAPI link


def deleteCalendar(calendarId: str) -> None:
    calendarService.calendars().delete(calendarId=calendarId).execute()


def getEvents(room: str) -> dict:
    """
    Returns start and summary of the next 3 events on the "room" calendar.
    """
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = calendarService.events().list(calendarId=rooms[room], timeMin=now,
                                                  maxResults=1, singleEvents=True,
                                                  orderBy='startTime').execute()
    event = events_result['items'][0]
    return event
