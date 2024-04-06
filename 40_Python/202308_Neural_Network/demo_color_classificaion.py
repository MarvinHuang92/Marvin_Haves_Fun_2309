from sklearn.datasets import make_blobs, make_circles
import torch
from torch import nn
import matplotlib.pyplot as plt
import numpy as np

# https://pytorch-cn.readthedocs.io/zh/latest/package_references/torch-nn/
# https://blog.51cto.com/u_16099263/6762878


# 每种颜色的样本点数量
SAMPLE_NUM = 250

# Create data
def make_data(num):
    # 保持样本的随机数种子固定，便于评估不同神经网络性能
    np.random.seed(0)
    red, _ = make_blobs(n_samples=num, centers=[[0, 0]], cluster_std=0.15)  # 正态分布堆，1个，在正中间
    green, _ = make_circles(n_samples=num, noise=0.02, factor=0.7)          # 环状分布
    blue, _ = make_blobs(n_samples=num, centers=[[-1.2, -1.2],
                                                 [-1.2, 1.2],
                                                 [1.2, -1.2],
                                                 [1.2, 1.2]], cluster_std=0.2)  # 正态分布堆，4个角
    return red, green, blue


# 定义神经网络类
from neural_network_template import Network, Network_2_hidden_layer, softmax_epoch

# 绘制决策边界的函数
def draw_decision_boundary(minx1, maxx1, minx2, maxx2, resolution, model):
    # 生成网格数据点，网格越细，等高线的分辨率越高
    xx1, xx2 = np.meshgrid(np.arange(minx1, maxx1, resolution), np.arange(minx2, maxx2, resolution))
    # 设置 x1s, x2s, z 表示数据点的横纵坐标和预测结果
    x1s = xx1.ravel()
    x2s = xx2.ravel()
    z = list()  # z 是一个列表
    for x1, x2, in zip(x1s, x2s):  # 遍历全部样本
        # 将样本转换为张量
        test_point = torch.FloatTensor([[x1, x2]])
        output = model(test_point)  # 使用传入的 model 预测结果
        # 选择概率最大的类别
        _, predicted = torch.max(output, 1)
        z.append(predicted.item())  # 添加到高度列表 z 中
    # 将 z 设置回和 xx1 相同格式
    z = np.array(z).reshape(xx1.shape)

    return xx1, xx2, z

if __name__ == "__main__":
    red, green, blue = make_data(SAMPLE_NUM)

    # create a drawboard
    board = plt.figure()
    axis = board.add_subplot(1,1,1)
    axis.set(xlim=[-1.5, 1.5], ylim=[-1.5, 1.5], title="Neural Network", xlabel="x1", ylabel="x2")

    # draw data on the board
    plt.scatter(red[:, 0], red[:, 1], color="red")
    plt.scatter(green[:, 0], green[:, 1], color="green")
    plt.scatter(blue[:, 0], blue[:, 1], color="blue")
    # plt.show()

    # 训练模型
    n_features = 2          # 特征数（输入神经元数量，对应样本的 xy 坐标）
    n_hidden = 5            # 隐藏神经元数量
    n_classes = 3           # 类别数（输出神经元数量，对应三种颜色的概率）
    n_epochs = 5001         # 迭代次数
    learning_rate = 0.1     # 学习速率
    n_print_loss = 500      # 每迭代n次，打印当前损失

    # 将样本从 numpy 数组，转换为张量形式
    red = torch.FloatTensor(red)
    green = torch.FloatTensor(green)
    blue = torch.FloatTensor(blue)
    # 组合成为训练数据 data
    data = torch.cat((red, green, blue), dim=0)
    
    # print(data)
    # data的格式：(两层括号[[]])
    # tensor[
    #     [红点的xy坐标]*N,
    #     [绿点的xy坐标]*N,
    #     [蓝点的xy坐标]*N,
    # ]


    # 设置 label 保存三种样本标签，使用数值 012 分别对应三种颜色
    label = torch.LongTensor([0] * len(red) + [1] * len(green) + [2] * len(blue))
    
    # print(label)
    # label的格式：(一层括号[])
    # [
    #     0*N,
    #     1*N,
    #     2*N,
    # ]

    # 创建神经网络实例
    # model = Network(n_features, n_hidden, n_classes, torch.relu)  # relu激活函数
    model = Network_2_hidden_layer(n_features, n_hidden, 3, n_classes, torch.relu)  # relu激活函数
    # 定义损失计算规则
    criterion = nn.CrossEntropyLoss()  # 交叉熵损失函数
    # Adam 优化器
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # 训练模型 - softmax 回归模型的循环迭代
    model= softmax_epoch(data, label, model, criterion, optimizer, n_epochs, n_print_loss)
        # print(data[0], output[0], label[0])                                     # one of red sample points
        # print(data[SAMPLE_NUM], output[SAMPLE_NUM], label[SAMPLE_NUM])          # one of green sample points
        # print(data[SAMPLE_NUM*2], output[SAMPLE_NUM*2], label[SAMPLE_NUM*2])    # one of blue sample points

    # 绘制决策边界，网格点的 xy 边界应大于数据点的 xy 边界
    xx1, xx2, z = draw_decision_boundary(-3, 3, -3, 3, 0.03, model)
    plt.contour(xx1, xx2, z, colors=['orange'])
    plt.show()