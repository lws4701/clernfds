# Code adapted from Tensorflow Object Detection Framework
# https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb
# Tensorflow Object Detection Detector

import time
import os
import cv2
import numpy as np
import tensorflow as tf


class DetectorAPI:
    def __init__(self, path_to_ckpt):
        self.path_to_ckpt = path_to_ckpt

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.compat.v1.gfile.GFile(self.path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        self.default_graph = self.detection_graph.as_default()
        self.sess = tf.compat.v1.Session(graph=self.detection_graph)

        # Definite input and output Tensors for detection_graph
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

    def processFrame(self, image):
        # Expand dimensions since the trained_model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image, axis=0)
        # Actual detection.
        start_time = time.time()
        (frame_boxes, frame_scores, frame_classes, frame_num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})


        im_height, im_width, _ = image.shape
        boxes_list = [None for i in range(frame_boxes.shape[1])]
        for i in range(frame_boxes.shape[1]):
            boxes_list[i] = (int(frame_boxes[0, i, 0] * im_height),
                        int(frame_boxes[0, i, 1]*im_width),
                        int(frame_boxes[0, i, 2] * im_height),
                        int(frame_boxes[0, i, 3]*im_width))

        scores = frame_scores[0].tolist()
        classes = [int(x) for x in frame_classes[0].tolist()]
        box_coords = []

        for i in range(len(boxes_list)):
            # Class 1 represents human
            if classes[i] == 1 and scores[i] > threshold:
                box = boxes_list[i]
                cv2.rectangle(image, (box[1], box[0]), (box[3], box[2]), (255, 0, 0), 2)
                box_coords.append([(box[1], box[0]), (box[3], box[0]), (box[1], box[2]), (box[3], box[2])])

        end_time = time.time()
        print("Elapsed Time:", end_time - start_time)
        return box_coords

        #return boxes_list, frame_scores[0].tolist(), [int(x) for x in frame_classes[0].tolist()], int(frame_num[0])

    def processPacket(self, packet):
        box_dict = {}

        for frame in packet:
            frame_path = 'archives/' + frame
            cap = cv2.VideoCapture(frame_path)
            r, image = cap.read()
            img = cv2.resize(image, (640, 480))
            coords = self.processFrame(img)
            #print(coords)
            box_dict[frame] = coords

        return box_dict

    def close(self):
        self.sess.close()
        self.default_graph.close()


if __name__ == "__main__":
    model_path = 'test/faster_rcnn_inception_v2_coco/frozen_inference_graph.pb'
    odapi = DetectorAPI(path_to_ckpt=model_path)
    threshold = 0.7
    frame_packet = os.listdir('img')
    packet_coords = odapi.processPacket(frame_packet)
    print(packet_coords)
    # for frame in frame_packet:
    #     frame = 'img/' + frame
    #     cap = cv2.VideoCapture(frame)
    #     r, img = cap.read()
    #     img = cv2.resize(img, (1280, 720))
    #boxes, scores, classes, num = odapi.processPacket(img)

    # Visualization of the results of a detection.

    # for i in range(len(boxes)):
    #     # Class 1 represents human
    #     if classes[i] == 1 and scores[i] > threshold:
    #         box = boxes[i]
    #         cv2.rectangle(img, (box[1], box[0]), (box[3], box[2]), (255, 0, 0), 2)
    #         print("(", box[1], ", ", box[0], ")")
    #         print("(", box[3], ", ", box[2], ")")
    # cv2.imshow("preview", img)
    # key = cv2.waitKey(10000)
    #if key & 0xFF == ord('q'):
        #break
