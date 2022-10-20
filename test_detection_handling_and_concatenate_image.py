import numpy as np
import time
import cv2
import collections

def bbox2points(bbox):
    x, y, w, h = bbox
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

def is_bbox_occlusion(bbox1, bbox2):
    left, top, right, bottom = bbox2points(bbox1)
    if bbox2[0] > left and bbox2[0] < right and bbox2[1] > top and bbox2[1] < bottom:
        return True
    else:
        return False

def dupplicate_handling(detections):
    temp_detection = []
    for first_index, (label, confidence, bbox) in enumerate(detections):
        # label, confidence, bbox = detections[i]
        if first_index == len(detections) -1:
            temp_detection.append([label, confidence, bbox])
            break
        for second_index in range(first_index + 1, len(detections), 1):
            temp_label, _, temp_bbox = detections[second_index]
            if label == temp_label and (is_bbox_occlusion(bbox,temp_bbox) or is_bbox_occlusion(temp_bbox, bbox)):
                break
            elif second_index == len(detections) -1:
                temp_detection.append([label, confidence, bbox])
    return temp_detection

def clasify_plate_data(detections):
    # Get plate list
    detections_plate = [(label, acc, bbox) for label, acc, bbox in detections if label == 'plate']
    detections_mask = [{} for i in range(len(detections_plate))]
    for label, _, bbox in detections:
        if label == 'plate':
            continue
        for plate_index, plate_data in enumerate(detections_plate):
            if abs(bbox[0] - plate_data[2][0]) < plate_data[2][2] and abs(bbox[1] - plate_data[2][1]) < plate_data[2][3]:
                detections_mask[plate_index][bbox[0]]= label
                break
    return detections_plate, detections_mask

def check_image_close_border(image_height, image_width, xmin, xmax, ymin, ymax):
    if xmin < 0:
        xmax = xmax - xmin
        xmin =0
    if xmax > image_width:
        xmin = image_width - (xmax-xmin)
        xmax = image_width

    if ymin < 0:
        ymax = ymax - ymin
        ymin =0
    if ymax > image_height:
        ymin = image_height - (ymax-ymin)
        ymax = image_height
    return xmin, xmax, ymin, ymax

def image_crop_base_ratio(raw_image, plate_detection_data, ratio):
    zoom_ratio_jump = ((ratio/2)-max_ratio_zoom)/16
    x,y,_, _ = plate_detection_data[2]
    image_height, image_width = raw_image.shape[:2]
    images = []
    for index in range(zoom_iteration):
        zoom_image = max_ratio_zoom + zoom_ratio_jump*index
        crop_image_ratio = zoom_image/ratio
        ymin, ymax, xmin, xmax = [int(y-crop_image_ratio*image_height/2),int(y+crop_image_ratio*image_height/2),
                                int(x-crop_image_ratio*image_width/2),int(x+crop_image_ratio*image_width/2)]
        xmin, xmax, ymin, ymax = check_image_close_border(image_height, image_width, xmin, xmax, ymin, ymax)
        image_crop = raw_image[ymin:ymax,xmin:xmax]
        image_crop = cv2.resize(image_crop, 
                            (int(image_width/2), int(image_height/2)), 
                            interpolation = cv2.INTER_NEAREST)
        images.append(image_crop)
    return images
image_size_temp = 416
def image_concatenate(images):
    concatenate_images = []
    # for index in range(0, len(images), images_per_page):
    #     numpy_horizontal_12 = np.hstack(images[index:int(index+images_per_page/2)])
    #     numpy_horizontal_34 = np.hstack(images[int(index+images_per_page/2):index+images_per_page])
    #     numpy_vertical = np.vstack((numpy_horizontal_12, numpy_horizontal_34))
    #     concatenate_images.append(numpy_vertical)
    #     # numpy_vertical = cv2.cvtColor(numpy_vertical, cv2.COLOR_BGR2RGB)
    #     cv2.imwrite(f'image_log/{time.time()}.jpg', numpy_vertical)
    for index in range(0, len(images), images_per_page):
        h,w,c = images[index].shape
        numpy_vertical = np.zeros((h*2, w*2, c),dtype=np.uint8)
        numpy_vertical[0:h,0:w] = images[index]
        numpy_vertical[0:h,w:2*w] = images[index+1]
        numpy_vertical[h:h*2,0:w] = images[index+2]
        numpy_vertical[h:h*2,w:w*2] = images[index+3]
        concatenate_images.append(numpy_vertical)
    return concatenate_images

def add_white_image_four_even(images):
    iteration = images_per_page-len(images)%images_per_page
    if iteration == images_per_page:
        return
    img = np.zeros(images[-1].shape,dtype=np.uint8)
    img.fill(255)
    for i in range(iteration):
        images.append(img)

def plate_zoom_concatenate(raw_image, plate_detection_data):
    plate_width, plate_height = plate_detection_data[2][2:]
    image_height, image_width = raw_image.shape[:2]
    ratio_width = image_width/plate_width
    ratio_height = image_height/plate_height
    zoom_ratio = ratio_width if ratio_width < ratio_height else ratio_height
    images = image_crop_base_ratio(raw_image, plate_detection_data, zoom_ratio)
    return images

def resize_detections(raw_image, detections):
    image_height, image_width = raw_image.shape[:2]
    ratio_width = image_width/image_size_temp
    ratio_height = image_height/image_size_temp
    detections = [[label, acc, np.array(bbox)* np.array([ratio_width,ratio_height,ratio_width,ratio_height])] for label, acc, bbox in detections]
    return detections

def get_plate_character(char_dict):
  plate_character = ''
  char_dict = collections.OrderedDict(sorted(char_dict.items()))
  for k, v in char_dict.items():
    plate_character = plate_character + v
  return plate_character

# concatenate
max_ratio_zoom = 1.2
zoom_iteration = 4
images_per_page = 4

