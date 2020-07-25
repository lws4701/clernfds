import os

import cv2 as cv

from Server.oldcode.backsub import DetectorAPI

files = os.listdir('./img1')
parent_dir = os.getcwd()
files = sorted([x for x in files if x.endswith('.png')])
os.chdir('img1')
frame_packet = [cv.imread(x) for x in files]
os.chdir(parent_dir)
timestamp = [x for x in range(len(frame_packet))]
dapi = DetectorAPI(frame_packet, timestamp, cv.imread('mask.png'))
dapi.background_subtract()
rect = dapi.get_rectangles()
print(rect)
