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
store = file.Storage('.creds/tokenDrive.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('.creds/credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
drive_service = build('drive', 'v3', http=creds.authorize(Http()))

rooms = {}


def config_drive(room: dict) -> None:
    rooms[room['name']] = room['drive'].split('/')[-1]


def create_folder(building: str, room: str) -> str:
    folder_metadata = {
        'name': building + '-' + room,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    folder = drive_service.files().create(body=folder_metadata,
                                          fields='id').execute()

    new_perm = {
        'type': 'anyone',
        'role': 'reader'
    }

    drive_service.permissions().create(
        fileId=folder['id'], body=new_perm).execute()
    return "https://drive.google.com/drive/u/1/folders/" + folder['id']


def delete_folder(folder_id: str) -> None:
    drive_service.files().delete(fileId=folder_id).execute()


def move_file(file_id: str, room: str):
    folder_id = [rooms[room]]
    file = drive_service.files().get(fileId=file_id,
                                     fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))
    file = drive_service.files().update(fileId=file_id,
                                        addParents=folder_id,
                                        removeParents=previous_parents,
                                        fields='id, parents').execute()


def upload(filename: str, room: str, names: list = []) -> str:
    """
    Upload file "filename" on drive
    """
    media = MediaFileUpload(filename, mimetype="video/mp4", resumable=True)
    file_data = {
        "name": filename.split('/')[4],
        "parents": [rooms[room]],
        'description': 'На занятии присутсвовали: ' + ','.join(names)
    }
    file = drive_service.files().create(
        body=file_data, media_body=media).execute()
    return file.get('id')
