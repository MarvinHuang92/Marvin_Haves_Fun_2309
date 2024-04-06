import sys
import torch    
from torch import nn
import matplotlib.pyplot as plt
from math import sqrt
# import numpy as np
# import random

"""
# 基本步骤：
# 1. 定义神经网络类 Network (包含中间层种类：线性 or 卷积，激活函数的选择)
# 2. 创建神经网络实例
# 3. 定义 loss 损失函数（取决于问题类型：线性、非线性），和优化器
# 4. 开始迭代，训练模型（找到使得 loss 最小的权重参数）

# note: 模型创建好后，不可调整：神经元数量，激活函数，样本集维度（和输入层数量一致）
#       训练过程中可以调整的: 样本集内容 (更换同等维度的新样本), 学习速率 (当error不再减小或有波动, 降低学习速率)
"""

# 获取参数
from neural_network_run import *

# 定义神经网络类，和一些辅助函数
sys.path.append("../202308_Neural_Network")  # 跨目录引用模块，先将所在目录添加至系统路径
from neural_network_template import Network, Network_2_hidden_layer, softmax_epoch, calcMSE, plot_3d_figure


# 样本区间初始化
sample_start = 0
sample_end = 0
sample_index_range = []

# 计算样本区间
def calcSampleRange(current_batch):
    global sample_start, sample_end, sample_index_range
    if task_type == "prediction":
        sample_start = sample_start_pr + batchsize_pr * (current_batch - 1)
        sample_end = sample_start + batchsize_pr
    else:
        sample_start = sample_start_tr + batchsize_tr * (current_batch - 1)
        sample_end = sample_start + batchsize_tr
    sample_index_range = range(sample_start, sample_end)
    print("Sample index: [%d-%d]\n" % (sample_start, sample_end - 1))


# 生成数据样本
def get_data(plot):
        
    # 从 csv 读取
    contents = []
    with open(csv_input) as f:
        contents = f.readlines()
        f.close()

    # 输入： NN_state 的 0-63 位
    # 输出： 一个 reward 标量
    x = []
    y = []
    
    for i in sample_index_range:
        line = contents[i].strip().split(',')
        x_i = []
        for i in range(input_col_max):
            x_i.append(int(line[i].strip()))
        x.append(x_i)
        y.append([float(line[-1].strip())])
    # print(x)
    # print(y)
        
    # 上面的数据构造形式，和 x_reshaped y_reshaped 格式一致，不需要重复转换格式
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


    """
    # 超过三维的图像, 无法预览

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
    Y, _ = np.meshgrid(y_grid, [0]*(sample_end-sample_start))
    # print(y_grid)
    # print(Y)

    plot_3d_figure(X0, X1, Y, x_label="x0", y_label="x1", z_label="y", title="{x0, x1} -> y")
    """

    # 预览y的分布
    if plot:
        plt.scatter(sample_index_range, y, color="green")
        # plt.show()

    # 将样本转换为张量形式
    x = torch.Tensor(x_reshaped)
    if model_type == "fitting":
        y = torch.Tensor(y_reshaped)
    elif model_type == "classification":
        y = torch.LongTensor(y_reshaped)  # LongTensor可以避免将整形转成float，否则交叉熵函数会报错
    # print(x)
    # print(y)
        
    return x, y


# 创建新模型
def create_model():
    # 模型参数从全局变量中获取

    # 创建神经网络实例
    if model_type == "fitting":
        # activation_func = torch.sigmoid  # 进行 sigmoid 激活
        activation_func = torch.relu  # relu 激活，计算更快
    elif model_type == "classification":
        activation_func = torch.relu    # relu激活函数
    model = Network_2_hidden_layer(n_features, n_hidden, n_hidden_2, n_classes, activation_func)

    return model

# 加载已有的模型
def load_model():
    print("Loading model: %s\n" % model_path)
    return torch.load(model_path)

# 保存模型
def save_model(model):
    print("\nSaving model: %s" % model_path)
    torch.save(model, model_path)     

# 训练模型 (lr=learning_rate)
def training_model(model, lr, x, y):
    # 定义损失计算规则
    if model_type == "fitting":
        criterion = nn.MSELoss()  # 均方误差损失函数
    elif model_type == "classification":
        criterion = nn.CrossEntropyLoss()  # 交叉熵损失函数
    # Adam 优化器
    optimizer = torch.optim.Adam(model.parameters(), lr)

    print("Learning Rate: %f\n" % lr)
    
    # 开始 softmax 回归模型的循环迭代，并返回训练好的模型
    return softmax_epoch(x, y, model, criterion, optimizer, n_epochs, n_print_loss)

    
# 使用模型进行预测，并显示结果
def predict(model, x, y, plot):
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
    
    """
    # 超过三维图像无法绘制

    # 绘制 X-H 图像
    h_grid = []
    for h_i in h:
        h_grid.append(h_i[0])
    H, _ = np.meshgrid(h_grid, [0]*sample_end)
    plot_3d_figure(X0, X1, H, x_label="x0", y_label="x1", z_label="h", title="{x0, x1} -> h")
    plot_3d_figure(X0, X1, Y-H, x_label="x0", y_label="x1", z_label="y-h", title="{x0, x1} -> y-h")
    """

    # print(h)
    error = []
    for e in (y - h):
        error += e

    # 打印 y-h 的均方差
    mse = calcMSE(error)
    print("\nMean Square Error: %f" % mse)
    print("Root Mean Square Error: %f\n" % sqrt(mse))

    if plot:
        plt.scatter(sample_index_range, h, color="orange")
        # plt.scatter(sample_index_range, y-h, color="blue")
        plt.show()


def main(task_type, current_batch, plot):
    # 判断任务类型
    if task_type == "training_new_model":
        model_input = "create_new_model"
        training_model_switch = True
    elif task_type == "training_existing_model":
        model_input = "load_existing_model"
        training_model_switch = True
    elif task_type == "prediction":
        model_input = "load_existing_model"
        training_model_switch = False

    # 计算样本区间
    calcSampleRange(current_batch)

    # 生成数据样本
    x, y = get_data(plot)

    # 创建新模型
    if model_input == "create_new_model":
        model = create_model()
        lr = learning_rate * 10  # 初次创建的模型，学习速率*10
    # 加载已有模型
    elif model_input == "load_existing_model":
        model = load_model()
        lr = learning_rate
    
    # 训练并保存模型
    if training_model_switch:
        model = training_model(model, lr, x, y)
        save_model(model)

    # 预测新数据
    predict(model, x, y, plot)
    


if __name__ == "__main__":

    # 请在 neural_network_run.py 中运行程序

    # main(task_type, current_batch=1, plot)
    pass

    