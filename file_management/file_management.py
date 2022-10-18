import pyzed.sl as sl
from datetime import datetime, timedelta, date
import cv2
import math
import numpy as np
import shutil
import PIL
import config
import time
from PIL import Image
import os

def filter_list(x):
    if os.path.isdir(x) and 'ache' not in x:
        return True
    else :
        return False

def get_date(date): 
    ## Input datetime format
    ## Output  Int

    return date.year, date.month, date.day, date.hour, date.minute, date.second, date.microsecond

def new_folder(timestamp,save_path):
    ## Input: Timestamp.

    new_date = datetime.fromtimestamp(timestamp)
    new_year, new_month, new_day, new_hour, new_minute, new_second , new_microsecond = get_date(new_date)
    # os.makedirs(save_path + f"/{new_year}_{new_month}_{new_day}", exist_ok= True)
    try:
        os.makedirs(save_path + f"/{new_year}_{new_month}_{new_day}")
        return True
    except:
        return False    


def check_list_path(save_path):
    list_path = sorted(filter(filter_list, os.listdir('.')), key = os.path.getmtime)
    if len(list_path)  != 0 and len(list_path) > expired_time + 1:
        shutil.rmtree(save_path + '/' + list_path[0])
        print('Removed')


count = 0
save_path = config.save_path
pillow = config.pillow
image_format = str(config.image_format).lower()

 ### {'resolution: (width, height)}
resolution_dict ={
    'HD2k': (2208, 1242),
    'HD1080':(1920,1080),
    'HD720':(1280,720),
    'WVG':(672, 376),
}  

ratio = config.quality/100
width, height = resolution_dict[config.resolution]
width, height = int(width*ratio), int(height*ratio)
expired_time = config.expired_time
time_diff = config.time_diff
os.chdir(save_path)


### Zed Camera Initialization Parameter
zed = sl.Camera()
init_params = sl.InitParameters()
init_params.camera_fps
init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE
init_params.coordinate_units = sl.UNIT.METER

if config.resolution == 'HD2k':
     init_params.camera_resolution = sl.RESOLUTION.HD2K
elif config.resolution == 'HD1080':
     init_params.camera_resolution = sl.RESOLUTION.HD1080
elif config.resolution == 'HD720':
     init_params.camera_resolution = sl.RESOLUTION.HD720
elif config.resolution == 'WVGA':
     init_params.camera_resolution = sl.RESOLUTION.WVGA
else:
     raise ValueError('None available resolution provided!')


err = zed.open(init_params)
if err != sl.ERROR_CODE.SUCCESS:
     print(f'Error : {err}')
     exit(1)

image = sl.Mat()
depth = sl.Mat()
point_cloud = sl.Mat()
runtime_parameters = sl.RuntimeParameters()
runtime_parameters.sensing_mode = sl.SENSING_MODE.STANDARD

while True:
    if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
        
        ###  Add New Folder during first process if necessary.
        if  count == 0: 
            if new_folder(datetime.timestamp(datetime.now()),save_path):
                check_list_path(save_path)

            list_path = sorted(filter(filter_list, os.listdir('.')), key = os.path.getmtime)
            current_date = datetime.strptime(list_path[-1],'%Y_%m_%d') + timedelta(days = 1)
            count+=1

        else :
            time.sleep(time_diff)

        zed.grab(runtime_parameters)
        zed.retrieve_image(image, sl.VIEW.LEFT)
        zed.retrieve_measure(depth, sl.MEASURE.DEPTH)
        if pillow:
            zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)
        else:
            zed.retrieve_measure(point_cloud, sl.MEASURE.XYZBGRA)

        timestamp = zed.get_timestamp(sl.TIME_REFERENCE.CURRENT)
        date = datetime.fromtimestamp(timestamp.get_milliseconds()/1000)

        ### If the camera current date greater than folder time, add new folder to saving path.
        if date > current_date:
            # new_folder(datetime.timestamp(date), save_path )
            if new_folder(datetime.timestamp(datetime.now()),save_path):
                check_list_path(save_path)            
            list_path = sorted(filter(filter_list, os.listdir('.')), key = os.path.getmtime)
            current_date = datetime.strptime(list_path[-1],'%Y_%m_%d') + timedelta(days = 1)


        year, month, day, hour, minute, second ,milsecond = get_date(date)
        save_file =  save_path + f'/{year}_{month}_{day}/{hour}_{minute}_{second}_{milsecond}'

        if pillow:
            Image.fromarray(image.get_data()[:,:,:3][:,:,::-1]).save(save_file + f'.{image_format}', quality = config.quality)
        else:
            if ratio != 1:
                cv2.imwrite( save_file + f'.{image_format}', cv2.resize(image.get_data(), (width,height)))
            else:    
                cv2.imwrite( save_file + f'.{image_format}', image.get_data())

        with open(save_file  + f'.npy','wb') as f:
            if ratio != 1:
                np.save(f, np.resize(point_cloud.get_data(), (height, width, 4)))
            else:
                np.save(f,point_cloud.get_data())
        print(f'Saved :{save_file}.{image_format}')
  