import numpy as np

""" MLP = Multi-Layer Perceptron 多层感知机 """

# 导入训练数据集
x_train = np.load("dataset/mnist/x_train.npy")
y_train_label = np.load("dataset/mnist/y_train_label.npy")

print(x_train[:10])
print(y_train_label[:10])

# 将label由标量转为one_hot向量，classes为类别数，-1表示invalid值
def scalar_to_one_hot(scalar_list, classes):
    ret = []
    for i in scalar_list:
        if i == -1:
            ret_line = [-1]*classes
        else:
            ret_line = [0]*classes
            ret_line[i] = 1
        ret.append(ret_line)
    return ret

# 将one_hot向量转为标量，-1表示invalid值
def one_hot_to_scalar(one_hot_list):
    ret = []
    for line in one_hot_list:
        if line[0] == -1:
            scalar = -1   # check if data is invalid
        else:
            scalar = line.index(1)
        ret.append(scalar)
    return ret

print(scalar_to_one_hot(y_train_label[:10], classes=10))
print(scalar_to_one_hot([-1, 0, 1], classes=2))
print(one_hot_to_scalar([[-1, -1], [1, 0], [0, 1]]))