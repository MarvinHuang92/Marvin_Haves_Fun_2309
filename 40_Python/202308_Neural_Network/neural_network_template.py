from torch import nn

# 基本步骤：
# 1. 定义神经网络类 Network (包含中间层种类：线性 or 卷积，激活函数的选择)
# 2. 创建神经网络实例
# 3. 定义 loss 损失函数（取决于问题类型：线性、非线性），和优化器
# 4. 开始迭代，训练模型（找到使得 loss 最小的权重参数）


# 定义神经网络类（激活函数，隐藏层数量不变时，可以直接复用）
class Network(nn.Module):
    # 重载初始化函数（构造函数）
    # 传入参数：输入层，隐藏层，输出层
    def __init__(self, n_in, n_hidden, n_out, activation_func):
        super().__init__()  # 首先调用父类的初始化函数
        # 使用传入的激活函数类型 - 解决不同问题，使用的激活函数也不同
        self.activation_func = activation_func
        # 然后新增步骤，创建两个线性层
        self.layer1 = nn.Linear(n_in, n_hidden)
        self.layer2 = nn.Linear(n_hidden, n_out)

    # 定义前向传播
    def forward(self, x):
        x = self.layer1(x)  # 计算 layer1 结果
        x = self.activation_func(x)  # 调用激活函数
        return self.layer2(x)  # 返回 layer2 结果


# 训练模型 - softmax 回归模型的循环迭代
def softmax_epoch(x, y, network, criterion, optimizer, n_epochs, n_print_loss):
    for epoch in range(n_epochs):
        y_pred = network(x)  # 调用forward 方法，预测输出

        # 计算预测值 y_pred 与真实值 y 之间的损失 loss
        loss = criterion(y_pred, y)
        loss.backward()  # 通过自动微分计算损失函数关于模型参数的梯度
        optimizer.step()  # 更新模型参数，使得损失函数减小
        optimizer.zero_grad()  # 将梯度清零，用于下一次迭代

        # 模型的每一次迭代，都由前向传播，和反向传播组成
        if epoch % n_print_loss == 0:
            # 每迭代 1000 次，打印当前损失
            print("%d iterations: loss = %.4lf" % (epoch, loss.item()))
    
    return network