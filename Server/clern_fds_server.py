"""
clern_server.py

Authors: CLERN FDS Team

SRS cross-reference: The purpose of this file is to satisfy the functional requirement referenced in our
SRS document in section 3.1.3 (Implementing client-server communication).
In addition, background subtraction is performed here, so it is in partial fulfillment of section 3.1.4.
The remaining work to fulfill 3.1.4 are implemented in helper_functions.py

SDD cross-reference: This functionality implements the first portion of the algorithmic detail for the CLERN Image Analyzer
as well as the makes use of the TCP_Server class which implements section 3.3 (CLERN File Server)

Description: This file utilizes the tcp_server component (which implements the file server) and uses helper functions to
implement the CLERN image analyzer.
"""

# Standard Library Imports
import os
from time import sleep, time
import shutil
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
# Non Standard Library Imports
import cv2

import motion_detector, message_sender
from fall_detector import detect_fall
from helper_functions import *
from tcp_server import TCPServer


def main() -> None:
    clern_server = TCPServer()
    if not (os.path.exists("./archives")):
        os.mkdir("./archives")
    # Looks for new archives collected
    t = ThreadPoolExecutor()
    t.submit(clern_server.listen_loop)
    # Performs all detection logic on received packets.
    detection_loop(clern_server)
    # Shut down listen loop
    t.shutdown()


def detection_loop(server) -> None:
    """
    The core of clern_server. Listens for zips and calls the helper functions to act as the image analyzer
    :param server: The CLERN_Server Object
    :return: None
    """
    parent_dir = os.getcwd()
    while True:
        # NOTE server only stores a max of 10 packets of frames at once so do not have too long.
        sleep(.1)
        # If new camera index it resets the background subtractor
        if server.new_backsub:
            sub = cv2.createBackgroundSubtractorKNN(dist2Threshold=500, history=50, detectShadows=False)
            sub.setShadowThreshold(8)
            sub.setkNNSamples(2)
            server.new_backsub = False
        if len(server.new_packets) > 0:
            first = time()
            frame_paths = server.new_packets.pop(0)
            try:
                frames = load_frames(frame_paths)
                frames = [cv2.resize(x, (1280, 720)) for x in frames]
                frames = [sub.apply(frame) for frame in frames]
                frames = [cv.medianBlur(frame, 3) for frame in frames]
                rectangles = get_rectangles(frames, frame_paths)
                motion_data = motion_detector.motion_data_from_frames(rectangles)
                fall_id = detect_fall(motion_data)
                if fall_id != "":
                    message_sender.send_text_messages()
                    file_name = fall_id.partition("Frames/")[2]
                    ProcessPoolExecutor().submit(message_sender.send_image_messages, file_name, fall_id,
                                                 file_name.split('.')[2])
                    print("***Fall detected at %s***" % fall_id)
                    cv2.imshow("***FALL DETECTED***", cv2.imread(fall_id))
                    cv2.waitKey(1000)
                    cv2.destroyWindow("***FALL DETECTED***")

                print(f"{time() - first} to view packet")
            except Exception as e:
                print(f"[{e}] error in fall detection loop")
                os.chdir(parent_dir)
                pass

if __name__ == '__main__':
    main()
