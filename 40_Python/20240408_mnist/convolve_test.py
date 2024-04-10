import torch

""" CNN = Convolve Neural Network 卷积神经网络 """

# 随机生存一组图片，格式 B, C, W, H
# 5张图片，3通道，长宽128
image = torch.randn(size=(5,3,28,28))
# print(image[0][0])

# 卷积的例子

# 输入通道 3
# 输出通道 10
# 卷积核 3*3，可以写作 3 或 [3,3] 
# 步长 2，亦可写作 [2,2]
# 补偿方式：边缘补偿的宽度 (padding>0)，或不补偿边缘 (padding=0)
conv2d = torch.nn.Conv2d(in_channels=3, out_channels=10, kernel_size=3, stride=2, padding=1)
image_new = conv2d(image)
print(image_new.shape)
print(image_new[0][0])


# 池化的例子
pool = torch.nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
image_pooled = pool(image_new)
print(image_pooled.shape)
print(image_pooled[0][0])

# 全局池化，只有一个参数，输出小矩阵的尺寸，可以是1，大于1时会对全图做平均切割
# pool = torch.nn.AdaptiveAvgPool2d(output_size=1)
pool = torch.nn.AdaptiveMaxPool2d(output_size=2)
image_pooled = pool(image_new)
print(image_pooled.shape)
print(image_pooled[0][0])
