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
    zoom_ratio_jump = ((ratio/2)-max_ratio_zoom)/4
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
                            interpolation = cv2.INTER_AREA)
        images.append(image_crop)
    return images
image_size_temp = 608
def image_concatenate(images):
    concatenate_images = []
    for index in range(0, len(images), images_per_page):
        numpy_horizontal_12 = np.hstack(images[index:int(index+images_per_page/2)])
        numpy_horizontal_34 = np.hstack(images[int(index+images_per_page/2):index+images_per_page])
        numpy_vertical = np.vstack((numpy_horizontal_12, numpy_horizontal_34))
        concatenate_images.append(numpy_vertical)
        # numpy_vertical = cv2.cvtColor(numpy_vertical, cv2.COLOR_BGR2RGB)
        cv2.imwrite(f'image_log/{time.time()}.jpg', numpy_vertical)
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


detections = [('3', '27.47', (28.58824348449707, 302.53173828125, 7.233067512512207, 13.82115650177002)), 
                ('9', '29.51', (21.658220291137695, 302.8802795410156, 6.748055934906006, 16.394304275512695)), 
                ('8', '40.56', (21.658220291137695, 302.8802795410156, 6.748055934906006, 16.394304275512695)), 
                ('plate', '52.32', (28.58824348449707, 302.53173828125, 7.233067512512207, 13.82115650177002)), 
                ('x', '54.16', (490.6280822753906, 285.5679626464844, 6.881631851196289, 16.96036720275879)), 
                ('plate', '58.01', (21.658220291137695, 302.8802795410156, 6.748055934906006, 16.394304275512695)), 
                ('8', '59.14', (514.5220336914062, 285.8786926269531, 6.891545295715332, 16.220966339111328)), 
                ('0', '88.71', (514.5220336914062, 285.8786926269531, 6.891545295715332, 16.220966339111328)), 
                ('8', '89.68', (15.039226531982422, 303.529296875, 5.306866645812988, 15.310150146484375)), 
                ('j', '89.71', (490.6280822753906, 285.5679626464844, 6.881631851196289, 16.96036720275879)), 
                ('3', '97.54', (503.0694580078125, 285.8420104980469, 7.302872657775879, 17.015560150146484)), 
                ('3', '99.53', (508.8966979980469, 285.6167907714844, 6.509527206420898, 16.57345199584961)), 
                ('plate', '99.56', (22.781414031982422, 301.6792907714844, 27.239728927612305, 28.81048583984375)), 
                ('0', '99.56', (520.2601928710938, 286.2208557128906, 7.1091718673706055, 15.988213539123535)), 
                ('a', '99.86', (484.5466003417969, 285.6286315917969, 6.751768589019775, 16.273067474365234)), 
                ('plate', '99.99', (502.2041931152344, 284.4739685058594, 47.39316940307617, 31.452478408813477))]

detections1 = [('3', '41.7', (492.1046447753906, 456.39300537109375, 49.101524353027344, 35.877052307128906)), 
 ('a', '52.03', (477.7144775390625, 457.61700439453125, 6.825870990753174, 17.22686004638672)), 
 ('3', '57.25', (153.44033813476562, 153.73385620117188, 52.66558074951172, 46.33270263671875)), 
 ('3', '63.99', (174.34375, 456.6196594238281, 53.69977569580078, 39.52908706665039)), 
 ('plate', '68.67', (462.3174133300781, 153.96847534179688, 8.923372268676758, 22.449750900268555)), 
 ('j', '70.55', (158.9365234375, 458.15130615234375, 7.55463171005249, 19.338619232177734)), 
 ('8', '74.09', (507.9677429199219, 458.20770263671875, 12.446541786193848, 17.67310905456543)), 
 ('a', '82.82', (158.9365234375, 458.15130615234375, 7.55463171005249, 19.338619232177734)), 
 ('j', '89.04', (477.7144775390625, 457.61700439453125, 6.825870990753174, 17.22686004638672)), 
 ('0', '98.36', (507.9677429199219, 458.20770263671875, 12.446541786193848, 17.67310905456543)), 
 ('3', '98.78', (175.2104034423828, 457.8562316894531, 7.36706018447876, 20.993988037109375)), 
 ('3', '98.78', (492.1151428222656, 457.197021484375, 6.963630199432373, 18.29810905456543)), 
 ('j', '99.3', (443.9971923828125, 154.19773864746094, 8.204843521118164, 21.858978271484375)), 
 ('a', '99.4', (151.88619995117188, 458.29345703125, 8.034679412841797, 18.282119750976562)), 
 ('a', '99.41', (471.6353759765625, 457.9594421386719, 7.145735740661621, 16.559642791748047)), 
 ('x', '99.57', (166.346923828125, 458.0277404785156, 7.272622108459473, 20.851478576660156)), 
 ('j', '99.66', (133.43289184570312, 154.79908752441406, 9.045493125915527, 25.589763641357422)), 
 ('3', '99.73', (462.31005859375, 153.9793243408203, 8.853008270263672, 22.53898811340332)), 
 ('x', '99.74', (483.9715576171875, 457.43597412109375, 6.992224216461182, 19.386680603027344)), 
 ('x', '99.83', (452.2142639160156, 154.27694702148438, 8.234317779541016, 22.68916893005371)), 
 ('a', '99.83', (435.9441223144531, 154.8026580810547, 8.818227767944336, 21.148723602294922)), 
 ('3', '99.84', (154.68019104003906, 154.87313842773438, 9.655092239379883, 25.96133804321289)), 
 ('3', '99.84', (181.87513732910156, 458.2022399902344, 7.568175315856934, 21.004283905029297)), 
 ('8', '99.84', (188.81222534179688, 458.498046875, 7.7809834480285645, 20.76588249206543)), 
 ('0', '99.86', (196.23910522460938, 459.2176208496094, 7.762885093688965, 19.661592483520508)), 
 ('3', '99.88', (498.3087463378906, 457.5361633300781, 6.921912670135498, 18.63231086730957)), 
 ('x', '99.92', (142.7823486328125, 154.8902130126953, 9.06440258026123, 26.372961044311523)), 
 ('8', '99.92', (477.7777099609375, 154.5242919921875, 8.881559371948242, 22.947160720825195)), 
 ('3', '99.94', (469.97491455078125, 154.17572021484375, 8.619683265686035, 22.754398345947266)), 
 ('0', '99.94', (486.1698913574219, 155.2750701904297, 8.64971923828125, 21.952072143554688)), 
 ('a', '99.94', (124.21929931640625, 155.48971557617188, 9.947527885437012, 24.04389190673828)), 
 ('8', '99.96', (172.4354705810547, 155.57928466796875, 9.782135009765625, 26.11509132385254)), 
 ('3', '99.97', (163.58583068847656, 155.31687927246094, 9.283503532409668, 25.66629981994629)), 
 ('0', '99.97', (181.92355346679688, 156.28616333007812, 9.4979248046875, 25.08689308166504)), 
 ('plate', '99.98', (491.5050048828125, 456.0624694824219, 52.16703414916992, 36.12636947631836)), 
 ('plate', '99.98', (461.5253601074219, 151.91555786132812, 65.06527709960938, 42.806724548339844)), 
 ('plate', '99.98', (173.87850952148438, 456.22930908203125, 57.06219482421875, 39.585357666015625)), 
 ('plate', '99.99', (153.40406799316406, 152.752197265625, 73.89910888671875, 47.74468231201172))]      

raw_image = cv2.imread('12)AJX3380.jpg')

# raw_image = cv2.resize(raw_image, (608,608), interpolation = cv2.INTER_AREA)
detections = resize_detections(raw_image, detections)
detections = dupplicate_handling(detections)
detections_plate, detections_masks = clasify_plate_data(detections)
# Plate list
print([get_plate_character(plate) for plate in detections_masks])

# concatenate
max_ratio_zoom = 2
zoom_iteration = 4
images_per_page = 4
images = []  
for detection_plate in detections_plate:
    images += plate_zoom_concatenate(raw_image, detection_plate)
add_white_image_four_even(images)
image_concatenate(images)