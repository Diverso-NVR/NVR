from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.http import MediaFileUpload
import json
from threading import RLock

lock = RLock()


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


def createFolder(building, room):
    folder_metadata = {
        'name': building + '-' + room,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    folder = service.files().create(body=folder_metadata,
                                    fields='id').execute()

    new_perm = {
        'type': 'anyone',
        'role': 'reader'
    }

    service.permissions().create(fileId=folder['id'], body=new_perm).execute()
    return "https://drive.google.com/drive/u/1/folders/" + folder['id']


def deleteFolder(folder_id):
    service.files().delete(fileId=folder_id).execute()


def upload(filename, room):
    """
    Upload file "filename" on drive
    """
    with lock:
        media = MediaFileUpload(filename, mimetype="video/mp4", resumable=True)
        fileData = {
            "name": filename.split('/')[2],
            "parents": [rooms[room]]
        }
        file = service.files().create(body=fileData, media_body=media, fields='id').execute()
