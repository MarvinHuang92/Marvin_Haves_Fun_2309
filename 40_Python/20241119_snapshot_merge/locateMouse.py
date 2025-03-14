# -*- coding: utf-8 -*-

""" test of autoGUI """

__author__ = 'Marvin Huang'

# import pyautogui as pag
import pynput.mouse as pm

# pag.PAUSE = 1               # 每个autogui功能都自动暂停1秒，防止失控
# pag.FAILSAFE = False        # 禁用鼠标快速移动到左上角的“自动防故障”功能

# width, height = pag.size()  # 获得当前屏幕分辨率
# pag.moveTo(500, 500, duration = 0.5)  # 移动鼠标
# pag.moveRel(50, -50, duration = 0.5)


# print("Press Ctrl+C to quit.")

# try:
#     while True:
#         x, y = pag.position()                                               # 获得鼠标位置
#         positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)    # 右对齐，总是显示4位数的宽度
#         pixelColor = pag.screenshot().getpixel((x, y))
#         positionStr += ' RGB: (' + str(pixelColor[0]).rjust(3) + ', ' + str(pixelColor[1]).rjust(3)\
#                        + ', ' + str(pixelColor[2]).rjust(3) + ')'           # 添加当前位置的像素颜色
#         print(positionStr, end='')                                          # end=''表示不要在结尾换行
#         print('\b' * len(positionStr), end='', flush=True)                  # 打印若干个退格，相当于擦除刚才写的字

# except KeyboardInterrupt:
#     print('\nDone...')
#     # print(pag.locateOnScreen("sample_search.png"))                        # 总是找不到，怀疑是截屏后会让颜色有变化

####################################################################

# global config
g_min_crop_range = 20  # 截图长宽的最小值（像素）

g_counter = 0  # 点击坐标的计数器，from 0 to 3
g_coordinates = []  # 存储点击的坐标
g_print_flag = True

def on_click(x, y, button, pressed):
    global g_counter
    global g_coordinates
    global g_print_flag
    if g_print_flag:
        if g_counter == 0:
            print("全图左上角坐标：     ", end='')  # end=''表示不要在结尾换行
        elif g_counter == 1:
            print("全图右下角坐标：     ", end='')
        elif g_counter == 2:
            print("裁剪区域左上角坐标： ", end='')
        elif g_counter == 3:
            print("裁剪区域右下角坐标： ", end='')
        g_print_flag = False
    if pressed:
        print(str(x).rjust(4) + ", " + str(y).rjust(4))    # 右对齐，总是显示4位数的宽度
        # print(button)  # 显示左键，右键或中键
        g_coordinates.append([x, y])
        g_counter += 1
        g_print_flag = True
    if g_counter >= 4:
        return False  # 输出false会结束监听
    # if not pressed:
    #     return False  # 输出false会结束监听


def main():
    print("请确保图片可以在屏幕上完整显示，然后依次点击：")
    print("1.图片左上角，2.图片右下角，3.裁剪区域左上角，4.裁剪区域右下角")

    with pm.Listener(on_click=on_click) as listener:
        listener.join()

    ratio = input("图片显示比例为(默认100%): ")
    if ratio.strip() == "":
        ratio = 1.0
    else:
        try:
            ratio = float(ratio) / 100.0
        except:
            ratio = 1.0
    
    # print(ratio)

    # print(g_coordinates)
    img_cood_1, img_cood_2, crop_cood_1, crop_cood_2 = g_coordinates

    # 以下为相对屏幕的坐标
    img_x_min = min(img_cood_1[0], img_cood_2[0])
    # img_x_max = max(img_cood_1[0], img_cood_2[0])
    img_y_min = min(img_cood_1[1], img_cood_2[1])
    # img_y_max = max(img_cood_1[1], img_cood_2[1])
    crop_x_min = min(crop_cood_1[0], crop_cood_2[0])
    crop_x_max = max(crop_cood_1[0], crop_cood_2[0])
    crop_y_min = min(crop_cood_1[1], crop_cood_2[1])
    crop_y_max = max(crop_cood_1[1], crop_cood_2[1])

    # 计算裁剪区域的相对坐标，并除以显示比例，再取整
    rel_x_min = int(max(0, (crop_x_min - img_x_min)) / ratio)
    rel_y_min = int(max(0, (crop_y_min - img_y_min)) / ratio)
    rel_x_range = int(max(g_min_crop_range, (crop_x_max - crop_x_min)) / ratio)
    rel_y_range = int(max(g_min_crop_range, (crop_y_max - crop_y_min)) / ratio)
    rel_x_max = rel_x_min + rel_x_range
    rel_y_max = rel_y_min + rel_y_range

    # 输出裁剪参数：相对坐标左上角x,y，右下角x,y
    return [rel_x_min, rel_y_min, rel_x_max, rel_y_max]


if __name__ == "__main__":
    print(main())
    # 20, 594, 1094, 1560

