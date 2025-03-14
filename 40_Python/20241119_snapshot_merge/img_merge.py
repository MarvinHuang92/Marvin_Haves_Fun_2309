import os, shutil
import pyautogui
# import cv2  # pip install opencv-python
# import numpy as np
from PIL import Image
from math import sqrt


# for quick test
# test_mode = True  # 测试模式
test_mode = False  # 工作模式

# global config
scroll_direction = "vertical"
# scroll_direction = "horizontal"

# input image (for test mode only)
image_path_1 = "screenshot_1.png"
image_path_2 = "screenshot_2.png"
output_path = "screenshot_new.png"

min_overlap_ratio = 0.04

scroll_bar_margin_ratio = 0.25

pixel_diff_avg_threshold = 100.0

remove_img_2_white_margin = True  # 去掉图2上方或左侧的白边
white_margin_pixel_diff_avg_threshold = 5.0

sample_stepsize = 37  # to speed up the comparison, default 1: slowest

###################################################################

def calc_3d_vector_distance(vector_1, vector_2):
    dx = vector_2[0] - vector_1[0]
    dy = vector_2[1] - vector_1[1]
    dz = vector_2[2] - vector_1[2]
    return sqrt(dx**2 + dy**2 + dz**2)

def calc_3d_max_distance(vector_1, vector_2):
    dx = vector_2[0] - vector_1[0]
    dy = vector_2[1] - vector_1[1]
    dz = vector_2[2] - vector_1[2]
    return max(dx, dy, dz)

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
    scroll_bar_margin_left = 0
    scroll_bar_margin_right = int(scroll_bar_margin_ratio * img_width)
    scroll_bar_margin_top = 0
    scroll_bar_margin_bottom = int(scroll_bar_margin_ratio * img_height)
    
    if scroll_direction == "vertical":
        overlap_w = img_width - scroll_bar_margin_left - scroll_bar_margin_right
        overlap_h = min(img_height - offset, img_height_2)
        overlap_1_lefttop = scroll_bar_margin_left, offset  # image_1
        overlap_2_lefttop = scroll_bar_margin_left, 0       # image_2
    elif scroll_direction == "horizontal":
        overlap_w = min(img_width - offset, img_width_2)
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
            pixel_diffs.append(calc_3d_vector_distance(rgb_1, rgb_2))  # 计算三维向量距离
            # pixel_diffs.append(calc_3d_max_distance(rgb_1, rgb_2))  # 计算三个维度差值的最大值

    # calculate average pixel difference （均值）
    return calc_avg(pixel_diffs)

    # calculate mean pixel difference （标准差）
    # return np.mean(pixel_diffs)


# 去白边
def remove_white_margin(img_2):
    pixels_2 = img_2.load()
    check_finished = False
    crop_area = (0, 0, 0, 0)

    if scroll_direction == "vertical":
        for y in range(img_height_2):
            pixels_diff_this_line = []
            for x in range(img_width_2):
                rgb_2 = pixels_2[x, y]
                pixels_diff_this_line.append(calc_3d_vector_distance((255,255,255), rgb_2))  # 计算三维向量距离
            if calc_avg(pixels_diff_this_line) > white_margin_pixel_diff_avg_threshold:
                check_finished = True
                break
        if check_finished:
            crop_area = (0, y, img_width_2, img_height_2)

    elif scroll_direction == "horizontal":
        for x in range(img_width_2):
            pixels_diff_this_line = []
            for y in range(img_height_2):
                rgb_2 = pixels_2[x, y]
                pixels_diff_this_line.append(calc_3d_vector_distance((255,255,255), rgb_2))  # 计算三维向量距离
            if calc_avg(pixels_diff_this_line) > white_margin_pixel_diff_avg_threshold:
                check_finished = True
                break
        if check_finished:
            crop_area = (x, 0, img_width_2, img_height_2)
    
    if not crop_area == (0, 0, 0, 0):
        img_2 = img_2.crop(crop_area)

    return img_2
    

def img_merge(img_1, img_2, output_path, scroll_direction):

    # save as new image
    img_1.save("screenshot_1.png")
    img_2.save("screenshot_2.png")

    # pixels: 2-dimension array
    pixels_1 = img_1.load()
    pixels_2 = img_2.load()
    # r, g, b = pixels_1[0, 0]
    # print(r, g, b)


    # iterate offset and find minimum pixel difference
    find_offset = False
    if scroll_direction == "vertical":
        offset_min_limit = img_height - img_height_2  # to speed up
        offset_max_limit = int(img_height * (1 - min_overlap_ratio))
    elif scroll_direction == "horizontal":
        offset_min_limit = img_width - img_width_2  # to speed up
        offset_max_limit = int(img_width * (1 - min_overlap_ratio))
    overlap_per_offset = []
    for offset in range(offset_min_limit, offset_max_limit):
        # if calc_overlap_diff(scroll_direction, pixels_1, pixels_2, img_width, img_height, offset) <= pixel_diff_avg_threshold:
        #     find_offset = True
        #     break
        
        overlap_per_offset.append(calc_overlap_diff(scroll_direction, pixels_1, pixels_2, img_width, img_height, offset))
        min_overlap = min(overlap_per_offset)
        if min_overlap <= pixel_diff_avg_threshold:
            find_offset = True
            offset = offset_min_limit + overlap_per_offset.index(min_overlap)
        

    if not find_offset:
        print("Merging image failed!")
        exit(-1)
    else:
        print("offset = %d, merging image..." % offset)

    # calculate size of merged image
    if scroll_direction == "vertical":
        x, y = img_width, max(img_height, img_height_2 + offset)
    elif scroll_direction == "horizontal":
        x, y = max(img_width, img_width_2 + offset), img_height

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

    img_merged.save(output_path)



if __name__ == "__main__":

    if test_mode:
        # size of a single snapshot
        img_width = int(1920 / 3)   # 测试用，可以修改
        img_height = int(1080 / 2)  # 测试用，可以修改

        # create snapshot as input
        img_1 = pyautogui.screenshot(region=[0, 0, img_width, img_height])  # x, y, w, h
        if scroll_direction == "vertical":
            img_2 = pyautogui.screenshot(region=[0, 360, img_width, img_height])  # vertical test
        else:
            img_2 = pyautogui.screenshot(region=[420, 0, img_width, img_height])  # horizontal test

        img_merge(img_1, img_2, output_path, scroll_direction)

    # working mode
    else:

        # 遍历输入文件夹
        input_dir = "crop_output"
        output_dir = "merge_output"
        input_images = []
        output_images = []

        print("Getting inputs...")
        for root, dirs, files in os.walk(input_dir):
            for f in files:
                file_name, file_extension = os.path.splitext(f)  # 使用os.path.splitext()获取文件名和扩展名
                if file_extension in (".png", ".jpg"):
                    print(f)
                    input_images.append(os.path.join(input_dir, f))
                    output_images.append(os.path.join(output_dir, file_name + "_merged" + file_extension))
        
        # 批量拼合图片
        print("\nMerging images...")
        shutil.copyfile(input_images[0], output_images[0])

        for i in range(len(input_images)):
            if i > 0:  # skip the first image
                print(output_images[i])
                img_1 = Image.open(output_images[i-1])
                # img_size = img_1.size # 大小/尺寸
                # img_format = img_1.format # 图像格式
                img_width = img_1.width # 图片的宽
                img_height = img_1.height # 图片的高

                img_2 = Image.open(input_images[i])
                img_width_2 = img_2.width
                img_height_2 = img_2.height

                if remove_img_2_white_margin:
                    img_2 = remove_white_margin(img_2)
                    img_width_2 = img_2.width
                    img_height_2 = img_2.height  # 更新去白边后的图2尺寸

                img_merge(img_1, img_2, output_images[i], scroll_direction)
                