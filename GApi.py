from __future__ import print_function
import pickle
import os.path
import gspread
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd

class Api():
    """ Basic class of API clients """
    def __init__(self):
        """ Basic classes initialization """
        self.API_NAME = 'drive'
        self.API_VERSION = 'v3'
        self.CLIENT_SECRET_FILE = 'credentials.json'
        self.SCOPES = ['https://www.googleapis.com/auth/drive',
                        'https://www.googleapis.com/auth/spreadsheets']

    def auth(self):
        """ Authentication api with token or secret_file """
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRET_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        # registration services
        self.GS = gspread.authorize(creds)
        self.DRIVE = build(self.API_NAME, self.API_VERSION, credentials=creds)

        return self

class GoogleAPI(Api):
    """ Google Drive Class of API clients """
    def __init__(self):
        """ Parent classes initialization """
        super().__init__()

    def create(self, name, parent):
        """ Create folder method """
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parent': parent,
        }
        request = self.DRIVE.files().create(body=file_metadata).execute()
        return request['id']
    
    def read(self, name):
        """ Search method """
        query = f"name = '{name}'"
        response = self.DRIVE.files().list(q = query).execute().get("files")
        df = pd.DataFrame(response)
        print(f"Вывод: \n{df}\n")

    def update(self, file_id, folder_id):
        """ Moving files between folders """
        # Retrieve the existing parents to remove
        file = self.DRIVE.files().get(fileId=file_id,
                                        fields='parents').execute()
        previous_parents = ",".join([parent["id"] for parent in file.get('parents')])
        # Move the file to the new folder
        file = self.DRIVE.files().update(fileId=file_id,
                                            addParents=folder_id,
                                            removeParents=previous_parents,
                                            fields='id, parents').execute()

    def delete(self, file_id):
        self.DRIVE.files().delete(file_id)

    def copy(self, name, id_data, times):
        pass

class Gspread(Api):
    """ Gspread Library Class of API clients """
    def __init__(self):
        """ Parent classes initialization """
        super().__init__()
    
    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass