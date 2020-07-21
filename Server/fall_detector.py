from math import pi


def get_fall_score(motion_data) -> int:
    score = 0
    diag_angle_delta = motion_data.diag_angle_change
    diag_magnitude_delta = motion_data.diag_length_change
    if diag_angle_delta >= pi/4:
        score += 5
    if diag_magnitude_delta >= 20:
        score += 5

    angle = abs(motion_data.end_frame.detected_person.angle_of_diag)
    if angle < pi / 4:
        if angle < pi / 12:
            score += 5
        else:
            score += 3

    velocity = motion_data.velocity
    if velocity >= 50:
        score += 5
    if velocity <= 10:
        score += 2

    return score