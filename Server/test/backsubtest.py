import os

import cv2 as cv

from Server.backsub import DetectorAPI

files = os.listdir('./img1')
files = sorted([x for x in files if x.endswith('.png')])
os.chdir('img1')
framePacket = [cv.imread(x) for x in files]
timestamp = [1 * x for x in range(len(framePacket))]
dapi = DetectorAPI(framePacket, timestamp)
dapi.background_subtract()
rect = dapi.get_rectangles()
print(rect)