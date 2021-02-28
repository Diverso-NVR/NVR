from __future__ import print_function

import os.path
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from threading import RLock

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from core.models import Session, Room

lock = RLock()

HOME = str(Path.home())
SCOPES = "https://www.googleapis.com/auth/calendar"
"""
Setting up calendar
"""
# creds = None
# token_path = "/creds/tokenCalendar.pickle"
# creds_path = "/creds/credentials.json"

# if os.path.exists(token_path):
#     with open(token_path, "rb") as token:
#         creds = pickle.load(token)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
#             creds = flow.run_local_server(port=0)
#         with open(token_path, "wb") as token:
#             pickle.dump(creds, token)

# calendar_service = build("calendar", "v3", credentials=creds)


def create_event_(room_name: str, start_time: str, end_time: str, summary: str) -> str:
    """
    format 2019-11-12T15:00
    """
    with lock:
        session = Session()
        room = session.query(Room).filter_by(name=room_name).first()
        session.close()
        if not room:
            raise NameError()

        date_format = "%Y-%m-%dT%H:%M:%S"

        start_dateTime = datetime.strptime(start_time, date_format[:-3])
        end_StartTime = (
            datetime.strptime(end_time, date_format[:-3])
            if end_time
            else start_dateTime + timedelta(minutes=80)
        )

        event = {
            "summary": summary,
            "start": {
                "dateTime": start_dateTime.strftime(date_format),
                "timeZone": "Europe/Moscow",
            },
            "end": {
                "dateTime": end_StartTime.strftime(date_format),
                "timeZone": "Europe/Moscow",
            },
        }

        event = (
            calendar_service.events()
            .insert(calendarId=room.calendar, body=event)
            .execute()
        )

        return event["htmlLink"]


def create_calendar(room: str) -> str:
    """
    Creates calendar with name: 'room'
    """
    with lock:
        calendar_metadata = {"summary": room, "timeZone": "Europe/Moscow"}
        created_calendar = (
            calendar_service.calendars().insert(body=calendar_metadata).execute()
        )
        return created_calendar["id"]  # calendarAPI link


def delete_calendar(calendar_id: str) -> None:
    """
    Delete calendar with 'calendar_id' id
    """
    with lock:
        try:
            calendar_service.calendars().delete(calendarId=calendar_id).execute()
        except Exception as e:
            print(e)


def get_events(
    calendar_id: str,
    start_time: datetime or None = None,
    end_time: datetime or None = None,
) -> list:
    if start_time is None and end_time is None:
        now = datetime.utcnow()
        start_time = now - timedelta(days=30)
        end_time = now + timedelta(days=30)

    events_result = []
    page_token = None
    while True:
        events = (
            calendar_service.events()
            .list(
                calendarId=calendar_id,
                pageToken=page_token,
                timeMin=start_time.isoformat() + "Z",
                timeMax=end_time.isoformat() + "Z",
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        page_token = events.get("nextPageToken")
        events_result += events["items"]

        if not page_token:
            break

    return events_result
