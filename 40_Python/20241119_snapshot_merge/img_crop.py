import os
from PIL import Image

import locateMouse as lm

def img_crop(input_path, output_path, crop_area):
    # 打开图片文件
    img = Image.open(input_path)
    # 裁剪图片
    img_cropped = img.crop(crop_area)
    # 保存裁剪后的图片
    img_cropped.save(output_path)

if __name__ == "__main__":
    
    # 定义裁剪区域的四元组（左上角x, 左上角y, 右下角x, 右下角y）
    # crop_area = (20, 594, 1094, 1560)
    crop_area = (20, 612, 1091, 1540)

    print("如需重新选取裁剪区域，请先打开图片，并将本程序框拖动到不遮挡图片的位置，再输入字符...\n")
    print("当前裁剪区域为： " + str(crop_area))
    a = input("是否重新选取裁剪区域？\n- 直接回车：不重新选取\n- 输入任意字符：重新选取\n")
    if a.strip() != "":
        crop_area = lm.main()

    # 遍历输入文件夹
    input_dir = "02_crop_input"
    output_dir = "02_crop_output"
    input_images = []
    output_images = []

    for root, dirs, files in os.walk(input_dir):
        for f in files:
            file_name, file_extension = os.path.splitext(f)  # 使用os.path.splitext()获取文件名和扩展名
            if file_extension in (".png", ".jpg"):
                print(f)
                input_images.append(os.path.join(input_dir, f))
                output_images.append(os.path.join(output_dir, file_name + "_cropped" + file_extension))
    
    # 批量裁剪图片
    for i in range(len(input_images)):
        img_crop(input_images[i], output_images[i], crop_area)
    
    os.system('start "" ' + output_dir)
