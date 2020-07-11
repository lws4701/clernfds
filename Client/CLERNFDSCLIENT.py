"""
CLERNFDSCLIENT.py
Author
Camera Ready
Alter this and tkinter_gui.py as Necessary to run testfiles.
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
        frame_rate = 5

        # TODO replace when camera is accessible
        #cap = cv2.VideoCapture("test/test.mp4")
        # For when webcam is available
        cap = cv2.VideoCapture(index)
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
            if frameCount % 5 == 1:
                filename = 'Frames/' + str(time.time()) + '.jpg'
                cv2.imwrite(filename, frame)
                frames.append(filename)
                print(f'{filename} saved')
            if frameCount == 25:
                archiveCount += 1
                deliver(frames, archiveCount, frameClient)
                frames.clear()
                frameCount = 0
                print(f"{time.time() - it} seconds to collect and deliver archive.")
                it = time.time()
            # THIS IS FOR TEST DATA ONLY NOT WEBCAM USAGE TODO comment out when using webcam
            #time.sleep(.033)  # time between frames in 30 fps for when putting in a mp4
        cap.release()


def deliver(frames, count, client):
    """
    Creates an Archive of Collected Frames.
    Sends that Archive
    :param frames:
    :param client:
    :return:
    """
    imgZip = Archive(str(count) + ".zip")
    for frame in frames:
        imgZip.add(frame)
        print(f"{frame} added")
        # deleting files once added to zip
        if os.path.exists(frame):
            os.remove(frame)
        else:
            print(f"{frame} does not exist")
    # sending frames to server
    imgZip.close()
    client.sendFile(imgZip.fileName)


if __name__ == "__main__":
    main()
