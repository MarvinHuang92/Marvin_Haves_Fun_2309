# -*- coding: utf-8 -*-

import random
import easygame_ai

###### 一个超简单小游戏 ######
# 一个数字初始值为0或1
# 两名玩家轮流决定对它+1或+0
# 结果为奇数时，玩家1得分
# 结果为偶数时，玩家2得分
# 10个回合后结束

# 人类扮演 P1 陪练，分数不重要
# AI 扮演 P2，目标是尽可能多得分
#############################

# 定义玩家类
class Player():
    def __init__(self, name):
        self.name = name
        self.choice = [0, 1]
        self.decision = 0
        self.score = 0
    
    def makeDecision(self, game, human=False):
        if human:
            # 真实人类输入
            # while True:
            #     a = input("%s: Please choose 0 or 1\n" % self.name)
            #     if a == "0" or a == "1":
            #         game.value += int(a)
            #         break
            
            # “超人” 自动陪练
            game.value += self.supermanMakeDecision(game, strength=0.5)
        else:
            game.value += self.aiMakeDecision(game)
            # 如果对手也是“超人”
            # game.value += self.supermanMakeDecision(game, strength=1.0, negative=True)

    def supermanMakeDecision(self, game, strength=1.0, negative=False):
        a = 0
        if game.value % 2 == 0:
            a = 1
        # 有失误的概率，取决于strength 0 ~ 1
        if random.random() > strength:
            a = 1 - a
        # 如果作为对手，输出相反的结果
        if negative:
            a = 1 - a
        print("%s chooses %d" % (self.name, a))
        return a

    # 预留电脑决策方法
    def aiMakeDecision(self, game):
        # 随机选择0或1
        # a = random.randint(0,1)
        
        # 神经网络输出
        a = easygame_ai.network(game.value)
        print("%s's raw output: %.3f" % (self.name, a))
        
        # 将神经网络输出正则化
        a = easygame_ai.normalize(a)

        print("%s chooses %d" % (self.name, a))
        return a

    def showScore(self):
        print("%s Score: %d" % (self.name, self.score))


# 定义“游戏”类
class Game():
    def __init__(self):
        self.value = random.randint(0,1)  # 定义初始值
    
    # 定义结算规则，奇数P1得分，偶数P2得分
    def calcScore(self, P1, P2):
        if game.value % 2 != 0:
            P1.score += 1
        else:
            P2.score += 1
     
    def showValue(self):
        print("Current Value: %d" % self.value)



if __name__ == "__main__":

    print("\n=================== Init Game =========================")

    # 创建游戏
    game = Game()
    game.showValue()

    # 创建玩家对象
    P_human = Player("Human")
    P_ai = Player("AI")

    # 游戏开始
    for i in range(10):
        print("\n====== Round %s ======" % str(i+1))
        game.showValue()

        # 人类玩家行动
        P_human.makeDecision(game, human=True)
        game.showValue()
        game.calcScore(P_human, P_ai)
        P_human.showScore()

        # 电脑玩家行动
        P_ai.makeDecision(game)
        game.showValue()
        game.calcScore(P_human, P_ai)
        P_ai.showScore()

    # 游戏结束
    print("\n=================== Game End =======================")
    game.showValue()
    P_human.showScore()
    P_ai.showScore()
