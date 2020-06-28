import math

SIZE_OF_PACKET = 5
ORIGIN = (0, 0)

class Frame:
    frame_id = None
    detected_person = None

    def __init__(self, frame_id, detected_person):
        self.frame_id = frame_id
        self.detected_person = detected_person

    def person_detected(self):
        return self.detected_person is None


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
        self.length_of_diag = math.sqrt(self.width ** 2 + self.height ** 2)
        self.angle_of_diag = round(math.atan2(top_right[0] - bottom_left[0], top_right[1] - bottom_left[1]), 2)


class MotionData:
    start_frame = None
    end_frame = None
    delta_x = None
    delta_y = None
    motion_vector = (None, None)

    # unit: pixels per frame
    velocity = None

    # counterclockwise angle in radians (not degrees) between the positive X-axis
    # (or the X-axis of the start point) and the point (x, y).
    direction = None

    transform_detected = None
    translate_detected = None

    def __init__(self, start_frame, end_frame):
        start_top_left = start_frame.detected_person.top_left
        end_top_left = end_frame.detected_person.top_left
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.delta_x = abs(start_top_left[0] - end_top_left[0])
        self.delta_y = abs(start_top_left[1] - end_top_left[1])
        self.motion_vector = (end_top_left[0] - start_top_left[0], end_top_left[1] - start_top_left[1])
        self.velocity = self.calc_velocity(start_top_left, end_top_left)
        self.direction = self.calc_direction(start_top_left, end_top_left)
        self.transform_detected = (not (start_frame.detected_person.length_of_diag == end_frame.detected_person.length_of_diag) or
                                   not (start_frame.detected_person.angle_of_diag == end_frame.detected_person.angle_of_diag))
        self.translate_detected = (not (start_top_left == end_top_left) and
                                   not (start_frame.detected_person.top_right == end_frame.detected_person.top_right) and
                                   not (start_frame.detected_person.bottom_left == end_frame.detected_person.bottom_left) and
                                   not (start_frame.detected_person.bottom_right == end_frame.detected_person.bottom_right))


    def calc_velocity(self, start_point, end_point) -> float:
        start_x = start_point[0]
        start_y = start_point[1]
        end_x = end_point[0]
        end_y = end_point[1]
        sign = -1 if end_x < start_x else 1
        return sign * round(math.sqrt(abs(end_x - start_x) ** 2 + abs(end_y - start_y) ** 2) / abs(self.end_frame.frame_id - self.start_frame.frame_id), 2)

    def calc_direction(self, start_point, end_point) -> float:
        return round(math.atan2(end_point[0] - start_point[0], end_point[1] - start_point[1]), 2)


    def __str__(self):
        return '{' + '\n' \
                + '\t' + 'frames: ' + str(self.start_frame.frame_id) + '-' + str(self.end_frame.frame_id) + ',' + '\n' \
                + '\t' + 'delta_x: ' + str(self.delta_x) + ',' + '\n' \
                + '\t' + 'delta_y: ' + str(self.delta_y) + ',' + '\n' \
                + '\t' + 'motion_vector: ' + str(self.motion_vector) + '\n' \
                + '\t' + 'velocity: ' + str(self.velocity) + ' pixels/frame' + '\n' \
                + '\t' + 'direction: ' + str(self.direction) + ' radians' + '\n' \
                + '\t' + 'transform_detected: ' + str(self.transform_detected) + '\n' \
               + '\t' + 'translate_detected: ' + str(self.translate_detected) + '\n' \
               + '}'

def main():
    if __name__ == "__main__":
        test_data = [
            Frame(0, DetectedPerson((1, 2), (5, 2), (1, 8), (5, 8))),
            Frame(1, DetectedPerson((5, 2), (9, 2), (5, 8), (9, 8))),
            Frame(2, DetectedPerson((5, 2), (9, 2), (5, 8), (9, 8))),
            Frame(3, DetectedPerson((5, 4), (9, 4), (5, 8), (9, 8))),
            Frame(4, DetectedPerson((0, 6), (3, 6), (0, 12), (3, 12))),
        ]
        result = motion_data_from_frames(test_data)
        for obj in result:
            print(str(obj))


def motion_data_from_frames(list_of_frames) -> list:
    motion_data_list = []
    num_frames = len(list_of_frames)
    for i in range(1, num_frames):
        motion_data_list.append(MotionData(list_of_frames[i-1], list_of_frames[i]))
    return motion_data_list



main()

