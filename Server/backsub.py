import cv2 as cv
class DetectorAPI:
    mask = None

    def __init__(self, frame_array, timestamp_array) -> None:
        '''
        Constructor Method: Takes an array of frames. If a background mask
        does not exist, one is created from the first index in the frames.
        :param frame_array: An array of frames to analyze:
        '''
        if self.mask is None:
            self.mask = frame_array[0]
            self.frame_array = frame_array[0:]
        else:
            self.frame_array = frame_array
        self.timestamp_array = timestamp_array
        self.back_sub = cv.createBackgroundSubtractorKNN()

    def background_subtract(self) -> None:
        '''
        Creates a overwrites the frames in the frame_array with a
        background-subtracted form of the image.
        '''
        for current_frame in range(len(self.frame_array)):
            self.frame_array[current_frame] = self.back_sub.apply(self.frame_array[current_frame])
            # For viewing the background subtracted photo
            #cv.imshow(self.frame_array[current_frame])


    # def create_mhi(self) -> bytes: # May not be necessary when using Noah's motion detection module
    #     '''
    #     Creates the motion history image of a set of frames
    #     :return current_mhi: a motion history image of the set of frames
    #     '''
    #     current_mhi = self.frame_array[0]
    #     for current_frame in range(1, len(self.frame_array)):
    #         cv.motempl.updateMotionHistory(silhouette=self.frame_array[current_frame], mhi=current_mhi,
    #                                        timestamp=self.timestamp_array[current_frame], duration=0.2)
    #     return current_mhi

    def get_rectangles(self) -> dict:
        '''
        Returns rectangles approximation of foreground objects in images
        :return rectangles: a dictionary of rectangles in the frame set
        '''
        rectangles = dict()
        for cur_image in range(len(self.frame_array)):
            contours, hierarchy = cv.findContours(self.frame_array[cur_image], cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                img_name = "%s" % self.timestamp_array[cur_image]
                rectangles[img_name] = cv.boundingRect(contour) # Returns (x, y, w, h) where
                                                                # (x,y) is the top left corner
                                                                # and the (w, h) is the width and height
        return rectangles