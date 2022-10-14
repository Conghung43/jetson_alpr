import queue
import test_mock_camera
import threading
import time
import random
queue_data = queue.Queue()

threading.Thread(target=test_mock_camera.read_camera_mock, args=(queue_data,)).start()
while True:
    if queue_data.empty():
        continue
    image_data = queue_data.get()
    size = int(queue_data.qsize()/2)
    if queue_data.qsize() < 19:
        size = 50
    
    time.sleep(random.randint(1,size)/10)
