from tcp_server import TCPServer
from archive import Archive
import os
import cv2
import sys


def main():
    clern_server = TCPServer()
    clern_server.connect()
    currentFrames = []
    try:
        while True:
            currentArchiveName = clern_server.receiveFile()
            currentFrameArchive = Archive(currentArchiveName)
            currentFrameArchive.extract()
    except Exception as err_type:
        print("\n***TCP SERVER %s error thrown during image processing ***")
        clern_server.close()
        sys.exit()


if __name__ == '__main__':
    main()
