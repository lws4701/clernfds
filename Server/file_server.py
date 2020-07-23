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

    listener = (ThreadPoolExecutor().submit(clern_server.listen_loop))
    # Receives and Unpacks the zips sent from client-side.
    # processes.append(ProcessPoolExecutor().submit(clern_server.listenLoop))
    fall_loop(clern_server)

    # Shut down loop
    listener.result()


def listdir_nohidden(path):
    '''For listing only visible files'''
    fileList = []
    for f in os.listdir(path):
        if not f.startswith(('.')) and not (f.endswith('.zip')):
            fileList.append(f)
    return fileList


def fall_detect(packet):
    parent_dir = os.getcwd()
    frame_packet = sorted(os.listdir(f"{packet}/Frames"))
    os.chdir(f"{packet}/Frames")
    #print(frame_packet)
    frame_packets = [cv2.imread(x) for x in frame_packet]
    os.chdir(parent_dir)
    dapi = DetectorAPI(frame_packets, frame_packet)
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


def fall_loop(server):
    sub = cv2.createBackgroundSubtractorKNN(dist2Threshold=1250, history=0)

    while True:
        # There needs to be a sleep to work but it probably only needs to be only a fraction of a second.
          # You can tweak this if you want to work with a certain amount of packets of frames at once
        # NOTE server only stores a max of 10 packets of frames at once so do not have too long.
        try:
            #if len(server.open_frames) > 0:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            while cap.isOpened():
                """for packet in server.new_packets:
                    temp_packet = sorted(os.listdir(f"{packet}/Frames"))
                    os.chdir(f"{packet}/Frames")
                    # print(frame_packet)
                    temp_packets = [cv2.imread(x) for x in temp_packet]
                    frame_packet += temp_packet
                    frame_packets += temp_packets"""
                #frame = server.open_frames.pop(0)
                ret, frame = cap.read()
                #frame_name = server.frame_names.pop(0)
                #cv2.imshow("Server", frame)
                #dapi = DetectorAPI(frame, frame_name)
                #dapi.background_subtract()
                #data = dapi.get_rectangles()
                #print(data)
                back_sub = sub.apply(frame)
                contours, hierarchy = cv2.findContours(
                    back_sub, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(contour)
                box = [(x, y), ((x + w), y), (x, (y + h)), ((x + w), (y + h))]
                if box != [(0, 0), (852, 0), (0, 480), (852, 480)]:
                    print(cv2.boundingRect(contour))
                    cv2.rectangle(back_sub,
                                  (x, y), ((x+w), (y+h)), (255, 0, 0), 2)
                    #cv2.imshow('Server', frame)
                    # cv.waitKey(1000)
                    print(box)  # Returns (x, y, w, h) where
                    # (x,y) is the top left corner
                    # and the (w, h) is the width and height

                cv2.imshow("Backsub", back_sub)
                # put at end
                #os.remove(frame_name)
                if cv2.waitKey(33) == ord("q"):
                    break


                """os.chdir(parent_dir)
                dapi = DetectorAPI(frame_packets, frame_packet)
                dapi.background_subtract()
                # test_data = odapi.processPacket(frame_packet)
                test_data = dapi.get_rectangles()
                print(test_data)"""
        except Exception as e:
            print(e)
    cv2.destroyAllWindows()



if __name__ == '__main__':
    main()
