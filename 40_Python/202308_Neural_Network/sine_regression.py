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


# 定义神经网络类（激活函数，隐藏层数量不变时，可以直接复用）
class Network(nn.Module):
    # 重载初始化函数（构造函数）
    # 传入参数：输入层，隐藏层，输出层
    def __init__(self, n_in, n_hidden, n_out):
        super().__init__()  # 首先调用父类的初始化函数
        # 然后新增步骤，创建两个线性层
        self.layer1 = nn.Linear(n_in, n_hidden)
        self.layer2 = nn.Linear(n_hidden, n_out)

    # 定义前向传播
    def forward(self, x):
        x = self.layer1(x)  # 计算 layer1 结果
        x = torch.sigmoid(x)  # 进行 sigmoid 激活 - 解决不同问题，使用的激活函数也不同
        return self.layer2(x)  # 返回 layer2 结果

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

    # 创建神经网络实例，输入、输出神经元只有1个
    model = Network(1, n_hidden, 1)
    # 定义损失计算规则
    criterion = nn.MSELoss()  # 均方误差损失函数
    # Adam 优化器
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # 进入 softmax 回归模型的循环迭代
    for epoch in range(n_epochs):
        y_pred = model(x)  # 调用forward 方法，预测输出

        # 计算预测值 y_pred 与真实值 y 之间的损失 loss
        loss = criterion(y_pred, y)
        loss.backward()  # 通过自动微分计算损失函数关于模型参数的梯度
        optimizer.step()  # 更新模型参数，使得损失函数减小
        optimizer.zero_grad()  # 将梯度清零，用于下一次迭代

        # 模型的每一次迭代，都由前向传播，和反向传播组成
        if epoch % 1000 == 0:
            # 每迭代 1000 次，打印当前损失
            print("%d iterations: loss = %.4lf" % (epoch, loss.item()))

    # 显示预测结果和真实值的区别
    h = model(x)
    x = x.data.numpy()
    h = h.data.numpy()
    plt.scatter(x, h, color="orange")
    plt.show()