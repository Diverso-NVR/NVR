from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

from API.models import nvr_db_context, Room


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


@nvr_db_context
def get_events(room_id: int) -> dict:
    """
    Returns start/end time and summary of the next event of the "room" calendar.
    """
    room = Room.query.get(room_id)
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = calendar_service.events().list(calendarId=room.calendar, timeMin=now,
                                                   maxResults=1, singleEvents=True,
                                                   orderBy='startTime').execute()
    event = events_result['items'][0]
    return event
