from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = "https://www.googleapis.com/auth/calendar"
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets("credentials.json", SCOPES)
    creds = tools.run_flow(flow, store, flags)
CAL = build("calendar", "v3", http=creds.authorize(Http()))

GMT_OFF = "+03:00"
EVENT = {
    "summary": "Math conference",
    "start": {"dateTime": "2018-12-30T12:00:00%s" % GMT_OFF},
    "end": {"dateTime": "2018-12-30T16:00:00%s" % GMT_OFF}
}

e = CAL.events().insert(calendarId="primary",
                        sendNotifications=True, body=EVENT).execute()
print('''*** %r event added:
    Start: %s
    End: %s''' % (e["summary"].encode('utf-8'),
        e['start']['dateTime'], e['end']['dateTime']))
