from __future__ import print_function
import pickle
import os.path
import gspread
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GoogleAPI():
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive',
                    'https://www.googleapis.com/auth/spreadsheets']
        self.secret_file = 'credentials.json'

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
                    self.secret_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        self.GS = gspread.authorize(creds)
        self.DRIVE = build('drive', 'v3', credentials=creds)
    
    def create(self, name, path, service):
        pass
    
    def read(self, path):
        pass

    def update(self, name, id_data, new_param):
        pass
    
    def delete(self, name, id_data):
        pass

    def download(self, name, id_data):
        pass

    def backup_files(self, name, id_data, times):
        pass