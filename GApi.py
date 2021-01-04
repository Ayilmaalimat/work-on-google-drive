from __future__ import print_function
import pickle
import gspread
import os
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

    def create(self, name):
        """ Create folder method """
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        request = self.DRIVE.files().create(body=file_metadata).execute()
        print("Create Complete")
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
        # Move the file to the new folder
        file = self.DRIVE.files().update(fileId=file_id,
                                            addParents=folder_id,
                                            fields='id, parents').execute()

    def delete(self, file_id):
        """ Delete data in Google Drive"""
        self.DRIVE.files().delete(file_id).execute()

    def download(self, fileId, destinationFolder):
        """ Download directory files """
        if not os.path.isdir(destinationFolder):
            os.mkdir(path=destinationFolder)

        results = self.DRIVE.files().list(
            pageSize=300,
            q="parents in '{0}'".format(fileId),
            fields="files(id, name, mimeType)"
            ).execute()

        items = results.get('files', [])

        for item in items:
            itemName = item['name']
            itemId = item['id']
            itemType = item['mimeType']
            filePath = destinationFolder + "/" + itemName

            if itemType == 'application/vnd.google-apps.folder':
                print("Stepping into folder: {0}".format(filePath))
                self.download(itemId, filePath) # Recursive call
            elif not itemType.startswith('application/'):
                self.downloadFile(itemId, filePath)
            else:
                print("Unsupported file: {0}".format(itemName))
    
    def downloadFile(self, fileId, filePath):
        print("-> Downloading file with id: {0} name: {1}".format(fileId, filePath))
        request = self.DRIVE.files().get_media(fileId=fileId)
        fh = io.FileIO(filePath, mode='wb')
        
        try:
            downloader = MediaIoBaseDownload(fh, request, chunksize=1024*1024)

            done = False
            while done is False:
                status, done = downloader.next_chunk(num_retries = 2)
                if status:
                    print("Download %d%%." % int(status.progress() * 100))
            print("Download Complete!") 
        finally:
            fh.close()

    def backupFiles(self, fileId, hours):
        from apscheduler.schedulers.background import BackgroundScheduler
        import time

        self.download(fileId, time.strftime('%d %b %y'))

        try:
            scheduler = BackgroundScheduler()
            scheduler.add_job(self.download, 'interval', 
                    args=(fileId, time.strftime('%d %b %y')), 
                    hours=hours)
            scheduler.start()
            print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

            while True:
                time.sleep(2)
        except:
            scheduler.shutdown() 

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