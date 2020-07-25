"""
[insert file description]
"""

import numpy as np


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
        angle_chang = obj.diag_angle_change
        current_score = get_score(velocity, vel_mean, vel_std, angle, angle_mean, angle_std,
                                  angle_chang, angle_chang_mean, angle_chang_std)
        if current_score == 1:
            score = 0
        else:
            score += current_score
        if score >= 12:
            return obj.end_frame.frame_id
    return ""
