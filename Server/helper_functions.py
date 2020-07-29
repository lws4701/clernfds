"""
helper_functions.py

SRS cross-reference: The purpose of this file is to satisfy the functional requirement referenced in our
SRS document in section 3.1.4, Locating people within a frame
In addition, background subtraction is performed here, so it is in partial fulfillment of section 3.1.4.
The remaining work to fulfill 3.1.4 are implemented in helper_functions.py

SDD cross-reference: This functionality implements the bulk of person detection in the algorithmic detail
for the CLERN Image Analyzer (Section 3.4)

Description: This file provides helper functions that implement algorithms which comprise the some core functionality of
the CLERN Image Analyzer
"""


# Non Standard Library Imports
import cv2 as cv


def get_rectangles(frame_array, name_array) -> dict:
    """
    Takes a frame array and outputs a rectangle around the largest contour in the frame.
    :param frame_array: Array of background-subtracted frames
    :param name_array: Array of the names of each frame
    :return: A dictionary of frames and corresponding boxes created around the largest contour
    """
    rectangles = dict()
    for cur_image in range(len(frame_array)):
        contours, hierarchy = cv.findContours(
            frame_array[cur_image], cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        contour = max(contours, key=cv.contourArea)
        x, y, w, h = cv.boundingRect(contour)
        box = [(x, y), ((x + w), y), (x, (y + h)), ((x + w), (y + h))]
        if box != [(0, 0), (1280, 0), (0, 720), (1280, 720)]:
            #print(cv.boundingRect(contour))
            cv.rectangle(frame_array[cur_image],
                         (x, y), ((x+w), (y+h)), (255, 0, 0), 2)
            cv.imshow('Backsub', frame_array[cur_image])
            cv.waitKey(33)
            img_name = "%s" % name_array[cur_image]
            rectangles[img_name] = box  # Returns (x, y, w, h) where
            # (x,y) is the top left corner
            # and the (w, h) is the width and height
    return rectangles

def load_frames(frame_paths) -> list:
    """
    :param frame_paths: A list of paths to individual frames
    :return: A series of frame objects in greyscale
    """
    return [cv.imread(frame, cv.IMREAD_GRAYSCALE) for frame in frame_paths]