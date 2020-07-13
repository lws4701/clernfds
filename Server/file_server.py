'''
File Name: start_fileserver.py
Authors: CLERN Development Team
Last Modified: 3 Jul 2020
Description: This module serves as the start script for the
             CLERN file server component of the CLERN Server
'''
from Server.tcp_server import TCPServer
from Server.archive import Archive
import os
import sys


def start_server():
    clern_server = TCPServer()
    clern_server.connect()
    parent_dir = os.getcwd()
    if not (os.path.exists("./archives")):
        os.mkdir("./archives")
    try:
        while True:
            archive_name = clern_server.receiveFile()
            frame_archive = Archive(archive_name)
            os.chdir("./archives")
            frame_archive.extract()
            os.chdir(parent_dir)
            os.remove("./%s" % frame_archive.file_name)
    except Exception as err_type:
        print("\n***TCP SERVER %s error thrown during file transfer ***" % err_type)
        clern_server.close()
        sys.exit()
