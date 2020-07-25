"""
archive.py

Description: A simple archiving handling class made for handling video frame archives
"""

from zipfile import ZipFile
from datetime import datetime
import os


class Archive:
    def __init__(self, file_name=str(abs(hash(datetime.now()))) + '.zip'):
        self.file_name = file_name
        self.name_wo_extension = file_name.replace('.zip', '')
        self.zip_archive = ZipFile(file_name, 'w')

    def add(self, file_name):
        try:
            self.zip_archive.write(file_name)
        except Exception as err_type:
            print("Unable to add %s to %s: %s" %
                  (file_name, self.zip_archive.file_name, err_type))

    def extract(self):
        os.mkdir(self.name_wo_extension)
        os.chdir(self.name_wo_extension)
        self.zip_archive.extractall()
        self.zip_archive.close()

    def close(self):
        """Ryan - Need this to send a valid .zip"""
        self.zip_archive.close()

    def open(self):
        """
        Ryan - May have some use for future
        (maybe only instantiate the zip once?)
        """
        self.zip_archive.open()
