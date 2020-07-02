'''
archive.py

Description: A simple archiving handling class made for handling video frame archives
'''
from zipfile import ZipFile
from datetime import datetime
from os import path
import os


class Archive:
    fileName = None

    def __init__(self, fileName=str(abs(hash(datetime.now()))) + '.zip'):
        self.fileName = fileName
        self.nameWOExtension = fileName.replace('.zip', '')
        self.zipArchive = ZipFile(fileName, 'w')

    def add(self, fileName):
        try:
            self.zipArchive.write(fileName)
        except:
            print("Unable to add %s to %s" %
                  (fileName, self.zipArchive.filename))

    def extract(self):
        os.mkdir(self.nameWOExtension)
        os.chdir(self.nameWOExtension)
        self.zipArchive.extractall()
        self.zipArchive.close()

    def close(self):
        """Ryan - Need this to send a valid .zip"""
        self.zipArchive.close()

    def open(self):
        """
        Ryan - May have some use for future
        (maybe only instantiate the zip once?)
        """
        self.zipArchive.open()
# DO NOT USE: CV2 HAS cv2.imwrite() and cv2.imread(). Use these for writing to file instead

# # Helper function for reading an image a byte string
# def readImage(fileName):
#     try:
#         with open(fileName, 'rb') as cf:
#             return cf.read() # returns a string of hex values
#     except:
#         print("Unable to read image: %s" % fileName) # In the case the file does not exist/cannot be opened


# # Write an image as a bytestring to a file
# def writeImage(byteString, fileName):
#     with open(fileName, 'wb') as cf:
#         cf.write(byteString) # writes a hexadecimal stream to a file
