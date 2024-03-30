import torch
from torch import nn
import matplotlib.pyplot as plt
# import numpy as np

# 该脚本基于 202308_Neural_Network/sine_regression.py 修改
# 函数拟合问题，输出连续值

# 基本步骤：
# 1. 定义神经网络类 Network (包含中间层种类：线性 or 卷积，激活函数的选择)
# 2. 创建神经网络实例
# 3. 定义 loss 损失函数（取决于问题类型：线性、非线性），和优化器
# 4. 开始迭代，训练模型（找到使得 loss 最小的权重参数）


# 定义神经网络类
from template_neural_network import Network, softmax_epoch


if __name__ == "__main__":
    
    # 生成数据样本
    # 从 easygame_record.csv 读取
    contents = []
    with open("easygame_record.csv") as f:
        contents = f.readlines()
        f.close()
    # 去掉表格第一行
    contents.pop(0)

    # 输入： game_value
    # 输出： p2_choice（给AI学习用）
    x = []
    y = []
    # 当 p2_choice 有数据时
    for line in contents:
        line = line.strip().split(',')
        if line[3] != 'None':
            # 根据当前回合结果和 p2_choice，反推 p2_choice 之前的 game_value
            x.append(int(line[-1]) - int(line[3]))
            y.append(int(line[3]))
    # print(x)
    # print(y)
            
    # 换成简单的函数
    # x = [0,1,2,3,4,5,6,7,8,9]
    # y = [0,1,0,1,0,1,0,1,0,1]

    x_reshaped = []
    y_reshaped = []
    for x_i in x:
        x_reshaped.append([x_i,])
    for y_i in y:
        y_reshaped.append([y_i,])
    # print(x_reshaped)
    # print(y_reshaped)

    # create a drawboard - 定义画板格式，这步骤可以省略
    # board = plt.figure()
    # axis = board.add_subplot(1,1,1)
    # axis.set(xlim=[-1.5, 1.5], ylim=[-1.5, 1.5], title="Neural Network", xlabel="x1", ylabel="x2")

    # 预览 X-Y 数据
    plt.scatter(x_reshaped, y_reshaped, color="green")
    # plt.show()

    # 将样本转换为张量形式
    x = torch.Tensor(x_reshaped)
    y = torch.Tensor(y_reshaped)
    # print(x)
    # print(y)

    # 训练模型
    n_hidden = 10           # 隐藏神经元数量
    n_epochs = 10001        # 迭代次数
    learning_rate = 0.001   # 学习速率
    n_print_loss = 1000     # 每迭代n次，打印当前损失

    # 创建神经网络实例，输入、输出神经元只有1个
    model = Network(1, n_hidden, 1, torch.sigmoid) # 进行 sigmoid 激活
    # 定义损失计算规则
    criterion = nn.MSELoss()  # 均方误差损失函数
    # Adam 优化器
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # 训练模型 - softmax 回归模型的循环迭代
    model= softmax_epoch(x, y, model, criterion, optimizer, n_epochs, n_print_loss)

    # 使用训练后的模型进行预测，并显示结果
    # 显示预测结果和真实值的区别
    # h 为模型预测结果，y 为数据样本结果
    h = model(x)
    x = x.data.numpy()
    h = h.data.numpy()

    plt.scatter(x, h, color="orange")
    # 之前打印了 x_reshaped - y_reshaped，可以省略，两个图像重合
    # plt.scatter(x, y, color="blue")
    plt.show()
    