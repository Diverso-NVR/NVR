from __future__ import print_function

from threading import RLock

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client import file, client, tools

lock = RLock()

SCOPES = 'https://www.googleapis.com/auth/drive'
"""
Setting up drive
"""
store = file.Storage('.creds/tokenDrive.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('.creds/credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
driveService = build('drive', 'v3', http=creds.authorize(Http()))

rooms = {}


def configDrive(room: dict) -> None:
    rooms[room['name']] = room['drive'].split('/')[-1]


def createFolder(building: str, room: str) -> str:
    folder_metadata = {
        'name': building + '-' + room,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    folder = driveService.files().create(body=folder_metadata,
                                         fields='id').execute()

    new_perm = {
        'type': 'anyone',
        'role': 'reader'
    }

    driveService.permissions().create(
        fileId=folder['id'], body=new_perm).execute()
    return "https://drive.google.com/drive/u/1/folders/" + folder['id']


def deleteFolder(folder_id: str) -> None:
    driveService.files().delete(fileId=folder_id).execute()


def upload(filename: str, room: str) -> str:
    """
    Upload file "filename" on drive
    """
    media = MediaFileUpload(filename, mimetype="video/mp4", resumable=True)
    fileData = {
        "name": filename.split('/')[4],
        "parents": [rooms[room]]
    }
    file = driveService.files().create(
        body=fileData, media_body=media).execute()
    return file.get('id')
