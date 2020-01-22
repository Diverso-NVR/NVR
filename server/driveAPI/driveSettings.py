from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
import io


from threading import RLock
lock = RLock()


SCOPES = 'https://www.googleapis.com/auth/drive'
"""
Setting up drive
"""
creds = None
token_path = '.creds/tokenDrive.pickle'
creds_path = '.creds/credentials.json'

if os.path.exists(token_path):
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            creds_path, SCOPES)
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


def get_folders_by_name(name):
    with lock:
        page_token = None

        while True:
            response = drive_service.files().list(q=f"mimeType='application/vnd.google-apps.folder'"
                                                    f"and name='{name}'",
                                                  spaces='drive',
                                                  fields='nextPageToken, files(name, id, parents)',
                                                  pageToken=page_token).execute()
            page_token = response.get('nextPageToken', None)

            if page_token is None:
                break

        return {folder['id']: folder.get('parents', [''])[0] for folder in response['files']}
