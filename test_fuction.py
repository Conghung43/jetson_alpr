def detections_dupplicate_handling(detections):
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
    detections_mask = []
    for index, (label, acc, bbox) in enumerate(detections):
        if label == 'plate':
            detections_mask.append(-1)
            continue
        for plate_index, plate_data in enumerate(detections_plate):
            if abs(bbox[0] - plate_data[2][0]) < plate_data[2][2]:
                detections_mask.append(plate_index)
                break
            if plate_index == len(detections_plate) -1:
                detections_mask.append(-1)
    return detections_plate, detections_mask

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
clasify_plate_data(detections)


def process_plate_algorithm(detections, ori_image, network_size, iters):

    detections = detections_dupplicate_handling(detections)

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
