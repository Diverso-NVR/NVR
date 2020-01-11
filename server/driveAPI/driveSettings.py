from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
import io
from datetime import datetime


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


# Нужно вынести в сервис склейки
def download_video(video_id: str, video_name: str) -> None:
    request = drive_service.files().get_media(fileId=video_id)
    fh = io.FileIO(video_name, mode='w')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()


def get_video_by_name(name: str) -> str:
    page_token = None

    while True:
        response = drive_service.files().list(q=f"mimeType='video/mp4'"
                                                f"and name='{name}'",
                                                spaces='drive',
                                                fields='nextPageToken, files(name, id)',
                                                pageToken=page_token).execute()
        page_token = response.get('nextPageToken', None)

        if page_token is None:
            break

    return response['files'][0]['id']


def get_dates_between_timestamps(start_timestamp: int, stop_timestamp: int) -> list:

    start_timestamp = start_timestamp // 1800 * 1800
    stop_timestamp = (stop_timestamp // 1800 + 1) * 1800 if int(
        stop_timestamp) % 1800 != 0 else (stop_timestamp // 1800) * 1800

    dates = []
    for timestamp in range(start_timestamp, stop_timestamp, 1800):
        dates.append(datetime.fromtimestamp(timestamp))

    return dates

# Example
# d = get_dates_between_timestamps(1578764926, 1578764926 + 2700)

# room_name = 'Зал'
# source_name = '54'

# d = [i.strftime(f'%Y-%m-%d_%H:%M_{room_name}_{source_name}.mp4') for i in d]
# print(d)

# for i in d:
#     g = get_video_by_name(i)
#     download_video(g, i)
