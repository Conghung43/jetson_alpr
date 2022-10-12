
import numpy as np


def bbox2points(bbox):
    """
    From bounding box yolo format
    to corner points cv2 rectangle
    """
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
    # Detection duplicate handling
    temp_detection = []

    for first_index, (label, confidence, bbox) in enumerate(detections):
        # label, confidence, bbox = detections[i]
        if first_index == len(detections) -1:
            temp_detection.append([label, confidence, bbox])
            break
        for second_index in range(first_index + 1, len(detections), 1):
            temp_label, temp_confidence, temp_bbox = detections[second_index]
            if label == temp_label and (is_bbox_occlusion(bbox,temp_bbox) or is_bbox_occlusion(temp_bbox, bbox)):
                break
            elif second_index == len(detections) -1:
                temp_detection.append([label, confidence, bbox])
    return temp_detection


def clasify_plate_data(detections):
    # Get plate list
    detections_plate = [(label, acc, bbox) for label, acc, bbox in detections if label == 'plate']
    detections_mask = [[]]*len(detections_plate)
    for index, (label, acc, bbox) in enumerate(detections):
        if label == 'plate':
            # detections_mask.append(-1)
            continue
        for plate_index, plate_data in enumerate(detections_plate):
            if abs(bbox[0] - plate_data[2][0]) < plate_data[2][2] and abs(bbox[1] - plate_data[2][1]) < plate_data[2][3]:
                detections_mask[plate_index].append([label, acc, bbox])
                break
            # if plate_index == len(detections_plate) -1:
                # detections_mask.append(-1)
    return detections_plate, detections_mask

max_ratio = 4

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
    zoom_ratio_jump = ((ratio/2)-max_ratio)/4
    x,y,_, _ = plate_detection_data[2]
    image_height, image_width = raw_image.shape[:2]
    images = []
    for index in range(4):
        zoom_image = max_ratio + zoom_ratio_jump*index
        crop_image_ratio = zoom_image/ratio
        ymin, ymax, xmin, xmax = [int(y-crop_image_ratio*image_height/2),int(y+crop_image_ratio*image_height/2),
                                int(x-crop_image_ratio*image_width/2),int(x+crop_image_ratio*image_width/2)]
        xmin, xmax, ymin, ymax = check_image_close_border(image_height, image_width, xmin, xmax, ymin, ymax)
        image_crop = raw_image[ymin:ymax,xmin:xmax]
        image_crop = cv2.resize(image_crop, (int(image_width/2), int(image_height/2)), interpolation = cv2.INTER_AREA)
        # cv2.imwrite('image.jpg', image_crop)
        images.append(image_crop)
    return images
image_size = 608
def image_concentrate(images):
    numpy_horizontal_12 = np.hstack((images[0], images[1]))
    numpy_horizontal_34 = np.hstack((images[2], images[3]))
    numpy_vertical = np.vstack((numpy_horizontal_12, numpy_horizontal_34))
    # numpy_vertical = cv2.cvtColor(numpy_vertical, cv2.COLOR_BGR2RGB)
    # cv2.imwrite('image.jpg', numpy_vertical)

def plate_zoom_concentrate(raw_image, plate_detection_data):
    plate_width, plate_height = plate_detection_data[2][2:]
    image_height, image_width = raw_image.shape[:2]
    ratio_width = image_width/plate_width
    ratio_height = image_height/plate_height
    zoom_ratio = ratio_width if ratio_width < ratio_height else ratio_height
    images = image_crop_base_ratio(raw_image, plate_detection_data, zoom_ratio)
    image_concentrate(images)
    # return image_concentrate

def resize_detections(raw_image, detections):
    image_height, image_width = raw_image.shape[:2]
    ratio_width = image_width/image_size
    ratio_height = image_height/image_size
    detections = [[label, acc, np.array(bbox)* np.array([ratio_width,ratio_height,ratio_width,ratio_height])] for label, acc, bbox in detections]
    return detections
# detections = [('3', '27.47', (28.58824348449707, 302.53173828125, 7.233067512512207, 13.82115650177002)), 
#                 ('9', '29.51', (21.658220291137695, 302.8802795410156, 6.748055934906006, 16.394304275512695)), 
#                 ('8', '40.56', (21.658220291137695, 302.8802795410156, 6.748055934906006, 16.394304275512695)), 
#                 ('plate', '52.32', (28.58824348449707, 302.53173828125, 7.233067512512207, 13.82115650177002)), 
#                 ('x', '54.16', (490.6280822753906, 285.5679626464844, 6.881631851196289, 16.96036720275879)), 
#                 ('plate', '58.01', (21.658220291137695, 302.8802795410156, 6.748055934906006, 16.394304275512695)), 
#                 ('8', '59.14', (514.5220336914062, 285.8786926269531, 6.891545295715332, 16.220966339111328)), 
#                 ('0', '88.71', (514.5220336914062, 285.8786926269531, 6.891545295715332, 16.220966339111328)), 
#                 ('8', '89.68', (15.039226531982422, 303.529296875, 5.306866645812988, 15.310150146484375)), 
#                 ('j', '89.71', (490.6280822753906, 285.5679626464844, 6.881631851196289, 16.96036720275879)), 
#                 ('3', '97.54', (503.0694580078125, 285.8420104980469, 7.302872657775879, 17.015560150146484)), 
#                 ('3', '99.53', (508.8966979980469, 285.6167907714844, 6.509527206420898, 16.57345199584961)), 
#                 ('plate', '99.56', (22.781414031982422, 301.6792907714844, 27.239728927612305, 28.81048583984375)), 
#                 ('0', '99.56', (520.2601928710938, 286.2208557128906, 7.1091718673706055, 15.988213539123535)), 
#                 ('a', '99.86', (484.5466003417969, 285.6286315917969, 6.751768589019775, 16.273067474365234)), 
#                 ('plate', '99.99', (502.2041931152344, 284.4739685058594, 47.39316940307617, 31.452478408813477))]

detections = [('3', '41.7', (492.1046447753906, 456.39300537109375, 49.101524353027344, 35.877052307128906)), 
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

# detections = [('3', '26.9', (436.0654296875, 223.69798278808594, 8.365856170654297, 18.135061264038086)), 
#  ('7', '53.6', (428.5239562988281, 223.6650390625, 6.246547698974609, 18.65497589111328)), 
#  ('g', '69.95', (446.5540771484375, 223.65548706054688, 6.1387434005737305, 19.614879608154297)), 
#  ('8', '85.84', (428.5239562988281, 223.6650390625, 6.246547698974609, 18.65497589111328)), 
#  ('2', '90.98', (436.0654296875, 223.69798278808594, 8.365856170654297, 18.135061264038086)), 
#  ('h', '91.72', (452.1166076660156, 224.36627197265625, 5.225356101989746, 18.767257690429688)), 
#  ('plate', '99.96', (439.31744384765625, 222.12049865722656, 35.978111267089844, 30.686599731445312))]
            
import time
import cv2
from PIL import Image
raw_image = cv2.imread('12)AJX3380.jpg')
for i in range(100):
    s_time = time.time()
    # raw_image = cv2.resize(raw_image, (608,608), interpolation = cv2.INTER_AREA)
    detection = resize_detections(raw_image, detections)
    detection = dupplicate_handling(detection)
    detections_plate, detections_masks = clasify_plate_data(detection)
    detections_masks = np.array(detections_masks)[:,:,0]
    print(time.time()- s_time)
    

plate_zoom_concentrate(raw_image, detections_plate[1])

def process_plate_algorithm(detections, ori_image, network_size, iters):

    detections = dupplicate_handling(detections)

    is_break = False
    character_dict = {}
    ori_image_h, ori_image_w, _ = ori_image.shape
    height, width = network_size
    h_ratio = height/ori_image_h
    w_ratio = width/ori_image_w
    for label, accuracy, box in detections:
        l, t, r, b = bbox2points(box)
        l = int(l/w_ratio)
        r = int(r/w_ratio)
        t = int(t/h_ratio)
        b = int(b/h_ratio)
        if label == 'plate':
            try:
                plate_width
            except:
                plate_width = box[2]
            if plate_width <= box[2]:

                plate_width = box[2]
                plate_left = box[0] - box[2]/2
                plate_right = box[0] + box[2]/2

                if box[0] - box[2]/2 < width/8 or box[0] + box[2] > width*7/8:
                    if box[0] - box[2]/2 < width/8:
                        left = 0
                        right = int(ori_image_w*3/4)
                    else:
                        left = int(ori_image_w/4)
                        right = ori_image_w
                else:
                    left = int(ori_image_w/8)
                    right = int(ori_image_w*7/8)

                if box[1] - box[3]/2 < height/8 or box[1] + box[3] > height*7/8:
                    if box[1] - box[3]/2 < height/8:
                        top = 0
                        button = int(ori_image_h*3/4)
                    else:
                        top = int(ori_image_h/4)
                        button = ori_image_h
                else:
                    top = int(ori_image_h/8)
                    button = int(ori_image_h*7/8)
                if iters == 0:
                    gap = 300
                    left = l -gap
                    right = r+ gap
                    top = (t + b)/2 - (r-l)/4 - gap/2
                    button = (t + b)/2 + (r-l)/4 + gap/2
                    if top < 0:
                        button = button - top
                        top = 0
                    if button >= ori_image_h:
                        top = top - (button - ori_image_h + 1)
                        button = ori_image_h - 1
                    if left < 0:
                        right = right - left
                        left = 0
                    if right >= ori_image_w:
                        left = left - (right - ori_image_w + 1)
                        button = ori_image_w - 1

    try:
        top
    except:
        left = int(ori_image_w/8)
        right = int(ori_image_w*7/8)
        top = int(ori_image_h/8)
        button = int(ori_image_h*7/8)

    plate_key = str(ori_image_w) + "*" + str(ori_image_h) + ","
    try:
        image_copy = ori_image.copy()
        if iters == 0:# and len(detections) == 0:
            return_data = send_image(ori_image)
            detections = detections + [(obj[0], obj[1], (np.array(obj[2])*height).astype(int)) for obj in return_data]
        for label, accuracy, box in detections:
            # if box[0] > plate_left and box[0] < plate_right:
            character_dict[box[0]] = label
            l, t, r, b = bbox2points(box)
            l = int(l/w_ratio)
            r = int(r/w_ratio)
            t = int(t/h_ratio)
            b = int(b/h_ratio)
            # plate_key = plate_key + label + ":" + str( l) + ":" + str(t) + ":" + str(r-l) + ":" + str(b-t) + ","
            plate_key = plate_key + label + ":" + str( l) + ":" + str(t) + ":" + str(r-l) + ":" + str(b-t) + ":" + str(accuracy)  + "%" + ","
            cv2.rectangle(image_copy, (l, t), (r, b), [255,0,0], 1)
            image_copy = cv2.putText(image_copy, "{}".format(label),
                        (l, t - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        [0,0,255], 2)
        cv2.imwrite('D:/image_log/{}_{}_{}.jpg'.format(str(time.time()), str(ori_image_w), str(ori_image_w)), image_copy)
        ori_image = ori_image[int(top):int(button), int(left):int(right)]
        if plate_width > (right - left)/2:
            is_break = True
        # cv2.imshow('image', image)
        # cv2.waitKey(1000)
    except:
        print('')

    plate_character = get_plate_character(character_dict)

    return plate_character, ori_image, is_break, plate_key
