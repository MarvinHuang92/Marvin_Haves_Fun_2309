import os
from PIL import Image

def img_rotate(input_path, output_path, rotate_angle="r_90"):
    img = Image.open(input_path)
    if rotate_angle == "r_90":
        img_rotated = img.transpose(Image.ROTATE_270) # 顺时针旋转90度
    elif rotate_angle == "180":
        img_rotated = img.transpose(Image.ROTATE_180) # 旋转180度
    elif rotate_angle == "l_90":
        img_rotated = img.transpose(Image.ROTATE_90)  # 逆时针旋转90度
    else:
        img_rotated = img
        print("Invalid iput angle!")
    # img_rotated.show()
    img_rotated.save(output_path)

if __name__ == "__main__":
    
    # 定义旋转方向
    rotate_angle_candidates = ["r_90", "180", "l_90"]

    while True:
        print("请选择旋转方向：")
        print("1. 顺时针90度")
        print("2. 180度")
        print("3. 逆时针90度")
        a = input("")
        if a.strip() in ["1", "2", "3"]:
            rotate_angle = rotate_angle_candidates[int(a.strip()) - 1]
            break

    # 遍历输入文件夹
    input_dir = "01_rotate_input"
    output_dir = "01_rotate_output"
    input_images = []
    output_images = []

    for root, dirs, files in os.walk(input_dir):
        for f in files:
            file_name, file_extension = os.path.splitext(f)  # 使用os.path.splitext()获取文件名和扩展名
            if file_extension in (".png", ".jpg"):
                print(f)
                input_images.append(os.path.join(input_dir, f))
                output_images.append(os.path.join(output_dir, f))  # 保持文件名不变
    
    # 批量旋转图片
    for i in range(len(input_images)):
        img_rotate(input_images[i], output_images[i], rotate_angle)

    os.system('start "" ' + output_dir)
    