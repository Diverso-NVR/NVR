from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.http import MediaFileUpload
import json


SCOPES = 'https://www.googleapis.com/auth/drive'
"""
Setting up drive
"""
store = file.Storage('tokenDrive.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('drive', 'v3', http=creds.authorize(Http()))

with open("app/data.json", 'r') as f:
    data = json.loads(f.read())
rooms = {}
for building in data:
    for room in data[building]:
        rooms[room['auditorium']] = room['drive'].split('/')[-1]


def createFolder(title):
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    file = service.files().create(body=file_metadata,
                                  fields='id').execute()

    new_perm = {
        'type': 'anyone',
        'role': 'reader'
    }

    service.permissions().create(fileId=file['id'], body=new_perm).execute()

    return "https://drive.google.com/drive/u/1/folders/" + file['id']


def upload(filename, room):
    """
    Upload file "filename" on drive
    """
    media = MediaFileUpload(filename, mimetype="video/mp4", resumable=True)
    fileData = {
        "name": filename.split('/')[2],
        "parents": [rooms[room]]
    }
    file = service.files().create(body=fileData, media_body=media, fields='id').execute()
