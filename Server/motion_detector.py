import math
import os
import cv2
from Server.backsub import DetectorAPI


class MotionDetector:

    frames = list()

    def __init__(self, dict_of_frames):
        for key in dict_of_frames:
            self.frames.append(Frame(key, DetectedPerson(*dict_of_frames[key][0])))

    def motionDataFromFrames(self) -> list:
        motion_data_list = []
        for i in range(1, len(self.frames)):
            motion_data_list.append(MotionData(self.frames[i - 1], self.frames[i]))
        return motion_data_list

    def getFrameObjects(self):
        return self.frames


class Frame:
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
    top_left = (None, None)
    top_right = (None, None)
    bottom_left = (None, None)
    bottom_right = (None, None)
    width = None
    height = None
    center = (None, None)
    area = None
    length_of_diag = None

    # angle from the bottom of rectangle to the diag
    # that goes from bottom left to top right (radians)
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
        self.length_of_diag = round(math.sqrt(self.width ** 2 + self.height ** 2), 4)
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
    start_frame = None
    end_frame = None

    delta_x = None                  # ------------------------------------- #
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

    transform_detected = None       # Any change in "shape" of bounding box (this will happen most of the time)
    translate_detected = None       # A strict translation with no transformation occurring

    diag_angle_change = None
    diag_length_change = None

    height_change = None
    width_change = None

    def __init__(self, start_frame, end_frame):
        start_top_left = start_frame.detected_person.top_left
        end_top_left = end_frame.detected_person.top_left
        start_center = start_frame.detected_person.center
        end_center = end_frame.detected_person.center
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.transform_detected = (not (start_frame.detected_person.length_of_diag == end_frame.detected_person.length_of_diag) or
                                   not (start_frame.detected_person.angle_of_diag == end_frame.detected_person.angle_of_diag))

        motion_vector = (end_center[0] - start_center[0], end_center[1] - start_center[1])
        self.translate_detected = (not self.transform_detected and not motion_vector == (0, 0) and self.calcMotionVector(start_top_left, end_top_left) == motion_vector and
                                   self.calcMotionVector(start_frame.detected_person.top_right, end_frame.detected_person.top_right) == motion_vector and
                                   self.calcMotionVector(start_frame.detected_person.bottom_left, end_frame.detected_person.bottom_left) == motion_vector and
                                   self.calcMotionVector(start_frame.detected_person.bottom_right, end_frame.detected_person.bottom_right) == motion_vector)

        self.delta_x = abs(end_center[0] - start_center[0])
        self.delta_y = abs(end_center[1] - start_center[1])
        self.motion_vector = motion_vector
        self.velocity = self.calcVelocity(start_center, end_center)
        self.direction = self.calcDirection(start_center, end_center)

        if self.transform_detected:
            self.diag_angle_change = round(end_frame.detected_person.angle_of_diag - start_frame.detected_person.angle_of_diag, 4)
            self.diag_length_change = round(end_frame.detected_person.length_of_diag - start_frame.detected_person.length_of_diag, 4)
            self.height_change = end_frame.detected_person.height - start_frame.detected_person.height
            self.width_change = end_frame.detected_person.width - start_frame.detected_person.width

    def calcVelocity(self, start_point, end_point) -> float:
        start_x = start_point[0]
        start_y = start_point[1]
        end_x = end_point[0]
        end_y = end_point[1]
        sign = -1 if end_x < start_x else 1
        return sign * round(math.sqrt(abs(end_x - start_x) ** 2 + abs(end_y - start_y) ** 2) / 1, 4)

    def calcDirection(self, start_point, end_point) -> float:
        return round(math.atan2(end_point[1] - start_point[1], end_point[0] - start_point[0]), 4)

    def calcMotionVector(self, start_point, end_point) -> tuple:
        return end_point[0] - start_point[0], end_point[1] - start_point[1]

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


def main():
    if __name__ == "__main__":

        # model_path = 'test/faster_rcnn_inception_v2_coco/frozen_inference_graph.pb'
        # odapi = DetectorAPI(path_to_ckpt=model_path)
        parent_dir = os.getcwd()
        frame_packet = sorted(os.listdir('./test/img1'))
        os.chdir('test/img1')
        frame_packet = [x for x in frame_packet if x.endswith('.png')]
        frame_packet = [cv2.imread(x) for x in frame_packet]
        os.chdir(parent_dir)
        dapi = DetectorAPI(frame_packet, [0.2 * x for x in range(len(frame_packet))])
        dapi.background_subtract()
        # test_data = odapi.processPacket(frame_packet)
        test_data = dapi.get_rectangles()
        motion_detector = MotionDetector(test_data)
        result = motion_detector.motionDataFromFrames()
        frames = motion_detector.getFrameObjects()
        for obj in result:
            print(str(obj))
        for obj in frames:
            print(str(obj))



main()

