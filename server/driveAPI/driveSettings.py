from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

from threading import RLock
lock = RLock()


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


def create_folder(folder_name: str, folder_parent_id: str = '') -> str:
    """
    Creates folder in format: 'folder_name'
    """
    with lock:
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if folder_parent_id:
            folder_metadata['parents'] = [folder_parent_id]
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
    """
    Deletes folder with 'folder_id' id
    """
    with lock:
        drive_service.files().delete(fileId=folder_id).execute()


def move_file(file_id: str, folder_id: str):
    file = drive_service.files().get(fileId=file_id,
                                     fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))
    file = drive_service.files().update(fileId=file_id,
                                        addParents=folder_id,
                                        removeParents=previous_parents,
                                        fields='id, parents').execute()


def upload(filename: str, folder_id: str) -> str:
    """
    Upload file "filename" on drive folder 'folder_id'
    """
    with lock:
        media = MediaFileUpload(filename, mimetype="video/mp4", resumable=True)
        file_data = {
            "name": filename.split('/')[4],
            "parents": [folder_id]
        }
        file = drive_service.files().create(
            body=file_data, media_body=media).execute()
        return file.get('id')


def get_folder_by_date(date):
    with lock:
        page_token = None

        while True:
            response = drive_service.files().list(q=f"mimeType='application/vnd.google-apps.folder' and name='{date}'",
                                                  spaces='drive',
                                                  fields='nextPageToken, files(name, id, parents)',
                                                  pageToken=page_token).execute()
            page_token = response.get('nextPageToken', None)

            if page_token is None:
                break

        return {folder['id']: folder.get('parents', [''])[0] for folder in response['files']}
