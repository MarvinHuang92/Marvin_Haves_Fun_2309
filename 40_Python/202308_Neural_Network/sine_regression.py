from sklearn.datasets import make_blobs, make_circles
import torch
from torch import nn
import matplotlib.pyplot as plt
import numpy as np

# https://www.bilibili.com/video/BV1kX4y1s7VC/?spm_id_from=333.337.search-card.all.click&vd_source=9508c917b95f0be9ba14d698b0978a04
# http://playground.tensorflow.org/

# 基本步骤：
# 1. 定义神经网络类 Network (包含中间层种类：线性 or 卷积，激活函数的选择)
# 2. 创建神经网络实例
# 3. 定义 loss 损失函数（取决于问题类型：线性、非线性），和优化器
# 4. 开始迭代，训练模型（找到使得 loss 最小的权重参数）


# 定义神经网络类
from template_neural_network import Network, softmax_epoch

if __name__ == "__main__":
    
    # 生成数据样本
    x = np.arange(0.0, 1.0, 0.01)
    y = np.sin(2 * np.pi * x)
    x = x.reshape(100, 1)
    y = y.reshape(100, 1)

    # create a drawboard - 定义画板格式，这步骤可以省略
    # board = plt.figure()
    # axis = board.add_subplot(1,1,1)
    # axis.set(xlim=[-1.5, 1.5], ylim=[-1.5, 1.5], title="Neural Network", xlabel="x1", ylabel="x2")

    # draw data on the board
    plt.scatter(x, y, color="green")
    # plt.show()

    # 将样本从 numpy 数组，转换为张量形式
    x = torch.Tensor(x)
    y = torch.Tensor(y)

    # 训练模型
    n_hidden = 5           # 隐藏神经元数量
    n_epochs = 20001        # 迭代次数
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
    plt.show()