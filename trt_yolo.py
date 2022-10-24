import os
import time
import argparse
import cv2
import pycuda.autoinit  # This is needed for initializing CUDA driver

from utils.yolo_classes import get_cls_dict
from utils.camera import add_camera_args, Camera
from utils.display import open_window, set_display, show_fps
from utils.visualization import BBoxVisualization
from utils.yolo_with_plugins import TrtYOLO

import queue
import test_mock_camera
import threading
import time
import random
import test_sqlite
import test_detection_handling_and_concatenate_image as detection_handling
import sqlite3
import collections
queue_data = queue.Queue()

threading.Thread(target=test_mock_camera.read_camera, args=(queue_data,)).start()

def parse_args():
    """Parse input arguments."""
    desc = ('Capture and display live camera video, while doing '
            'real-time object detection with TensorRT optimized '
            'YOLO model on Jetson')
    parser = argparse.ArgumentParser(description=desc)
    parser = add_camera_args(parser)
    parser.add_argument(
        '-c', '--category_num', type=int, default=80,
        help='number of object categories [80]')
    parser.add_argument(
        '-t', '--conf_thresh', type=float, default=0.3,
        help='set the detection confidence threshold')
    parser.add_argument(
        '-m', '--model', type=str, required=True,
        help=('[yolov3-tiny|yolov3|yolov3-spp|yolov4-tiny|yolov4|'
              'yolov4-csp|yolov4x-mish|yolov4-p5]-[{dimension}], where '
              '{dimension} could be either a single number (e.g. '
              '288, 416, 608) or 2 numbers, WxH (e.g. 416x256)'))
    parser.add_argument(
        '-l', '--letter_box', action='store_true',
        help='inference with letterboxed image [False]')
    args = parser.parse_args()
    return args

def get_plate_character(char_dict):
  plate_character = ''
  char_dict = collections.OrderedDict(sorted(char_dict.items()))
  for k, v in char_dict.items():
    plate_character = plate_character + v
  return plate_character

def loop_and_detect(cam, trt_yolo, conf_th, vis):
    db = sqlite3.connect("main.db")
    cursor = db.cursor()
    while True:
        if queue_data.empty():
            continue
        image_data = queue_data.get()
        current_time,latitude, longitude, img = image_data
        boxes, confs, clss = trt_yolo.detect(img.copy(), conf_th)
        detections = zip(boxes, confs, clss)
        # detections = detection_handling.resize_detections(img, detections)#???
        detections = detection_handling.dupplicate_handling(detections)
        detections_plate, _ = detection_handling.clasify_plate_data(detections)

        # Handle zoom:
        images = []  
        for detection_plate in detections_plate:
            images += detection_handling.plate_zoom_concatenate(raw_image, detection_plate)
        detection_handling.add_white_image_four_even(images)
        concatenated_images = detection_handling.image_concatenate(images)

        for concatenated_image in concatenated_images:
            boxes, confs, clss = trt_yolo.detect(concatenated_image.copy(), conf_th)
            detections = zip(boxes, confs, clss)
            # detections = detection_handling.resize_detections(img, detections)#???
            detections = detection_handling.dupplicate_handling(detections)
            _, detections_masks = detection_handling.clasify_plate_data(detections)
            print([get_plate_character(plate) for plate in detections_masks])

            # test_sqlite.insert_sql(db, cursor, plate_number, recorded_time, longtitude, latitude)


        #[plate_number, recorded_time, longtitude, latitude]


def main():
    args = parse_args()
    if args.category_num <= 0:
        raise SystemExit('ERROR: bad category_num (%d)!' % args.category_num)
    if not os.path.isfile('yolo/%s.trt' % args.model):
        raise SystemExit('ERROR: file (yolo/%s.trt) not found!' % args.model)

    cam = Camera(args)
    if not cam.isOpened():
        raise SystemExit('ERROR: failed to open camera!')
    cls_dict = get_cls_dict(args.category_num)
    vis = BBoxVisualization(cls_dict)
    trt_yolo = TrtYOLO(args.model, args.category_num, args.letter_box)
    loop_and_detect(cam, trt_yolo, args.conf_thresh, vis=vis)

    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
