import sys
import torch    
from torch import nn
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # 用于绘制三维图像
# import random

"""
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
sys.path.append("../202308_Neural_Network")  # 跨目录引用模块，先将所在目录添加至系统路径
from neural_network_template import Network, softmax_epoch





"""
# 绘制二元函数图像的示例
 
def f(x, y):  # 设置函数表达式
    return np.sin(x) + np.sin(y) - np.sin(x+y)
"""
    
def plot_3d_figure(X, Y, Z, x_label="x", y_label="y", z_label="z", title=""):
    fig = plt.figure()
    ax = plt.axes(projection='3d')  # 设置为3维
    ax.plot_surface(X, Y, Z, cmap='viridis')
    ax.set_xlabel(x_label)  # 设置坐标轴标签
    ax.set_ylabel(y_label)
    ax.set_zlabel(z_label)
    plt.title(title)  # 在图中显示函数表达式
    plt.show()

""" 
def draw_fxy_figure():
    x = np.linspace(-2*np.pi, 2*np.pi, 100)  # 设置变量范围, 100为样本点数
    y = np.linspace(-2*np.pi, 2*np.pi, 100)
    X, Y = np.meshgrid(x, y)
    Z = f(X, Y)
    plot_3d_figure(X, Y, Z, title="f(x,y)=sinx+siny-sin(x+y)")

"""



if __name__ == "__main__":

    # 生成数据样本
    # 从 02_nn_sample_data_full.csv 读取

    """先简化一下, 只有两个x输入和一个输出"""

    contents = []
    with open("02_nn_sample_data_full.csv") as f:
        contents = f.readlines()
        f.close()

    # 输入： NN_state 的前两位
    # 输出： 一个 reward 标量
    x = []
    y = []
    num = 0
    MAX_LINE = 10  # 只取前 MAX_LINE 行数据，节省时间
    for line in contents:
        if num < MAX_LINE:
            line = line.strip().split(',')
            x.append([int(line[0].strip()), int(line[52].strip())])
            y.append([int(line[-1].strip())])
        num += 1
    # print(x)
    # print(y)

    
    """上面的数据构造形式，和 x_reshaped y_reshaped 格式一致，不需要重复转换格式"""
    x_reshaped = x
    y_reshaped = y

    # x_reshaped = []
    # y_reshaped = []
    # 注意：对于分类问题使用的交叉熵函数，输入数组维度不同！
    # x是多维数组，两层中括号
    # for x_i in x:
    #     x_reshaped.append([x_i,])
    # if model_type == "fitting":
    #     # 拟合问题，y是多维数组
    #     for y_i in y:
    #         y_reshaped.append([y_i,])
    # elif model_type == "classification":
    #     # 分类问题，y是一维数组，普通的list
    #     y_reshaped = y
    # print(x_reshaped)
    # print(y_reshaped)


    # 预览 X-Y 数据, 注意是三维图像 {x0, x1} -> y
    x0_grid = []
    x1_grid = []
    for x_i in x:
        x0_grid.append(x_i[0])
        x1_grid.append(x_i[1])
    X0, X1 = np.meshgrid(x0_grid, x1_grid)
    # print(x0_grid)
    # print(X0)
    # print(x1_grid)
    # print(X1)
    
    y_grid = []
    for y_i in y:
        y_grid.append(y_i[0])
    Y, _ = np.meshgrid(y_grid, [0]*MAX_LINE)
    # print(y_grid)
    # print(Y)

    plot_3d_figure(X0, X1, Y, x_label="x0", y_label="x1", z_label="y", title="{x0, x1} -> y")

    # 将样本转换为张量形式
    x = torch.Tensor(x_reshaped)
    if model_type == "fitting":
        y = torch.Tensor(y_reshaped)
    elif model_type == "classification":
        y = torch.LongTensor(y_reshaped)  # LongTensor可以避免将整形转成float，否则交叉熵函数会报错
    # print(x)
    # print(y)


    # 训练模型
    n_features = 2          # 特征数（输入神经元数量，对应样本的 xy 坐标）
    n_hidden = 75           # 隐藏神经元数量
    if model_type == "fitting":
        n_classes = 1
    elif model_type == "classification":
        n_classes = 2           # 类别数（输出神经元数量，对应各个分类的概率）
    n_epochs = 5001        # 迭代次数
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
    
    # 绘制 X-H 图像
    h_grid = []
    for h_i in h:
        h_grid.append(h_i[0])
    H, _ = np.meshgrid(h_grid, [0]*MAX_LINE)
    plot_3d_figure(X0, X1, H, x_label="x0", y_label="x1", z_label="h", title="{x0, x1} -> h")
    plot_3d_figure(X0, X1, Y-H, x_label="x0", y_label="x1", z_label="y-h", title="{x0, x1} -> y-h")

    