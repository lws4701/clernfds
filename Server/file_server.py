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
    processes.append(ThreadPoolExecutor().submit(zip_listener, clern_server))
    # Receives and Unpacks the zips sent from client-side.
    # processes.append(ProcessPoolExecutor().submit(clern_server.listenLoop))
    clern_server.listenLoop()

    # Shut down loop
    for process in processes:
        process.result()


def listdir_nohidden(path):
    '''For listing only visible files'''
    fileList = []
    for f in os.listdir(path):
        if not f.startswith(('.')) and not (f.endswith('.zip')):
            fileList.append(f)
    return fileList


def fall_detect(packet):
    images = sorted(listdir_nohidden(f"{packet}/Frames"))
    print(images)


def zip_listener(server):
    while True:
        # There needs to be a sleep to work but it probably only needs to be only a fraction of a second.
        sleep(5)  # You can tweak this if you want to work with a certain amount of packets of frames at once
        # NOTE server only stores a max of 10 packets of frames at once so do not have too long.
        while len(server.new_packets) > 0:
            # There will be an unavoidable delay
            print(server.new_packets)
            ProcessPoolExecutor().submit(fall_detect, server.new_packets.pop(0))


if __name__ == '__main__':
    main()
