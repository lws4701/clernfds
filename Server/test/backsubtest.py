import os

import cv2 as cv

from Server.backsub import DetectorAPI

files = os.listdir('./img1')
parent_dir = os.getcwd()
files = sorted([x for x in files if x.endswith('.png')])
os.chdir('img1')
framePacket = [cv.imread(x) for x in files]
os.chdir(parent_dir)
timestamp = [1 * x for x in range(len(framePacket))]
print(cv.imread('mask.png'))
dapi = DetectorAPI(framePacket, timestamp, cv.imread('mask.png'))
dapi.background_subtract()
rect = dapi.get_rectangles()
print(rect)