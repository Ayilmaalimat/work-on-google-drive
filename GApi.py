from __future__ import print_function
import pickle
import os.path
import gspread
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
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