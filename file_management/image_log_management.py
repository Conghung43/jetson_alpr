# import numpy as np
# import time
from jetson_alpr import config
from datetime import datetime
import os
from PIL import Image
import shutil

#Save image to directory
def save_image(image, current_time, add_name):
    datetime_now = datetime.fromtimestamp(current_time)
    folder_path = os.path.join(config.save_path, f"{datetime_now.month}_{datetime_now.day}")
    pl_image = Image.fromarray(image)
    try:
        pl_image.save(os.path.join(folder_path, f"{current_time}_{add_name[0]}_{add_name[1]}.{config.image_format}"),quality = config.quality)
    except:
        create_new_folder(folder_path)

def create_new_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    base_time = os.path.getmtime(folder_path)
    directories_path = os.listdir(os.path.dirname(folder_path))
    for dir_path in directories_path:
        dir_path = os.path.join(os.path.dirname(folder_path),dir_path) 
        c_time = os.path.getmtime(dir_path)
        if datetime.fromtimestamp(base_time).day - datetime.fromtimestamp(c_time).day > config.expired_day:
            shutil.rmtree(dir_path)
    
# Generate image
# image = np.zeros([1080,1920,3],dtype=np.uint8)
# image.fill(255)
# while True:
#     # get current time
#     current_time = time.time()
#     try:
#         save_image_time
#         if current_time- save_image_time > config.time_diff:
#                 save_image(image, current_time)
#                 save_image_time = current_time
#     except:
#         print('exception')
#         save_image_time = current_time
