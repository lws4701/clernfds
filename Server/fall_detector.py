from math import pi
import time
import os
import cv2
from Server.motion_detector import MotionDetector
from Server.backsub import DetectorAPI
import numpy as np

# def get_fall_score(motion_data) -> int:
#     score = 0
#     diag_angle_delta = motion_data.diag_angle_change
#     diag_magnitude_delta = motion_data.diag_length_change
#     if diag_angle_delta >= pi/4:
#         score += 5
#     if diag_magnitude_delta >= 20:
#         score += 5
#
#     angle = abs(motion_data.end_frame.detected_person.angle_of_diag)
#     if angle < pi / 4:
#         if angle < pi / 12:
#             score += 5
#         else:
#             score += 3
#
#     velocity = motion_data.velocity
#     if velocity >= 50:
#         score += 5
#     if velocity <= 10:
#         score += 2
#
#     return score
# def detect_fall(frame_packet):


def get_score(velocity, velocity_mean, velocity_std,
              angle, angle_mean, angle_std,
              angle_delta, angle_delta_mean, angle_delta_std) -> int:
    score = 0
    vel_diff = np.abs(velocity - velocity_mean).item(0)
    ang_diff = np.abs(angle - angle_mean).item(0)
    ang_delta_diff = np.abs(angle_delta - angle_delta_mean).item(0)
    score += vel_diff // velocity_std
    score += ang_diff // angle_std
    score += ang_delta_diff // angle_delta_std
    return score


def detect_fall(frame_packet):
    velocities = [frame.velocity for frame in frame_packet]
    angle_chang = [frame.diag_angle_change for frame in frame_packet]
    angle = [frame.end_frame.detected_person.angle_of_diag for frame in frame_packet]
    vel_std = np.std(velocities)
    vel_mean = np.mean(velocities)
    angle_chang_std = np.std(angle_chang)
    angle_chang_mean = np.std(angle_chang)
    angle_std = np.std(angle)
    angle_mean = np.mean(angle)
    score = 0
    for obj in frame_packet:
        velocity = obj.velocity
        angle = obj.end_frame.detected_person.angle_of_diag
        angle_delta = obj.diag_angle_change
        current_score = get_score(velocity, vel_mean, vel_std, angle, angle_mean, angle_std,
                                  angle_chang, angle_chang_mean, angle_chang_std)
        if current_score == 1:
            score = 0
        else:
            score += current_score
        if score >= 12:
            return obj.end_frame.frame_id
    return ""
# def fall_score(mean, standard_deviation):
if __name__ == "__main__":
    parent_dir = os.getcwd()
    test_images = parent_dir + '/test/img/fall-01'
    frame_packet = sorted(os.listdir(test_images))
    os.chdir(test_images)
    frame_packets = [x for x in frame_packet if x.endswith('.png')]
    start_time = time.time()
    frame_packetss = [cv2.imread(x) for x in frame_packet]
    os.chdir(parent_dir)
    dapi = DetectorAPI(frame_packetss, frame_packets, cv2.imread('./test/mask.png'))
    dapi.background_subtract()
    # test_data = odapi.processPacket(frame_packet)
    test_data = dapi.get_rectangles()
    # print(test_data)
    motion_detector = MotionDetector(test_data)
    result = motion_detector.motion_data_from_frames()
    frames = motion_detector.get_frame_objects()
    fall_id = detect_fall(result)
    if fall_id != '':
        print(f"Fall at {fall_id}")
    # for obj in frames:
    end_time = time.time()
    print(end_time - start_time)