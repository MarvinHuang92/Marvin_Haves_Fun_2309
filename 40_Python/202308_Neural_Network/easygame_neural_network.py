import torch    
from torch import nn
import matplotlib.pyplot as plt
# import numpy as np
import random

"""
# 该脚本基于 202308_Neural_Network/sine_regression.py 修改

# 函数拟合问题，输出连续值，参数 model_type = "fitting"
# 二分类问题，输出离散值 [0,1] 二选一，参数 model_type = "classification"
"""

model_type = "fitting"
# model_type = "classification"

"""
# 基本步骤：
# 1. 定义神经网络类 Network (包含中间层种类：线性 or 卷积，激活函数的选择)
# 2. 创建神经网络实例
# 3. 定义 loss 损失函数（取决于问题类型：线性、非线性），和优化器
# 4. 开始迭代，训练模型（找到使得 loss 最小的权重参数）
"""


# 定义神经网络类
from neural_network_template import Network, softmax_epoch


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
    if model_type == "fitting":
        x = [0,1,2,3,4,5,6,7,8,9]
        y = [0,1,0,1,0,1,0,1,0,1]
        pass
    elif model_type == "classification":
        x = []
        y = []
        for i in range(1,100):
            x.append(i)
            y.append(0.98+0.04*random.random())
        for i in range(201,300):
            x.append(i)
            y.append(-0.02+0.04*random.random())
        pass

    x_reshaped = []
    y_reshaped = []
    # 注意：对于分类问题使用的交叉熵函数，输入数组维度不同！
    # x是多维数组，两层中括号
    for x_i in x:
        x_reshaped.append([x_i,])
    if model_type == "fitting":
        # 拟合问题，y是多维数组
        for y_i in y:
            y_reshaped.append([y_i,])
    elif model_type == "classification":
        # 分类问题，y是一维数组，普通的list
        y_reshaped = y
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
    if model_type == "fitting":
        y = torch.Tensor(y_reshaped)
    elif model_type == "classification":
        y = torch.LongTensor(y_reshaped)  # LongTensor可以避免将整形转成float，否则交叉熵函数会报错
    # print(x)
    # print(y)

    # 训练模型
    n_features = 1          # 特征数（输入神经元数量，对应样本的 xy 坐标）
    n_hidden = 24           # 隐藏神经元数量
    if model_type == "fitting":
        n_classes = 1
    elif model_type == "classification":
        n_classes = 2           # 类别数（输出神经元数量，对应各个分类的概率）
    n_epochs = 20001        # 迭代次数
    if model_type == "fitting":
        learning_rate = 0.002   # 学习速率
    elif model_type == "classification":
        learning_rate = 0.01   # 学习速率
    n_print_loss = 500      # 每迭代n次，打印当前损失

    # 创建神经网络实例，对于拟合问题： 输入、输出神经元只有1个，分类问题： 输出神经元2个（类别数量）
    if model_type == "fitting":
        activation_func = torch.sigmoid  # 进行 sigmoid 激活
    elif model_type == "classification":
        activation_func = torch.relu    # relu激活函数
    model = Network(n_features, n_hidden, n_classes, activation_func)
    # 定义损失计算规则
    if model_type == "fitting":
        criterion = nn.MSELoss()  # 均方误差损失函数
    elif model_type == "classification":
        criterion = nn.CrossEntropyLoss()  # 交叉熵损失函数
    # Adam 优化器
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # 训练模型 - softmax 回归模型的循环迭代
    model= softmax_epoch(x, y, model, criterion, optimizer, n_epochs, n_print_loss)

    # 使用训练后的模型进行预测，并显示结果
    # 显示预测结果和真实值的区别
    # h 为模型预测结果，y 为数据样本结果
    if model_type == "fitting":
        h = model(x)  # 对于拟合问题，h和x格式相同
    elif model_type == "classification":
        h = []
        output = model(x)  # 使用传入的 model 预测结果
        # print(output)
        for h_i in output:
            # 选择概率最大的类别, torch.max(Tensor, dim) 其中 dim = -1（返回tensor的最小单位（行）的最大值索引）
            _, predicted = torch.max(h_i, -1)
            h.append(predicted.item())  # 添加到高度列表 h 中
    x = x.data.numpy()
    if model_type == "fitting":
        h = h.data.numpy()

    plt.scatter(x, h, color="orange")
    # 之前打印了 x_reshaped - y_reshaped，可以省略，两个图像重合
    # plt.scatter(x, y, color="blue")
    plt.show()
    