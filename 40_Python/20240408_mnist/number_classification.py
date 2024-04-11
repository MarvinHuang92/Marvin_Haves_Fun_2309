import numpy as np

###############################################################
# 导入训练数据集
x_train = np.load("dataset/mnist/x_train.npy")
y_train_label = np.load("dataset/mnist/y_train_label.npy")

# 选择网络类型
netowrk_type = "mlp"  # MLP = Multi-Layer Perceptron 多层感知机
netowrk_type = "cnn"  # CNN = Convolve Neural Network 卷积神经网络

# 任务参数
# model_type = "fitting"         # 函数拟合问题，输出连续值
model_type = "classification"  # 二分类问题，输出离散值 [0,1] 二选一

task_type = "training_new_model"       # 创建新模型，重新开始训练（学习速率*10）
# task_type = "training_existing_model"  # 加载模型，继续训练
task_type = "prediction"               # 加载模型，跳过训练，直接进行预测
# task_type = "model_visualization"       # 模型可视化

# 样本参数
image_size = 28      # 输入图片边长，整型或list
in_channels = 1      # 输入图片颜色通道数，1或3 

sample_start_tr = 0   # 训练样本起点，最小为0
batchsize_tr = 128     # 训练时每组样本数

# training_batch = len(x_train)//batchsize_tr      # 训练组数
training_batch = 2      # 训练组数
batch_training = True   # 是否自动进行多组训练

# sample_start_pr = 0   # 测试样本起点，最小为0
sample_start_pr = sample_start_tr + batchsize_tr * training_batch
batchsize_pr = 128    # 测试时每组样本数

plot = True             # 是否显示拟合图像
###############################################################

# 模型参数
model_path = 'model_%s.pth' % netowrk_type

# MLP参数
n_features = image_size*image_size         # 特征数（输入神经元数量，对应样本的维数）
hidden_layers = 2           # 隐藏层数量
n_hidden = 312              # 隐藏神经元数量
n_hidden_2 = 256            # 隐藏神经元数量
# n_hidden_3 = 30            # 隐藏神经元数量

# CNN参数
conv_channels = [12, 24, 6]   # 卷积通道数（每层对应一个元素）
kernal_sizes =  [7, 5, 3]     # 卷积核尺寸（只有边长，默认正方形卷积核）

# 输出神经元数量，拟合问题：1个，分类问题:（类别数量）
if model_type == "fitting":
    n_classes = 1
elif model_type == "classification":
    n_classes = 10           # 类别数（输出神经元数量，对应各个分类的概率）

# 训练参数
n_epochs = 1024+1             # 迭代次数
if netowrk_type == "cnn":
    n_epochs = 256+1           # 迭代次数
# 学习速率 （仅设置微调模型的学习速率；对于新创建的模型，学习速率*10）
if netowrk_type == "cnn":
    learning_rate = 2e-3  # 可以在训练中途调整，先快后慢(0.01 -> 0.0001)
elif model_type == "fitting":
    learning_rate = 5e-4
elif model_type == "classification":
    learning_rate = 2e-5
n_print_loss = 200          # 每迭代n次，打印当前损失
if netowrk_type == "cnn":
    n_print_loss = 16       # 每迭代n次，打印当前损失

###############################################################


# 运行模型
if __name__ == "__main__":
    import neural_network_mnist as nn6

    if not batch_training or task_type == "model_visualization":
        training_batch = 1
    
    # 新模型批量训练时，仅第一次创建模型，之后加载上一次保存的模型
    plot_and_batch_training = plot and batch_training
    for b in range(training_batch):
        current_batch = b + 1  # 从1开始计数
        if task_type == "training_new_model" and current_batch > 1:
            task_type = "training_existing_model"
        # 批量训练时，如plot开关开启，仅最后一轮显示图像
        if plot_and_batch_training:
            if current_batch < training_batch:
                plot = False
            else:
                plot = True
        print("\n====== Task [%s], Batch %d ======\n" % (task_type, current_batch))
        nn6.main(task_type, current_batch, plot)
    print("====== Task finished ======\n")

    