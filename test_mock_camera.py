import cv2
import time
import queue
import os

image = cv2.imread('image.jpg')

def put_queue_save_image(images_saved_path_queue, current_time, image):
    image_name_time_gps = f'image_temp/{current_time}_22.625876_120.311123.jpg'
    images_saved_path_queue.put(image_name_time_gps)
    #Save image
    cv2.imwrite(image_name_time_gps, image)

def read_camera_mock( queue_data):
    current_second = time.localtime(time.time()).tm_sec
    images_saved_path_queue = queue.Queue()
    while True:
        if time.localtime(time.time()).tm_sec != current_second:
            current_time = time.time()
            latitude, longitude = 22.625876, 120.311123
            print(queue_data.qsize(), images_saved_path_queue.qsize())
            # push image to queue
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


