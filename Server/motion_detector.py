"""
motion_detector.py

SRS cross-reference: The purpose of this file is to satisfy the functional requirement referenced in our
SRS document in section 3.1.5.

SDD cross-reference: This is code for the first responsibility of the CLERN Image Analyzer component
described in section 3.4.1 (first bullet point), instantiates the design class hierarchy diagram under section
3.4.3.1 and also is the implementation of the processing narrative and algorithmic detail under section 3.4.3.5
(second bullet points under heading 1 and 2).

Description: This file creates a structure for analysing a sequence of frames
and generating data about the motion of objects between those frames.
"""
import math


def motion_data_from_frames(dict_of_frames) -> list:
    """
    Loops through the list of frames and uses each adjacent pair and inputs them
    into the MotionData objects constructor.
    :returns motion_data_list: list of MotionData objects
    """
    frames = []
    for key in dict_of_frames:
        frames.append(Frame(key, DetectedPerson(*dict_of_frames[key])))

    motion_data_list = []
    for i in range(1, len(frames)):
        motion_data_list.append(MotionData(frames[i - 1], frames[i]))
    return motion_data_list



class Frame:
    """
    This class represents a frame/image that contains a foreground object that
    has been detected within the frame. It holds a frame_id to uniquely identifies
    the frame and then the detected_person which will hold an array of coordinates
    to represented the bounding box of the detected object. (referenced in design
    class hierarchy diagram under section 3.4.3.1)
    """

    frame_id = None
    detected_person = None

    def __init__(self, frame_id, detected_person):
        self.frame_id = frame_id
        self.detected_person = detected_person

    def person_detected(self):
        return self.detected_person is None

    def __str__(self):
        return '{' + '\n' \
                + '\t' + 'frame_id: ' + str(self.frame_id) + '\n' \
                + '\t' + 'detected_person: ' + str(self.detected_person) + '\n' \
                + '}'


class DetectedPerson:
    """
    This class represents a foreground object that has been detected within a frame. It holds
    member variables for the four corners of the bounding box around this detected object. Along
    data points about the rectangle including center, height, width etc. (referenced in design class
    hierarchy diagram under section 3.4.3.1)
    """

    top_left = (None, None)
    top_right = (None, None)
    bottom_left = (None, None)
    bottom_right = (None, None)
    width = None
    height = None
    center = (None, None)
    angle_of_diag = None

    def __init__(self, top_left, top_right, bottom_left, bottom_right):
        self.top_left = top_left
        self.top_right = top_right
        self.bottom_left = bottom_left
        self.bottom_right = bottom_right
        self.width = abs(top_right[0] - top_left[0])
        self.height = abs(top_left[1] - bottom_left[1])
        self.center = (top_left[0] + self.width / 2, top_left[1] + self.height / 2)

        # Arc-tan of opposite (height) over adjacent (width). This is the angle formed between the
        # diagonal running from bottom left corner to top right and the bottom edge of the rectangle
        self.angle_of_diag = round(math.atan2(self.height, self.width), 4)

    def __str__(self):
        return '{' + '\n' \
                + '\t' + 'top_left: ' + str(self.top_left) + ',' + '\n' \
                + '\t' + 'top_right: ' + str(self.top_right) + '\n' \
                + '\t' + 'bottom_left: ' + str(self.bottom_left) + ',' + '\n' \
                + '\t' + 'bottom_right: ' + str(self.bottom_right) + ',' + '\n' \
                + '\t' + 'width: ' + str(self.width) + ' pixels' + '\n' \
                + '\t' + 'height: ' + str(self.height) + ' pixels' + '\n' \
                + '\t' + 'center: ' + str(self.center) + '\n' \
                + '\t' + 'angle_of_diag: ' + str(self.angle_of_diag) + ' radians' + '\n' \
                + '}'


class MotionData:
    """
    This class represents the analysis of the motion between two frame objects.
    Holds data about the motion of the center point of the bounding box along with data
    on how the box has transformed between frames such as diag_angle_change, velocity etc.
    (referenced in design class hierarchy diagram under section 3.4.3.1)
    """

    # frame to start from
    start_frame = None

    # frame to end at
    end_frame = None

    # Change in x and y of center points between frames
    motion_vector = (None, None)

    # unit: pixels per frame
    velocity = None

    # change in the angle of diagonal from start frame to end frame
    diag_angle_change = None


    def __init__(self, start_frame, end_frame):
        """
        This constructor function only takes in two Frame objects and calculates
        and sets all the data point parameters.
        :param start_frame: the frame object to start from
        :param end_frame: the frame object to end at
        """
        start_center = start_frame.detected_person.center
        end_center = end_frame.detected_person.center

        # The frame to start at and frame to end at
        self.start_frame = start_frame
        self.end_frame = end_frame

        # A tuple with signed integers indicating the change in x and y
        self.motion_vector = (end_center[0] - start_center[0], end_center[1] - start_center[1])

        # Basically just the length of the line formed by the start center point and end center point
        self.velocity = round(math.sqrt(abs(end_center[0] - start_center[0]) ** 2 + abs(end_center[1] - start_center[1]) ** 2), 4)

        # Change in the angle of the diag from start_frame to end_frame
        self.diag_angle_change = round(end_frame.detected_person.angle_of_diag - start_frame.detected_person.angle_of_diag, 4)


    def __str__(self):
        return '{' + '\n' \
                + '\t' + 'frames: ' + str(self.start_frame.frame_id) + '-' + str(self.end_frame.frame_id) + ',' + '\n' \
                + '\t' + 'motion_vector: ' + str(self.motion_vector) + '\n' \
                + '\t' + 'velocity: ' + str(self.velocity) + ' pixels/frame' + '\n' \
                + '\t' + 'diag_angle_change: ' + str(self.diag_angle_change) + ' radians' + '\n' \
                + '}'
