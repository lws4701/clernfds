"""
archive.py

Description: A simple archiving handling class made for handling video frame archives
"""
from zipfile import ZipFile
from datetime import datetime
import os


class Archive:
    file_name = None

    def __init__(self, file_name=str(abs(hash(datetime.now()))) + '.zip'):
        self.file_name = file_name
        self.name_woextension = file_name.replace('.zip', '')
        self.zip_archive = ZipFile(file_name, 'r')

    def extract(self) -> None:
        """
        Extracts all of the zip contents into the current directory
        :return:
        """
        if not os.path.exists(self.name_woextension):
            os.mkdir(self.name_woextension)
        os.chdir(self.name_woextension)
        self.zip_archive.extractall()
        self.zip_archive.close()
