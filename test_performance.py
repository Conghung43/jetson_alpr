from PIL import Image
from tqdm import tqdm
import time
import cv2
# Opens a image in RGB mode
# im = Image.open(r"image_test\12)AJX3380.jpg")
im = cv2.imread(r"image_test\12)AJX3380.jpg")
total_time = 0
for i in range(1000):
    img = im.copy()
    s_time = time.time()
    # img.resize((960,540), Image.BICUBIC  )
    cv2.resize(img, (960,540), interpolation = cv2.INTER_NEAREST)
    total_time += time.time() - s_time
print(total_time)