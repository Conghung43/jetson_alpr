
import cv2
import numpy as np
import pyzed.sl as sl
import time
init = sl.InitParameters()
init.camera_resolution = sl.RESOLUTION.HD1080
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
while True:
    # ret, frame = cap.read()
    err = cam.grab(runtime)
    if err == sl.ERROR_CODE.SUCCESS:
        #if time.localtime(time.time()).tm_sec % 2 ==0:
        #    continue
        cam.retrieve_image(mat, sl.VIEW.LEFT)
        image = mat.get_data()
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        cv2.imshow('Image', image)
        code = cv2.waitKey(10)
        if code == ord('q'):
            break
