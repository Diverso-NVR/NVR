from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json


SCOPES = 'https://www.googleapis.com/auth/calendar'
"""
Setting up calendar
"""
creds = None

token_path = '.creds/tokenCalendar.pickle'

if os.path.exists(token_path):
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            '.creds/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open(token_path, 'wb') as token:
        pickle.dump(creds, token)

calendar_service = build('calendar', 'v3', credentials=creds)

rooms = {}


def config_calendar(room: dict) -> None:
    rooms[room['name']] = room['calendar']


def add_attachment(calendar_id: str, event_id: str, file_id: str) -> None:
    description = f"https://drive.google.com/a/auditory.ru/file/d/{file_id}/view?usp=drive_web"
    changes = {
        'description': description
    }
    calendar_service.events().patch(calendarId=calendar_id, eventId=event_id,
                                    body=changes,
                                    supportsAttachments=True).execute()


def give_permissions(building: str, mail: str) -> None:
    rule = {
        'scope': {
            'type': 'user',
            'value': mail,
        },
        'role': 'writer'
    }

    for room in rooms:
        created_rule = calendar_service.acl().insert(
            calendarId=rooms[room], body=rule).execute()


# def delete_permissions(building, mail):
#     calendars = calendar_service.calendarList().list(pageToken=None).execute()
#     copy_perm = ""
#     for item in calendars['items']:
#         if item['summary'].split('-')[0] == building:
#             copy_perm = item['id']
#             break
#     calendar = calendar_service.acl().list(
#         calendarId=copy_perm).execute()

#     # calendar_service.acl().delete(calendarId='primary', ruleId='ruleId').execute()


def create_calendar(building: str, room: str) -> None:
    calendar_metadata = {
        'summary': building + "-" + room,
        'timeZone': 'Europe/Moscow'
    }

    calendars = calendar_service.calendarList().list(pageToken=None).execute()
    copy_perm = ""
    for item in calendars['items']:
        if item['summary'].split('-')[0] == building:
            copy_perm = item['id']
            break
    calendar = calendar_service.acl().list(
        calendarId=copy_perm).execute()

    created_calendar = calendar_service.calendars().insert(
        body=calendar_metadata).execute()

    for rule in calendar['items']:
        if rule['role'] == 'writer':
            new_rule = calendar_service.acl().insert(
                calendarId=created_calendar["id"], body=rule).execute()
    return created_calendar["id"]  # calendarAPI link


def delete_calendar(calendar_id: str) -> None:
    calendar_service.calendars().delete(calendarId=calendar_id).execute()


def get_events(room: str) -> dict:
    """
    Returns start and summary of the next 3 events on the "room" calendar.
    """
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = calendar_service.events().list(calendarId=rooms[room], timeMin=now,
                                                   maxResults=1, singleEvents=True,
                                                   orderBy='startTime').execute()
    event = events_result['items'][0]
    return event
