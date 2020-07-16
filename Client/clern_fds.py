"""
clern_fds.py
Author: Ryan Schildknecht
Camera Ready
"""

import os
import time
import cv2
from Client.archive import Archive
from Client.tcp_client import TCPClient
from Client.tkinter_gui import CLERNFDS
from concurrent.futures import ThreadPoolExecutor


def main():
    # Ensure proper directories exist
    if not(os.path.exists('Frames')):
        os.mkdir('Frames')
    # Start The ClientGUI
    gui = CLERNFDS()
    # Init the Client being used to submit files
    client = TCPClient()
    # Get the frame deliverance loop started
    transThread = ThreadPoolExecutor().submit(frameProcesses, gui, client)
    # Run the mainloop

    gui.loop()
    transThread.result()
    print("Program Closed")


def frameProcesses(gui, frameClient):
    while not gui.isRunning:
        pass
    # Frame Deliverance
    while gui.isRunning:
        print("New Index")
        index = int(gui.selectedIndex)

        cap = cv2.VideoCapture(index)
        archive_size = 5
        # doesn't work on a webcam
        cap.set(cv2.CAP_PROP_FPS, 30)

        frameCount = 0
        archiveCount = 0
        frames = []
        # open the cap (throwaway values)
        ret, frame = cap.read()
        it = time.time()
        while index == int(gui.selectedIndex) and cap.isOpened() and gui.isRunning:
            ret, frame = cap.read()
            frameCount += 1
            if frameCount % archive_size == 0:
                file_name = 'Frames/' + str(time.time()) + '.jpg'
                cv2.imwrite(file_name, frame)
                frames.append(file_name)
                print(f'{file_name} saved')
            if frameCount == archive_size * archive_size:
                archiveCount += 1
                deliver(frames, archiveCount, frameClient)
                frames.clear()
                if archiveCount == 10:
                    archiveCount = 0
                frameCount = 0
                print(f"{time.time() - it} seconds to collect and deliver archive.")
                it = time.time()
        cap.release()


def deliver(frames, count, client):
    """
    Creates an Archive of Collected Frames.
    Sends that Archive
    :param frames:
    :param client:
    :return:
    """
    img_zip = Archive(str(count) + ".zip")
    file_name = img_zip.file_name
    for frame in frames:
        img_zip.add(frame)
        print(f"{frame} added")
        # deleting files once added to zip
        if os.path.exists(frame):
            os.remove(frame)
        else:
            print(f"{frame} does not exist")
    # sending frames to server
    img_zip.close()
    client.sendFile(img_zip.file_name)
    os.remove(file_name)


if __name__ == "__main__":
    main()
