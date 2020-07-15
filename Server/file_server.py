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


"""
Note to future self
Use thread to view the server current server variables
Then use that thread to call on actual processes for calculation. 
"""
def main():
    processes = []
    clern_server = TCPServer()

    if not (os.path.exists("./archives")):
        os.mkdir("./archives")
    # Looks for new archives collected
    processes.append(ThreadPoolExecutor().submit(zipListener, clern_server))
    # Receives and Unpacks the zips sent from client-side.
    #processes.append(ProcessPoolExecutor().submit(clern_server.listenLoop))
    clern_server.listenLoop()

    # Shut down loop
    for process in processes:
        process.result()

def process():
    print("Worked")

def zipListener(server):
    pass
    while True:
        sleep(5)
        print(server.receivedZips)
        ProcessPoolExecutor().submit(process)



if __name__ == '__main__':
    main()
