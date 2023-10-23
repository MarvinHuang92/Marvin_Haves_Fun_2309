# -*- coding: utf-8 -*-

import os
import random
import neat
# import visualize  # 用于出图

# NEAT 算法参考：
# https://developer.aliyun.com/article/395142
# https://blog.csdn.net/weixin_48577398/article/details/118315566

# 依赖库：
# python -m pip install neat-python -i https://mirrors.aliyun.com/pypi/simple/

def network(game_value):
    return random.uniform(-10,10)  # 随机浮点数

def normalize(input):
    output = 0
    if input > 0:
        output = 1
    return output

# 构造训练数据：简单的异或判断
# 神经网络的输出值一般为float
xor_inputs = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
xor_outputs = [   (0.0,),     (1.0,),     (1.0,),     (0.0,)]

# 定义进化神经网络
def eval_genomes(genomes, config):
    # 对每个个体，独立计算fitness
    for genome_id, genome, in genomes:
        genome.fitness = 4.0  # fitness 初始值(最大值，表示4组都预测准确)
        # 每个个体是一个独立的神经网络实例
        network = neat.nn.FeedForwardNetwork.create(genome, config)
        for xi, xo in zip(xor_inputs, xor_outputs):
            output = network.activate(xi)
            genome.fitness -= (output[0] - xo[0]) ** 2  # 初始 fitness 减去平方差损失

 
def run(config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
 
    # 根据配置文件创建种群
    p = neat.Population(config)
    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # 每5次迭代生成一个checkpoint
    p.add_reporter(neat.Checkpointer(5))
 
    # Run for up to 300 generations.
    winner = p.run(eval_genomes, 300)
 
    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))
 
    # 展示最优net的输出结果对比训练数据
    print('\nOutput:')
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    for xi, xo in zip(xor_inputs, xor_outputs):
        output = winner_net.activate(xi)
        # 使用惊叹号！后接a 、r、 s，声明 是使用何种模式， acsii模式、引用__repr__ 或 __str__
        print("input {!r}, expected output {!r}, got {!r}".format(xi, xo, output))
 
    # 用于展示net时输入节点和输出节点的编号处理
    # input node从-1,-2,-3...编号，output node从0,1,2...编号
    node_names = {-1: 'A', -2: 'B', 0: 'A XOR B'}


    # # 绘制net
    # visualize.draw_net(config, winner, view=True, node_names=node_names)
    # # 绘制最优和平均适应度,ylog表示y轴使用symlog（symmetric log）刻度
    # visualize.plot_stats(stats, ylog=False, view=True)
    # # 可视化种群变化
    # visualize.plot_species(stats, view=True)
 
    # 使用restore_checkpoint方法使得种群p恢复到的checkpoint-4时的状态，返回population
    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
    p.run(eval_genomes, 10)
 
 
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config.ini')
    run(config_path)