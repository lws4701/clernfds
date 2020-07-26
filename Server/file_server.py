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
import shutil
import cv2

from Server.fall_detector import detect_fall
from Server.helper_functions import *
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
"""


def zip_listener(server):
    p = ProcessPoolExecutor()
    parent_dir = os.getcwd()
    while True:
        # NOTE server only stores a max of 10 packets of frames at once so do not have too long.
        sleep(.1)
        if server.new_backsub:
            sub = cv2.createBackgroundSubtractorKNN(dist2Threshold=500, history=50, detectShadows=False)
            sub.setShadowThreshold(8)
            sub.setkNNSamples(2)
            server.new_backsub = False
            #mask = "mask.jpg"
            for i in range(1, 11):
                try:
                    os.chdir("./archives/%s/Frames" % i)
                    frame_paths = listdir_nohidden(".")
                    frames = load_frames(frame_paths)
                    frames = [sub.apply(frame) for frame in frames]
                    frames = [cv.medianBlur(frame, 3) for frame in frames]
                    rectangles = get_rectangles(frames, frame_paths)
                    motion_detector = MotionDetector(rectangles)
                    motion_data = motion_detector.motion_data_from_frames()
                    fall_id = detect_fall(motion_data)
                    if fall_id != "":
                        print("Fall detected at Packet %s, Frame %s" % (os.getcwd(), fall_id))
                    print(f"{time() - first} to view packet")
                    os.chdir(parent_dir)
                    shutil.rmtree("./archives/%s")
                    frame_paths.clear()
                except:
                    os.chdir(parent_dir)
                    pass


if __name__ == '__main__':
    main()