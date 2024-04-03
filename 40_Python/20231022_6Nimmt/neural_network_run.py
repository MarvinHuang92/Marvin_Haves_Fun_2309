
###############################################################
# 任务参数
model_type = "fitting"         # 函数拟合问题，输出连续值
# model_type = "classification"  # 二分类问题，输出离散值 [0,1] 二选一

# task_type = "training_new_model"       # 创建新模型，重新开始训练（学习速率*10）
# task_type = "training_existing_model"  # 加载模型，继续训练
task_type = "prediction"               # 加载模型，跳过训练，直接进行预测

batch_training = True   # 是否自动进行多组训练
training_batch = 3      # 训练组数

plot = True     # 是否显示拟合图像
###############################################################

# 样本参数
csv_input = "game_log/02_nn_sample_data_full.csv"
input_col_max = 64  # x的维数，最大值64

sample_start_tr = 0   # 训练样本起点，最小为0
batchsize_tr = 1000    # 训练时每组样本数

sample_start_pr = 3000   # 测试样本起点，最小为0
batchsize_pr = 100    # 测试时每组样本数


# 模型参数
model_path = 'model.pth'
n_features = input_col_max  # 特征数（输入神经元数量，对应样本的维数）
n_hidden = 500              # 隐藏神经元数量
# 输出神经元数量，拟合问题：1个，分类问题：2个（类别数量）
if model_type == "fitting":
    n_classes = 1
elif model_type == "classification":
    n_classes = 2           # 类别数（输出神经元数量，对应各个分类的概率）

# 训练参数
n_epochs = 1001             # 迭代次数
# 学习速率 （仅设置新微调模型的学习速率；创建的模型，学习速率*10）
if model_type == "fitting":
    learning_rate = 0.0001   # 可以在训练中途调整，先快后慢(0.01 -> 0.0001)
elif model_type == "classification":
    learning_rate = 0.001
n_print_loss = 200          # 每迭代n次，打印当前损失

###############################################################


# 运行模型
if __name__ == "__main__":
    import neural_network_6nimmt
    
    if not batch_training:
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
        neural_network_6nimmt.main(task_type, current_batch, plot)
    print("====== Task finished ======\n")

    