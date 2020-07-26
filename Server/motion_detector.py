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
    Returns: A list of MotionData objects created from the list of frames objects.
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
    data points about the rectangle including area, height, width etc. (referenced in design class
    hierarchy diagram under section 3.4.3.1)
    """

    top_left = (None, None)
    top_right = (None, None)
    bottom_left = (None, None)
    bottom_right = (None, None)
    width = None
    height = None
    center = (None, None)
    area = None
    length_of_diag = None
    angle_of_diag = None

    def __init__(self, top_left, top_right, bottom_left, bottom_right):
        self.top_left = top_left
        self.top_right = top_right
        self.bottom_left = bottom_left
        self.bottom_right = bottom_right
        self.width = abs(top_right[0] - top_left[0])
        self.height = abs(top_left[1] - bottom_left[1])
        self.center = (top_left[0] + self.width / 2, top_left[1] + self.height / 2)
        self.area = self.width * self.height

        # Pythagorean formula using width and height as the two lengths of sides of triangle
        self.length_of_diag = round(math.sqrt(self.width ** 2 + self.height ** 2), 4)

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
                + '\t' + 'area: ' + str(self.area) + ' pixels^2' + '\n' \
                + '\t' + 'length_of_diag: ' + str(self.length_of_diag) + ' pixels' + '\n' \
                + '\t' + 'angle_of_diag: ' + str(self.angle_of_diag) + ' radians' + '\n' \
                + '}'


class MotionData:
    """
    This class represents the analysis of the motion between two frame objects.
    Holds data about the motion of the center point of the bounding box along with data
    on how the box has transformed between frames such as diag_angle_change, height_change etc.
    (referenced in design class hierarchy diagram under section 3.4.3.1)
    """
    # frame to start from
    start_frame = None
    # frame to end at
    end_frame = None

    # absolute change in x
    delta_x = None                  # ------------------------------------- #
    # absolute change in y          #                                       #
    delta_y = None                  #                                       #
    motion_vector = (None, None)    #                                       #
                                    #                                       #
    # unit: pixels per frame        #   All these motion data points        #
    velocity = None                 #   describe the motion between         #
                                    #   frames of the center point          #
    # counterclockwise angle in     #   of the bounding box to sort of      #
    # radians between the positive  #   represent an overall avg of how     #
    # X-axis of the starting        #   the box changed/moved.              #
    # center point and the          #                                       #
    # end center point              #                                       #
    direction = None                # ------------------------------------- #

    # Any change in "shape" of bounding box (this will happen most of the time)
    transform_detected = None
    # A strict translation with no transformation occurring
    translate_detected = None

    # change in the angle of diagonal from start frame to end frame
    diag_angle_change = None
    # change in the length of diagonal from start frame to end frame
    diag_length_change = None

    # change in height ('+' = increased height, '-' = decreased height)
    height_change = None
    # change in width
    width_change = None

    def __init__(self, start_frame, end_frame):
        """
        This constructor function only takes in two Frame objects and calculates
        and sets all the data point parameters with help of some helper functions.
        :param start_frame: the frame object to start from
        :param end_frame: the frame object to end at
        """
        start_center = start_frame.detected_person.center
        end_center = end_frame.detected_person.center

        # The frame to start at and frame to end at
        self.start_frame = start_frame
        self.end_frame = end_frame

        # Checks for if the height or width of the rectangle has changed since this describes a transformation
        self.transform_detected = (not (start_frame.detected_person.height == end_frame.detected_person.height) or
                                   not (start_frame.detected_person.width == end_frame.detected_person.width))

        # Checks to see if a transformation has not been detected and if the center point has changed
        self.translate_detected = (not self.transform_detected and not start_center == end_center)

        # Absolute value of the difference in the center x/y
        self.delta_x = abs(end_center[0] - start_center[0])
        self.delta_y = abs(end_center[1] - start_center[1])

        # A tuple with signed integers indicating the change in x and y
        self.motion_vector = (end_center[0] - start_center[0], end_center[1] - start_center[1])

        # Basically just the length of the line formed by the start center point and end center point
        self.velocity = self.calc_velocity(start_center, end_center)

        # The Angle, measured in radians, of the line of velocity
        self.direction = self.calc_direction(start_center, end_center)

        self.diag_angle_change = round(end_frame.detected_person.angle_of_diag - start_frame.detected_person.angle_of_diag, 4)
        self.diag_length_change = round(end_frame.detected_person.length_of_diag - start_frame.detected_person.length_of_diag, 4)
        self.height_change = end_frame.detected_person.height - start_frame.detected_person.height
        self.width_change = end_frame.detected_person.width - start_frame.detected_person.width

    def calc_velocity(self, start_point, end_point) -> float:
        """
        This functions takes in a start_point and end_point and uses the pythagorean
        theorem to find the straight line distance between them on a 2D plane.
        :param start_point: Tuple of form: (x, y)
        :param end_point: Tuple of form: (x, y)
        :return: positive velocity: measured in pixels per frame
        """
        start_x = start_point[0]
        start_y = start_point[1]
        end_x = end_point[0]
        end_y = end_point[1]
        return round(math.sqrt(abs(end_x - start_x) ** 2 + abs(end_y - start_y) ** 2), 4)

    def calc_direction(self, start_point, end_point) -> float:
        """
        This functions takes in a start_point and end_point and calculates the counterclockwise angle
        by treating the start_point as the origin and then finding what angle is formed by the positive x-axis
        of that "origin"(a.k.a the start_point) and the straight line between the start_point and end_point.
        :param start_point: Tuple of form: (x, y)
        :param end_point: Tuple of form: (x, y)
        :return: direction: measured in radians
        """
        return round(math.atan2(-(end_point[1] - start_point[1]), end_point[0] - start_point[0]), 4)

    def __str__(self):
        return '{' + '\n' \
                + '\t' + 'frames: ' + str(self.start_frame.frame_id) + '-' + str(self.end_frame.frame_id) + ',' + '\n' \
                + '\t' + 'translate_detected: ' + str(self.translate_detected) + '\n' \
                + '\t' + 'delta_x: ' + str(self.delta_x) + ',' + '\n' \
                + '\t' + 'delta_y: ' + str(self.delta_y) + ',' + '\n' \
                + '\t' + 'motion_vector: ' + str(self.motion_vector) + '\n' \
                + '\t' + 'velocity: ' + str(self.velocity) + ' pixels/frame' + '\n' \
                + '\t' + 'direction: ' + str(self.direction) + ' radians' + '\n' \
                + '\t' + 'transform_detected: ' + str(self.transform_detected) + '\n' \
                + '\t' + 'diag_angle_change: ' + str(self.diag_angle_change) + ' radians' + '\n' \
                + '\t' + 'diag_length_change: ' + str(self.diag_length_change) + ' pixels' + '\n' \
                + '\t' + 'height_change: ' + str(self.height_change) + ' pixels' + '\n' \
                + '\t' + 'width_change: ' + str(self.width_change) + ' pixels' + '\n' \
                + '}'
