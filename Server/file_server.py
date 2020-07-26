"""
clern_server.py

SRS cross-reference: The purpose of this file is to satisfy the non-functional requirement referenced in our
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
# Custom Imports
from Server.fall_detector import detect_fall
from Server.helper_functions import *
from Server.motion_detector import MotionDetector
from Server.tcp_server import TCPServer



def main() -> None:
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


def listdir_nohidden(path) -> list:
    """
    Lists the files in a directoy, not including hidden (dotfiles) as well as zip files
    :param path: The path of to be listed
    :return: A sorted list of files in a directory
    """
    fileList = []
    for f in sorted(os.listdir(path)):
        if not f.startswith(('.')) and not (f.endswith('.zip')):
            fileList.append(f)
    return fileList

def zip_listener(server) -> None:
    """
    The core of clern_server. Listens for zips and calls the helper functions to act as the image analyzer
    :param server: The CLERN_Server Object
    :return: None
    """
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
                    first = time()
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