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
import threading, time


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

    def create(self, folderName, parentID=None):
        """ Create folder method """
        body = {
            'name': folderName,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parentID]
        }
        if parentID:
            body['parents'] = [parentID]
        request = self.DRIVE.files().create(body=body).execute()
        print(f"-> Create Complete with name: {body['name']} folder_id {body['parents']}")
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
        print(f"-> Downloading file with id: {fileId} name: {filePath}")
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
    
    def loopDownload(self, fileId, folderName, interval):
        while True:
            self.download(fileId, folderName)
            time.sleep(interval)


    def backupFiles(self, fileId, seconds=0, minutes=0, hours=0, days=0):
        folderName = time.strftime("%b %d %Y %H-%M-%S")
        interval = seconds + minutes*60 + hours*60*60 + days*24*60*60
        
        t = threading.Thread(target=self.loopDownload, args=(fileId, folderName, interval))
        t.start()
        
class Gspread(Api):
    """ Gspread Library Class of API clients """
    def __init__(self):
        """ Parent classes initialization """
        super().__init__()
    
    def create(self, name):
        sh = self.GS.create(name)
        print(f"Create Complete! \nId = {sh.id}")
        return sh.id

    def read(self, id_, sheet_id):
        response = self.GS.open_by_key(id_).get_worksheet(sheet_id).get_all_values()
        df = pd.DataFrame(response)
        print(f"Вывод: \n{df}\n")

    def update(self):
        pass

    def delete(self):
        pass