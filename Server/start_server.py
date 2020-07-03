from zipfile import ZipFile

from Server.tcp_server import TCPServer
from Server.archive import Archive
import os
import cv2
import sys


def main():
    clern_server = TCPServer()
    clern_server.connect()
    currentFrames = []
    try:
        while True:
            clern_server.connect()
            if not (os.path.exists("./archives")):
                os.mkdir("archives")
            os.chdir('archives')
            currentArchiveName = clern_server.receiveFile()
            currentFrameArchive = Archive(currentArchiveName)
            currentFrameArchive.extract()
            currentFrameArchive.close()
            os.remove(currentArchiveName)
            fileDir = currentFrameArchive.nameWOExtension
            fileList = os.listdir(fileDir)
            fileList = [fileDir + x for x in fileList]
            """for currentFile in fileList:
                currentFrames.append(cv2.imread(currentFile))
                os.remove(currentFile)"""
            # personCoords = [] (frameName, coordinates)
            # for frame in currentFrames:
                # personCoords.append(detectPerson(frame))"""
    except Exception as err_type:
        print("\n***TCP SERVER %s error thrown during image processing ***" % err_type)
        clern_server.close()
        sys.exit()


if __name__ == '__main__':
    main()
