from math import pi
from statistics import stdev
from statistics import mean
import time
import os
import cv2
from Server.motion_detector import MotionDetector
from Server.backsub import DetectorAPI

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
    vel_diff = abs(velocity - velocity_mean)
    ang_diff = abs(angle - angle_mean)
    ang_delta_diff = abs(angle_delta - angle_delta_mean)
    score += vel_diff // velocity_std
    score += ang_diff // angle_std
    score += ang_delta_diff // angle_delta_std
    return score


def detect_fall(frame_packet):
    velocity_mean = mean([x.velocity for x in frame_packet])
    velocity_std = stdev([x.velocity for x in frame_packet])
    angle_delta_mean = mean([x.diag_angle_change for x in frame_packet])
    angle_delta_std = stdev([x.diag_angle_change for x in frame_packet])
    angle_mean = mean([x.end_frame.detected_person.angle_of_diag for x in frame_packet])
    angle_std = stdev([x.end_frame.detected_person.angle_of_diag for x in frame_packet])
    score = 0
    for obj in frame_packet:
        velocity = obj.velocity
        angle = obj.end_frame.detected_person.angle_of_diag
        angle_delta = obj.diag_angle_change
        current_score = get_score(velocity, velocity_mean, velocity_std, angle, angle_mean, angle_std,
                                  angle_delta, angle_delta_mean, angle_delta_std)
        if current_score == 0:
            score = 0
        else:
            score += current_score
        if score >= 6:
            return obj.end_frame.frame_id
    return ""
# def fall_score(mean, standard_deviation):
if __name__ == "__main__":
    parent_dir = os.getcwd()
    frame_packet = sorted(os.listdir('./test/fall-30'))
    os.chdir('test/fall-30')
    frame_packet = [x for x in frame_packet if x.endswith('.png')]
    start_time = time.time()
    frame_packets = [cv2.imread(x) for x in frame_packet]
    os.chdir(parent_dir)
    dapi = DetectorAPI(frame_packets, frame_packet)
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