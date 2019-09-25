from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

SCOPES = 'https://www.googleapis.com/auth/drive'
"""
Setting up drive
"""
creds = None
token_path = '.creds/tokenDrive.pickle'

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

drive_service = build('drive', 'v3', credentials=creds)


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


# def move_file(file_id: str, room: str):
#     folder_id = [rooms[room]]
#     file = drive_service.files().get(fileId=file_id,
#                                      fields='parents').execute()
#     previous_parents = ",".join(file.get('parents'))
#     file = drive_service.files().update(fileId=file_id,
#                                         addParents=folder_id,
#                                         removeParents=previous_parents,
#                                         fields='id, parents').execute()


def upload(filename: str, drive_url: int, names: list = []) -> str:
    """
    Upload file "filename" on drive
    """
    media = MediaFileUpload(filename, mimetype="video/mp4", resumable=True)
    file_data = {
        "name": filename.split('/')[4],
        "parents": [drive_url],
        'description': 'На занятии присутсвовали: ' + ','.join(names)
    }
    file = drive_service.files().create(
        body=file_data, media_body=media).execute()
    return file.get('id')
