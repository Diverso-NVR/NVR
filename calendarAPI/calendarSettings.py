from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


rooms = {"513MIEM": "hsenvrproject@gmail.com", "P500": "cfqf9t99a65oi1jd3sbcccp9k0@group.calendar.google.com",
         "P505": "33e4j4htl0bvmmuc3t45ehsphk@group.calendar.google.com", "C401": "adfevhq6dbe00or14dkhfkq68k@group.calendar.google.com"}


def addEvent(room, summary, start, end):
    """
    Creates an event in "room" with title "summary", starts at "start, ends at "end"
    """
    GMT_OFF = "+03:00"
    EVENT = {
        "summary": summary,
        "start": {"dateTime": "2019-01-19T12:00:00%s" % GMT_OFF},
        "end": {"dateTime": "2019-01-19T16:00:00%s" % GMT_OFF}
    }

    e = service.events().insert(calendarId=rooms[room],
                                sendNotifications=True, body=EVENT).execute()
    print('''*** %r event added:
        Start: %s
        End: %s''' % (e["summary"].encode('utf-8'),
                      e['start']['dateTime'], e['end']['dateTime']))


def parseDate(date):
    """
    Parses date in YYYY-MM-DD hh-mm format
    """
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    hour = date[11:13]
    minute = date[14:16]
    # second = date[17:19]
    return "{}-{}-{} {}:{}".format(year, month, day, hour, minute)


def getEvents(room):
    """
    Prints the start and name of the next 10 events on the "room" calendar.
    """
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    # print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId=rooms[room], timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    # for event in events:
    #     start = event['start'].get('dateTime', event['start'].get('date'))
    #     end = event['end'].get('dateTime', event['end'].get('date'))
    #     print(start, end, event['summary'])

    return events


# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'
"""
Setting up calendar
"""
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
store = file.Storage('../tokenCalendar.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('../credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))
