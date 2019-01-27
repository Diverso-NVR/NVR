from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive'
"""
Setting up drive
"""
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
store = file.Storage('tokenDrive.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('drive', 'v3', http=creds.authorize(Http()))

# Call the Drive v3 API
# results = service.files().list(
#     pageSize=10, fields="nextPageToken, files(id, name)").execute()
# items = results.get('files', [])

# if not items:
#     print('No files found.')
# else:
#     print('Files:')
#     for item in items:
#         print(u'{0} ({1})'.format(item['name'], item['id']))


def upload(filename):
    """
    Upload file "filename" on drive
    """
    rooms = {"513MIEM": "1EkXrlRNtXp-YBF1-8SGanCvZRLThy3e_", "P500": "1EbJg0IzJLP788qWVr0u_Y9SmZ8ygzKwr",
             "P505": "15Ant5hntmfl84Rrkzr9dep2nh13sbXft", "S401": "1L4icf2QJsv7dBBDygNNXCG9dOnPwxY9r"}
    room = filename.split('-')[3]
    media = MediaFileUpload(filename, mimetype="video/mp4", resumable=True)
    fileData = {"name": filename.split('/')[2],
                "parents": [rooms[room]]
                }
    file = service.files().create(body=fileData, media_body=media, fields='id').execute()
