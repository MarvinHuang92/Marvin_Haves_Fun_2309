import sys
import torch    
from torch import nn
import matplotlib.pyplot as plt
from math import sqrt
import numpy as np
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
from number_classification import *

# 定义神经网络类，和一些辅助函数
sys.path.append("../202308_Neural_Network")  # 跨目录引用模块，先将所在目录添加至系统路径
from neural_network_template import Network_2_hidden_layer_for_mnist, softmax_epoch, calcMSE, plot_3d_figure


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
        
    x_list = x_train[sample_start:sample_end]
    y_list = y_train_label[sample_start:sample_end]

    if netowrk_type == "cnn":
        # 给输入图像添加channel维度，默认值是1（参数axis是维度序号，不是数值）
        x_list = np.expand_dims(x_list, axis=1)
        print(x_list.shape)

    # 预览y的分布
    if plot:
        plt.scatter(sample_index_range, y_list, color="green")
        # plt.show()

    # 将样本转换为张量形式
    x = torch.Tensor(x_list)
    if model_type == "fitting":
        y = torch.Tensor(y_list)
    elif model_type == "classification":
        y = torch.LongTensor(y_list)  # LongTensor可以避免将整形转成float，否则交叉熵函数会报错
    # print(x)
    # print(y)
        
    return x, y


# 创建新模型
def create_model():
    # 模型参数从全局变量中获取

    # 创建神经网络实例   
    # Network_2_hidden_layer_for_mnist 类里面规定了用relu函数
    if hidden_layers == 2:
        model = Network_2_hidden_layer_for_mnist(n_features, n_hidden, n_hidden_2, n_classes)

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
    # x = x.data.numpy()
    if model_type == "fitting":
        h = h.data.numpy()
    # print(h)
    
    # 将张量变形为 list
    y_list = []
    for y_i in y.data:  #.data()可以提取张量部分，舍弃梯度函数部分
        y_list.append(y_i.item())  #.item()将一维张量转为数值
    # print(y_list)

    error = []
    for i in range(len(y_list)):
        error.append(y_list[i] - h[i])

    # 打印 y-h 的均方差
    mse = calcMSE(error)
    print("\nMean Square Error: %f" % mse)
    print("Root Mean Square Error: %f\n" % sqrt(mse))

    if plot:
        plt.scatter(sample_index_range, h, color="orange")
        # plt.scatter(sample_index_range, y-h, color="blue")
        plt.show()

# 模型参数可视化
def model_visualization(model):
    
    # 随机化初始参数，维数从output向input反着写
    if hidden_layers == 1:
        dummy_input = torch.randn(n_classes, n_hidden, input_col_max)
    elif hidden_layers == 2:
        dummy_input = torch.randn(n_classes, n_hidden_2, n_hidden, input_col_max)
    elif hidden_layers == 3:
        dummy_input = torch.randn(n_classes, n_hidden_3, n_hidden_2, n_hidden, input_col_max)

    # 将模型导出为 ONNX 格式
    path = 'model.onnx'
    torch.onnx.export(model, dummy_input, path, verbose=True)

    # 添加shape信息
    import onnx
    from onnx import shape_inference
    onnx.save(onnx.shape_inference.infer_shapes(onnx.load(path)), path)

    # 打印模型参数(权重，偏置)
    # 显示训练好的模型参数，不受onnx的随机初始化影响
    for param_tensor in model.state_dict():
        np.set_printoptions(suppress=True)
        print(param_tensor, "\n", model.state_dict()[param_tensor].numpy())
    # 统计参数数量
    params = sum([np.prod(p.size()) for p in model.parameters()])
    print("\nTotal parameters: %d" % params)
    
    # 在浏览器中打开导出的 ONNX 模型文件。不建议，会让terminal卡住
    # import netron
    # netron.start('model.onnx')

    # 如果不能自动打开网页，手动访问 https://netron.app/ 亦可
    print('\nONNX model saved as: "%s", please goto "https://netron.app/" to view the model.\n' % path)



def main(task_type, current_batch, plot):
    # 判断任务类型
    if task_type == "model_visualization":
        model_visualization(load_model())
        return 0
    elif task_type == "training_new_model":
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

    