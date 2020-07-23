import cv2 as cv


class DetectorAPI:
    def __init__(self, frame_array, timestamp_array, image_mask="./archives/mask.jpg") -> None:
        '''
        Constructor Method: Takes an array of frames. If a background mask
        does not exist, one is created from the first index in the frames.
        :param frame_array: An array of frames to analyze:
        '''
        if image_mask is None:
            self.mask = frame_array[0]
            self.frame_array = frame_array[0:]
        else:
            self.mask = image_mask
        self.frame_array = frame_array
        self.timestamp_array = timestamp_array
        self.back_sub = cv.createBackgroundSubtractorKNN(dist2Threshold=1250)

    def background_subtract(self) -> None:
        '''
        Creates a overwrites the frames in the frame_array with a
        background-subtracted form of the image.
        '''
        for current_frame in range(len(self.frame_array)):
            self.frame_array[current_frame] = self.back_sub.apply(
                self.frame_array[current_frame])
            # For viewing the background subtracted photo
            # cv.imshow('Backsub', self.frame_array[current_frame])
            # cv.waitKey(30)

    def get_rectangles(self) -> dict:
        '''
        Returns rectangles approximation of foreground objects in images
        :return rectangles: a dictionary of rectangles in the frame set
        '''
        rectangles = dict()
        for cur_image in range(len(self.frame_array)):
            contours, hierarchy = cv.findContours(
                self.frame_array[cur_image], cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            contour = max(contours, key=cv.contourArea)
            x, y, w, h = cv.boundingRect(contour)
            box = [(x, y), ((x+w), y), (x, (y+h)), ((x+w), (y+h))]
            if box != [(0, 0), (640, 0), (0, 480), (640, 480)]:
                # print(cv.boundingRect(contour))
                # cv.rectangle(self.frame_array[cur_image],
                #              (x, y), ((x+w), (y+h)), (255, 0, 0), 2)
                # cv.imshow('Backsub', self.frame_array[cur_image])
                # cv.waitKey(1000)
                img_name = "%s" % self.timestamp_array[cur_image]
                rectangles[img_name] = box  # Returns (x, y, w, h) where
                # (x,y) is the top left corner
                # and the (w, h) is the width and height
        return rectangles

    def set_frame_array(self, frame_array):
        self.frame_array = frame_array

    def set_timestamp_array(self, timestamp_array):
        self.timestamp_array = timestamp_array