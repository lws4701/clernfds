"""
File Name: file_server.py
Authors: CLERN Development Team
Last Modified: 3 Jul 2020
Description: This module serves as the start script for the
             CLERN file server component of the CLERN Server
"""

from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from time import sleep
import cv2
from Server.fall_detector import detect_fall
from Server.oldcode.backsub import DetectorAPI
from Server.motion_detector import MotionDetector
from Server.tcp_server import TCPServer
import os


def main():
    clern_server = TCPServer()
    if not (os.path.exists("./archives")):
        os.mkdir("./archives")
    # Looks for new archives collected
    listener = (ThreadPoolExecutor().submit(zip_listener, clern_server))
    # Receives and Unpacks the zips sent from client-side.
    # processes.append(ProcessPoolExecutor().submit(clern_server.listenLoop))
    clern_server.listen_loop()

    # Shut down loop
    listener.result()


def listdir_nohidden(path):
    """For listing only visible files"""
    file_list = []
    for f in os.listdir(path):
        if not f.startswith('.') and not (f.endswith('.zip')):
            file_list.append(f)
    return file_list


def fall_detect(packet):
    parent_dir = os.getcwd()
    frame_packet = sorted(os.listdir(f"{packet}/Frames"))
    os.chdir(f"{packet}/Frames")
    print(frame_packet)
    frames = [cv2.imread(x) for x in frame_packet]
    os.chdir(parent_dir)
    dapi = DetectorAPI(frames, frame_packet)
    dapi.background_subtract()
    test_data = dapi.get_rectangles()
    print(test_data)
    motion_detector = MotionDetector(test_data)
    result = motion_detector.motion_data_from_frames()
    fall_id = detect_fall(result)
    if fall_id != "":
        print(f"***Fall happened at {fall_id}***")
        # For deciding if accurate analysis or not.
        img = cv2.imread(f"{packet}/Frames/{fall_id}", 0)
        cv2.imshow("Fall", img)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()


def zip_listener(server):
    while True:
        # There needs to be a sleep to work but it probably only needs to be only a fraction of a second.
        sleep(.5)  # You can tweak this if you want to work with a certain amount of packets of frames at once
        # NOTE server only stores a max of 10 packets of frames at once so do not have too long.
        while len(server.new_packets) > 0:
            # There will be an unavoidable delay
            print(server.new_packets)
            ProcessPoolExecutor().submit(fall_detect, server.new_packets.pop(0))


if __name__ == '__main__':
    main()
