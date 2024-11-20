import pyautogui
# import cv2  # pip install opencv-python
# import numpy as np
from PIL import Image
from math import sqrt


# global config
# scroll_direction = "vertical"
scroll_direction = "horizontal"

# size of a single snapshot
img_width = int(1920 / 3)
img_height = int(1080 / 2)

scroll_bar_margin_left = 0
scroll_bar_margin_right = int(0.05 * img_width)
scroll_bar_margin_top = 0
scroll_bar_margin_bottom = int(0.05 * img_height)

min_overlap_ratio = 0.1

pixel_diff_avg_threshold = 1.0

sample_stepsize = 20  # to speed up the comparison, default 1: slowest


# create snapshot
img_1 = pyautogui.screenshot(region=[0, 0, img_width, img_height])  # x, y, w, h
# img_2 = pyautogui.screenshot(region=[0, 360, img_width, img_height])  # vertical test
img_2 = pyautogui.screenshot(region=[420, 0, img_width, img_height])  # horizontal test

# save as new image
img_1.save("screenshot_1.png")
img_2.save("screenshot_2.png")

# or open an existing image
# img_1 = Image.open("screenshot_1.png")
# img_2 = Image.open("screenshot_2.png")

# pixels: 2-dimension array
pixels_1 = img_1.load()
pixels_2 = img_2.load()
# r, g, b = pixels_1[0, 0]
# print(r, g, b)


def calc_3d_vector_distance(vector_1, vector_2):
    dx = vector_2[0] - vector_1[0]
    dy = vector_2[1] - vector_1[1]
    dz = vector_2[2] - vector_1[2]
    return sqrt(dx**2 + dy**2 + dz**2)

def calc_avg(array):
    n = len(array)
    if n == 0:
        return 0.0
    else:
        sum = 0
        for i in array:
            sum += i
        avg = sum / n
        return avg

def calc_overlap_diff(scroll_direction, pixels_1, pixels_2, img_width, img_height, offset):

    # get overlap area size and lefttop coordinate
    if scroll_direction == "vertical":
        overlap_w = img_width - scroll_bar_margin_left - scroll_bar_margin_right
        overlap_h = img_height - offset
        overlap_1_lefttop = scroll_bar_margin_left, offset  # image_1
        overlap_2_lefttop = scroll_bar_margin_left, 0       # image_2
    elif scroll_direction == "horizontal":
        overlap_w = img_width - offset
        overlap_h = img_height - scroll_bar_margin_top - scroll_bar_margin_bottom
        overlap_1_lefttop = offset, scroll_bar_margin_top   # image_1
        overlap_2_lefttop = 0, scroll_bar_margin_top        # image_2
    else:
        print("Invalid scroll direction!")
        return -1

    # traverse each pixel in overlapping area
    pixel_diffs = []
    for x in range(0, overlap_w, sample_stepsize):
        for y in range(0, overlap_h, sample_stepsize):
            rgb_1 = pixels_1[overlap_1_lefttop[0] + x, overlap_1_lefttop[1] + y]
            rgb_2 = pixels_2[overlap_2_lefttop[0] + x, overlap_2_lefttop[1] + y]
            pixel_diffs.append(calc_3d_vector_distance(rgb_1, rgb_2))

    # calculate average pixel difference
    return calc_avg(pixel_diffs)


# iterate offset and find minimum pixel difference
find_offset = False
for offset in range(0, int(img_height * (1 - min_overlap_ratio))):
    if calc_overlap_diff(scroll_direction, pixels_1, pixels_2, img_width, img_height, offset) <= pixel_diff_avg_threshold:
        find_offset = True
        break

if not find_offset:
    print("Merging image failed!")
    exit(-1)
else:
    print("offset = %d, merging image..." % offset)

# calculate size of merged image
if scroll_direction == "vertical":
    x, y = img_width, img_height + offset
elif scroll_direction == "horizontal":
    x, y = img_width + offset, img_height

# create a new image
img_merged = Image.new("RGB", (x, y))

# draw each pixel with RGB info
if scroll_direction == "vertical":
    for i in range(x):
        for j in range(offset):
            img_merged.putpixel((i, j), pixels_1[i, j])   # image 1
        for j in range(offset, y):
            img_merged.putpixel((i, j), pixels_2[i, j - offset])   # image 2
elif scroll_direction == "horizontal":
    for j in range(y):
        for i in range(offset):
            img_merged.putpixel((i, j), pixels_1[i, j])   # image 1
        for i in range(offset, x):
            img_merged.putpixel((i, j), pixels_2[i - offset, j])   # image 2

img_merged.save("screenshot_new.png")

