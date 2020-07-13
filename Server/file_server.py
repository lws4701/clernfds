'''
File Name: start_fileserver.py
Authors: CLERN Development Team
Last Modified: 3 Jul 2020
Description: This module serves as the start script for the
             CLERN file server component of the CLERN Server
'''
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from Server.tcp_server import TCPServer
from Server.archive import Archive
import os
import sys


def main():
    clern_server = TCPServer()
    ThreadPoolExecutor().submit(clern_server.listenLoop)
    parent_dir = os.getcwd()
    if not (os.path.exists("./archives")):
        os.mkdir("./archives")
    while True:
        # Actively listens for new zips
        if len(clern_server.receivedZips) > 0:
            try:
                while True:
                    archive_name = clern_server.receivedZips.pop(0)
                    frame_archive = Archive(archive_name)
                    os.chdir("./archives")
                    frame_archive.extract()
                    os.chdir(parent_dir)
                    os.remove("./%s" % frame_archive.file_name)
                    print(f"{archive_name} unzipped and archived")
                    # TODO put the motion detection logic below in the ProcessPoolExecutor
                    # so if longer than expected it doesnt get hung-up on one sequence and slow down the entire process
                    # eg.) ProcessPoolExecutor().submit(runFile, arg1, arg2)
                    ProcessPoolExecutor().submit()

            except Exception as err_type:
                print("\n***TCP SERVER %s error thrown during file transfer ***" % err_type)
                clern_server.close()
                sys.exit()


if __name__ == '__main__':
    main()
