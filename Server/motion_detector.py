import math


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

    def __init__(self, start_frame, end_frame, delta_x, delta_y, motion_vector, velocity, direction):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.motion_vector = motion_vector
        self.velocity = velocity
        self.direction = direction

    def __str__(self):
        return '{' + '\n' \
                + '\t' + 'frames: ' + str(self.start_frame) + '-' + str(self.end_frame) + ',' + '\n' \
                + '\t' + 'delta_x: ' + str(self.delta_x) + ',' + '\n' \
                + '\t' + 'delta_y: ' + str(self.delta_y) + ',' + '\n' \
                + '\t' + 'motion_vector: ' + str(self.motion_vector) + '\n' \
                + '\t' + 'velocity: ' + str(self.velocity) + ' pixels/frame' + '\n' \
                + '\t' + 'direction: ' + str(self.direction) + ' radians' + '\n' \
                + '}'

def main():
    if __name__ == "__main__":
        test_data = [(3, 7), (6, 9), (6, 9), (7, 3), (4, 3)]
        result = []
        for i in range(1, len(test_data)):
            prev_frame = test_data[i - 1]
            cur_frame = test_data[i]
            motion_data = MotionData(
                i - 1,
                i,
                abs(cur_frame[0] - prev_frame[0]),
                abs(cur_frame[1] - prev_frame[1]),
                (cur_frame[0] - prev_frame[0], cur_frame[1] - prev_frame[1]),
                calc_velocity(prev_frame, cur_frame, 1),
                calc_direction(prev_frame, cur_frame)
            )
            result.append(motion_data)
        for obj in result:
            print(str(obj))


def calc_velocity(start_point, end_point, num_frames):
    start_x = start_point[0]
    start_y = start_point[1]
    end_x = end_point[0]
    end_y = end_point[1]
    sign = -1 if end_x < start_x else 1
    return sign * round(math.sqrt(abs(end_x - start_x) ** 2 + abs(end_y - start_y) ** 2) / num_frames, 2)


def calc_direction(start_point, end_point):
    return round(math.atan2(end_point[0] - start_point[0], end_point[1] - start_point[1]), 2)


main()

