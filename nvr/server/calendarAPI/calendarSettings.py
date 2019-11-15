from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
from pprint import pprint
from datetime import datetime, timedelta

from nvrAPI.models import nvr_db_context, Room


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


def add_attachment(calendar_id: str, event_id: str, file_id: str) -> None:
    """
    Adds url of drive file 'file_id' to calendar event 'event_id'
    """
    event = calendar_service.events().get(
        calendarId=calendar_id, eventId=event_id).execute()
    description = event['description'] + \
        f"\nhttps://drive.google.com/a/auditory.ru/file/d/{file_id}/view?usp=drive_web"
    changes = {
        'description': description
    }
    calendar_service.events().patch(calendarId=calendar_id, eventId=event_id,
                                    body=changes,
                                    supportsAttachments=True).execute()


@nvr_db_context
def create_event_(room_name: str, start_time: str, end_time: str, summary: str) -> str:
    """
        format 2019-11-12T15:00
    """
    room = Room.query.filter_by(name=room_name).first()
    date_format = "%Y-%m-%dT%H:%M:%S"

    start_dateTime = datetime.strptime(start_time, date_format[:-3])
    end_StartTime = datetime.strptime(end_time, date_format[:-3]) \
        if end_time else start_dateTime + timedelta(minutes=80)

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_dateTime.strftime(date_format),
            'timeZone': "Europe/Moscow"
        },
        'end': {
            'dateTime': end_StartTime.strftime(date_format),
            'timeZone': "Europe/Moscow"
        }
    }

    event = calendar_service.events().insert(
        calendarId=room.calendar, body=event).execute()

    return event['htmlLink']


@nvr_db_context
def give_permissions(building: str, mail: str) -> None:
    """
    Give write permissions to user 'mail', according his 'building'
    """
    rule = {
        'scope': {
            'type': 'user',
            'value': mail,
        },
        'role': 'writer'
    }

    for room in Room.query.all():
        try:
            created_rule = calendar_service.acl().insert(
                calendarId=room.calendar, body=rule).execute()
        except:
            pass


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
    """
    Creates calendar with name: 'building'-'room'
    and grant access to all users from same campus
    """
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

    created_calendar = calendar_service.calendars().insert(
        body=calendar_metadata).execute()

    if copy_perm:
        calendar = calendar_service.acl().list(
            calendarId=copy_perm).execute()

        for rule in calendar['items']:
            if rule['role'] == 'writer':
                new_rule = calendar_service.acl().insert(
                    calendarId=created_calendar["id"], body=rule).execute()

    return created_calendar["id"]  # calendarAPI link


def delete_calendar(calendar_id: str) -> None:
    """
    Delete calendar with 'calendar_id' id
    """
    try:
        calendar_service.calendars().delete(calendarId=calendar_id).execute()
    except Exception as e:
        pass
