# -*- coding: utf-8 -*-

""" test of autoGUI """

__author__ = 'Marvin Huang'

import pyautogui as pag

pag.PAUSE = 1               # 每个autogui功能都自动暂停1秒，防止失控
pag.FAILSAFE = False        # 禁用鼠标快速移动到左上角的“自动防故障”功能

# width, height = pag.size()  # 获得当前屏幕分辨率
# pag.moveTo(500, 500, duration = 0.5)
# pag.moveRel(50, -50, duration = 0.5)


print("Press Ctrl+C to quit.")

try:
    while True:
        x, y = pag.position()                                               # 获得鼠标位置
        positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)    # 右对齐，总是显示4位数的宽度
        pixelColor = pag.screenshot().getpixel((x, y))
        positionStr += ' RGB: (' + str(pixelColor[0]).rjust(3) + ', ' + str(pixelColor[1]).rjust(3)\
                       + ', ' + str(pixelColor[2]).rjust(3) + ')'           # 添加当前位置的像素颜色
        print(positionStr, end='')                                          # end=''表示不要在结尾换行
        print('\b' * len(positionStr), end='', flush=True)                  # 打印若干个退格，相当于擦除刚才写的字

except KeyboardInterrupt:
    print('\nDone...')
    # print(pag.locateOnScreen("sample_search.png"))                        # 总是找不到，怀疑是截屏后会让颜色有变化
