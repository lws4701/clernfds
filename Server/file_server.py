'''
File Name: start_fileserver.py
Authors: CLERN Development Team
Last Modified: 3 Jul 2020
Description: This module serves as the start script for the
             CLERN file server component of the CLERN Server
'''
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from time import sleep, time

import cv2

from Server.fall_detector import detect_fall
from Server.backsub import DetectorAPI
from Server.motion_detector import MotionDetector
from Server.tcp_server import TCPServer

import os
import sys

"""
Note to future self
Use thread to view the server current server variables
Then use that thread to call on actual processes for calculation. 
"""


def main():
    clern_server = TCPServer()
    if not (os.path.exists("./archives")):
        os.mkdir("./archives")
    # Looks for new archives collected
    t = ThreadPoolExecutor()
    t.submit(clern_server.listen_loop)
    # Receives and Unpacks the zips sent from client-side.
    zip_listener(clern_server)


    # Shut down loop
    t.shutdown()


def listdir_nohidden(path):
    '''For listing only visible files'''
    fileList = []
    for f in os.listdir(path):
        if not f.startswith(('.')) and not (f.endswith('.zip')):
            fileList.append(f)
    return fileList


"""def fall_detect(packet):
    parent_dir = os.getcwd()
    frame_packets = [cv2.imread(x) for x in packet]
    os.chdir(parent_dir)
    dapi = DetectorAPI(frame_packets, packet)
    dapi.background_subtract()
    # test_data = odapi.processPacket(frame_packet)
    test_data = dapi.get_rectangles()
    print(test_data)
    # print(test_data)
    motion_detector = MotionDetector(test_data)
    result = motion_detector.motion_data_from_frames()
    frames = motion_detector.get_frame_objects()
    fall_id = detect_fall(result)
    if fall_id != "":
        print(f"***Fall happened at {fall_id}***")
        # For deciding if accurate analysis or not.
        img = cv2.imread(f"{packet}/Frames/{fall_id}", 0)
        cv2.imshow("Fall", img)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()
"""


def zip_listener(server):
    p = ProcessPoolExecutor()
    sub = cv2.createBackgroundSubtractorKNN(dist2Threshold=550, detectShadows=False, history=50)
    while True:
        # NOTE server only stores a max of 10 packets of frames at once so do not have too long.
        sleep(.1)
        if len(server.new_packets) > 0:
            first =time()
            frames = server.new_packets.pop(0)
            rectangles = {}
            for path in frames:
                frame = cv2.imread(path)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                sub_frame = sub.apply(frame)
                sub_frame = cv2.medianBlur(sub_frame, 5)
                contours, hierarchy = cv2.findContours(
                    sub_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(contour)
                box = [(x, y), ((x + w), y), (x, (y + h)), ((x + w), (y + h))]
                if box != [(0, 0), (1280, 0), (0, 720), (1280, 720)]:
                    #print(cv2.boundingRect(contour))
                    cv2.rectangle(sub_frame,
                                 (x, y), ((x+w), (y+h)), (255, 0, 0), 2)
                    cv2.imshow('BackSub', sub_frame)
                    cv2.waitKey(33)
                    print(box)
                # test_data = odapi.processPacket(frame_packet)
                    rectangles[path] = box
                #print(test_data)

                # For deciding if accurate analysis or not.
            # There will be an unavoidable delay
            #print(server.new_packets.pop(0))

            #fall_detect(server.new_packets.pop(0))
            print(f"{time() - first} to view packet")


if __name__ == '__main__':
    main()
