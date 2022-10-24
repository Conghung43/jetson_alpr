import cv2
import time
import queue
import os
import glob
import pyzed.sl as sl
from file_management import image_log_management

# image = cv2.imread('image.jpg')
image_temp_path = 'image_temp'
def put_queue_save_image(images_saved_path_queue, current_time, image):
    image_name_time_gps = f'{image_temp_path}/{current_time}_22.625876_120.311123.jpg'
    images_saved_path_queue.put(image_name_time_gps)
    #Save image
    cv2.imwrite(image_name_time_gps, image)

def read_camera( queue_data):
    #Read zed canera
    init = sl.InitParameters()
    init.camera_resolution = sl.RESOLUTION.HD2K
    init.depth_mode = sl.DEPTH_MODE.NONE
    cam = sl.Camera()
    if not cam.is_opened():
        print("Opening ZED Camera...")
    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()
    runtime = sl.RuntimeParameters()
    mat = sl.Mat()

    current_second = time.localtime(time.time()).tm_sec
    images_saved_path_queue = queue.Queue()
    # put unhandle image from drive to queue
    for image_path in glob.glob(f'{image_temp_path}/*.jpg'):
        images_saved_path_queue.put(image_path)
    while True:
        err = cam.grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS:
            cam.retrieve_image(mat, sl.VIEW.LEFT)
            if time.localtime(time.time()).tm_sec != current_second:
                current_time = time.time()
                latitude, longitude = 22.625876, 120.311123
                # print(queue_data.qsize(), images_saved_path_queue.qsize())
                image = mat.get_data()
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
                image_log_management.save_image(image, current_time, [latitude, longitude])
                if queue_data.qsize() > 20:
                    put_queue_save_image(images_saved_path_queue, current_time, image)
                else:
                    if images_saved_path_queue.empty():
                        queue_data.put([current_time,latitude, longitude, image])
                    else:
                        while queue_data.qsize() <= 20 and not images_saved_path_queue.empty():
                            # move data from queue to return queue
                            image_path = images_saved_path_queue.get()
                            image_name = os.path.basename(image_path)
                            image_data = image_name.split('_')
                            image_data.append(cv2.imread(image_path))
                            queue_data.put(image_data)
                            os.remove(image_path)
                        if queue_data.qsize() <= 20:
                            # add image to return queue
                            queue_data.put([current_time,latitude, longitude, image])
                        else:
                            put_queue_save_image(images_saved_path_queue, current_time, image)
                current_second = time.localtime(time.time()).tm_sec
