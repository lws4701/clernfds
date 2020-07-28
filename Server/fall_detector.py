"""
fall_detector.py

SRS cross-reference: The purpose of this file is to satisfy the functional requirement referenced in our
SRS document in section 3.1.6.

SDD cross-reference: This is code for the second responsibility of the CLERN Image Analyzer component (Fall Detection
described in section 3.4.1 (second bullet point) and implements the algorithmic detail for detecting a fall in this section.

Description: This file implements CLERN's fall detection algorithm
"""

# Non Standard Library Imports
import numpy as np


def get_score(velocity, velocity_mean, velocity_std,
              angle, angle_mean, angle_std,
              angle_chang, angle_chang_mean, angle_chang_std, chang_in_y) -> int:
    """
    Calculates a fall likelihood score based on the statistical values of the velocity, angle, and change in the angle.
    :param velocity: Individual velocity value of the frame
    :param velocity_mean: Mean of velocity across all sampled frames
    :param velocity_std: Standard deviation of the velocity of all sampled frames
    :param angle: Individual angle value at the ending frame of each motion data object
    :param angle_mean: Mean of angles across all sampled frames
    :param angle_std: Standard deviation of the angle of the diagonal of the box in each motion data object
    :param angle_chang: Change in the angle for the calculated frame object.
    :param angle_chang_mean: Mean of the change in the angle for all sampled frames
    :param angle_chang_std: Standard deviation of the change in angle for all sampled frames
    :param chang_in_y: The chang in y from start frame to end frame
    :return: A fall likelihood score
    """
    score = 0
    vel_diff = np.abs(velocity - velocity_mean).item(0)
    ang_diff = np.abs(angle - angle_mean).item(0)
    ang_delta_diff = np.abs(angle_chang - angle_chang_mean).item(0)
    if 50 < chang_in_y < 100:
        score += vel_diff // velocity_std
    score += ang_diff // angle_std
    score += ang_delta_diff // angle_chang_std
    return score


def detect_fall(frame_packet) -> str:
    """
    :param frame_packet: Packet of frames for analysis
    :return: String corresponding to the fall frame for the detected fall
    """
    # Get motion data from frame_packet
    velocities = [frame.velocity for frame in frame_packet]
    angle_chang = [frame.diag_angle_change for frame in frame_packet]
    angle = [frame.end_frame.detected_person.angle_of_diag for frame in frame_packet]
    # Perform statistical calculations on motion data.
    vel_std = np.std(velocities)
    vel_mean = np.mean(velocities)
    angle_chang_std = np.std(angle_chang)
    angle_chang_mean = np.mean(angle_chang)
    angle_std = np.std(angle)
    angle_mean = np.mean(angle)
    # Loop through packet, perform calculations on individual frames
    score = 0 # Set counter
    for obj in frame_packet:
        velocity = obj.velocity
        angle = obj.end_frame.detected_person.angle_of_diag
        angle_chang = obj.diag_angle_change
        chang_in_y = obj.motion_vector[1]
        current_score = get_score(velocity, vel_mean, vel_std, angle, angle_mean, angle_std,
                                  angle_chang, angle_chang_mean, angle_chang_std, chang_in_y)
        # If there's nothing out of the ordinary, reset the frame score
        if current_score == 0:
            score = 0
        # Otherwise add current score to the counter to check against the threshold
        else:
            score += current_score
        if score >= 12:
            return obj.end_frame.frame_id
    return ""
