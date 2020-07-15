'''
File Name: start_fileserver.py
Authors: CLERN Development Team
Last Modified: 3 Jul 2020
Description: This module serves as the start script for the
             CLERN file server component of the CLERN Server
'''
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import Process
from time import sleep

from Server.tcp_server import TCPServer
from Server.archive import Archive
import os
import sys


# Will not be as easy as the client side, because the listenLoop needs to be done as a process and processes cant talk
# to each other as easily.
def main():
    processes = []
    clern_server = TCPServer()

    if not (os.path.exists("./archives")):
        os.mkdir("./archives")
    # Receives and Unpacks the zips sent from client-side.
    processes.append(ProcessPoolExecutor().submit(clern_server.listenLoop))
    # Looks for new archives collected
    processes.append(ProcessPoolExecutor().submit(zipListener))

    # Shut down loop
    for process in processes:
        process.result()


def zipListener():
    pass

    """while True:
        # Actively listens for new zips
        if len(clern_server.receivedZips) > 0:
            print(clern_server.receivedZips)
            clern_server.receivedZips.pop()
            try:
                # archive_name = clern_server.receivedZips.pop(0)
                # ThreadPoolExecutor.submit(extract, archive_name, parent_dir)
                pass
                # TODO put the motion detection logic below in the ProcessPoolExecutor
                # so if longer than expected it doesnt get hung-up on one sequence and slow down the entire process
                # eg.) ProcessPoolExecutor().submit(runFile, arg1, arg2)
                # ProcessPoolExecutor().submit()

            except Exception as err_type:
                print("\n***TCP SERVER %s error thrown during file transfer ***" % err_type)
                sys.exit()"""


if __name__ == '__main__':
    main()
