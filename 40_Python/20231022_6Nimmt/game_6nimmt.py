# -*- coding: utf-8 -*-

import random, sys
import torch  
from neural_network_6nimmt import load_model

# 用于神经网络训练的样本集，每个回合，每个玩家出牌时，更新一组
# State / Action 在玩家的 playCard() 方法中更新
# Reward 在玩家的 showPenaltyCard() 方法中更新
class NNSampleData():
    def __init__(self):
        # 成员全都是int，格式为：
        ### State ###
        # （舍弃）0-39位：桌面20张牌的数字（偶数位）和牛头数量（奇数位）
        # 0-19位：10张手牌的数字（偶数位）和牛头数量（奇数位）
        # 20-23位：桌面每行剩余空位
        # 24-31位：桌面每行最后一张牌的数字和牛头数量
        # 32-35位：桌面每行牛头总数
        # 36位：玩家数量
        # 37位：剩余手牌数量
        # 38位：当前分数（惩罚牛头数）
        # 39位：决策类型：0-出牌，1-收一整行
        self.state = []
        ### Action ###
        # 40位：打出的手牌index（0-9）或收的行数（1-4）
        self.action = 0
        ### Reward ###
        # 41位：执行动作后的分数
        self.reward = 0
        # 总表
        self.final_list = []
    
    def calcFinalList(self):
        self.final_list = self.state + [self.action, self.reward]


# 定义玩家类
class Player():
    def __init__(self, name):
        self.name = name  # P1, P2...
        self.handCards = []  # 手牌
        self.penaltyCards = []  # 惩罚牌
        self.bullheads = 0  # 惩罚牌的牛头总数（罚分）
        self.played_smallest = False  # 本回合是否出了最小牌，会在每回合playCard之前重置
        # 区分玩家的智能程度 {simple_ai, advanced_ai, human, network}
        self.intellegence = "simple_ai"
        # 用于训练神经网络的指令集，0用于出牌时，1用于打出最小牌后收一整行时
        self.NN_data_0 = NNSampleData()  # 每回合都记录
        self.NN_data_1 = NNSampleData()  # 仅当 played_smallest 时记录
        # 玩家的神经网络模型（若没有神经网络，默认None）
        self.NN_model = None
    
    def sortHandCards(self):
        self.handCards.sort()  # 需要对象支持用 < 操作比较大小

    def showHandCards(self):
        cardlist = ""
        for card in self.handCards:
            cardlist += (str(card.value) + ", ")
        print("%s's HandCards: (%s)" % (self.name, cardlist.strip(", ")))
    
    def showPenaltyCards(self):
        cardlist = ""
        bullheads = 0
        for card in self.penaltyCards:
            cardlist += (str(card.value) + ", ")
            bullheads += card.bullheads
        print("%s's PenaltyCards: (%s), Bullheads: %d" % (self.name, cardlist.strip(", "), bullheads))
        self.bullheads = bullheads  # 将牛头数记录在玩家属性中

        # 更新训练样本集 - Reward
        # 方案1，记录本回合结束时，该玩家“实际”牛头数（回合结束后计算总数）
        # self.NN_data_0.reward = self.bullheads
        # self.NN_data_1.reward = self.bullheads

        # 方案2，采用 Adv Ai 的方法，计算“预期”分数（回合结束前计算delta）
        # 分别在 playCard()，chooseRowWhenSmallest() 方法中执行
    
    # 收集当前场上信息，用于更新 State 样本
    def getGameStateToNNData(self, game, situation=0):
        # 桌面牌型
        # state = game.table_data[:]  # 注意list的赋值要加上[:]，否则将成为对原list的引用，无法修改
        state = []  # 暂不添加桌面牌型在前40位
        # 出牌前的手牌
        for card in self.handCards:
            state += [card.value, card.bullheads]
        # 手牌不足10张，补足空位
        for i in range(game.max_round - len(self.handCards)):
            state += [0, 0]
        # 桌面每行剩余空位
        state += self.calcEachRowBlanks(game)
        # 桌面每行最后一张牌的数字和牛头数
        each_row_last_card = self.calcEachRowLastCard(game)
        for last_card in each_row_last_card:
            state += [last_card.value, last_card.bullheads]
        # 桌面每行牛头总数
        state += self.calcEachRowBullheads(game)
        # 玩家人数
        state += [game.players]
        # 出牌前的手牌数
        state += [len(self.handCards)]
        # 出牌前的牛头数
        state += [self.bullheads]
        # print(state)
        
        # 赋值给 NN_data_X，同时加上“场景”状态位
        # 0=出牌时，1=打出最小牌需要收一行时
        # if-else 防止同一回合内 NN_data_1 覆盖了 NN_data_0
        if situation == 0:
            self.NN_data_0.state = (state + [situation])
        elif situation == 1:
            self.NN_data_1.state = (state + [situation])

    def playCard(self, game, cardDeck):
        # 收集 State 信息
        self.getGameStateToNNData(game)

        # 选择出哪张牌
        card, index, handcards_dicts = self.chooseCardToPlay(game, cardDeck)
        self.handCards.pop(index)
        print("%s plays %s. (index: %d)" % (self.name, card.name, index))
        game.stash.append({"player":self, "card":card})
        
        # 将出牌的脚标加入 Action 样本集
        if not self.intellegence == "network":
            self.NN_data_0.action = index
        else:
            self.NN_data_0.action = -1  # 如果玩家是神经网络，用-1标记，后续不会加入样本集
        
        # 记录 Reward 样本集
        self.NN_data_0.reward = handcards_dicts[index]["reward"]

    # 玩家思考该出哪张牌
    def chooseCardToPlay(self, game, cardDeck):
        # 计算每张手牌的预期分数
        display = False
        if self.intellegence == "advanced_ai":
            display = True
        handcards_dicts = self.advAiCalcPlayCardReward(game, cardDeck, display)

        # 普通电脑
        if self.intellegence == "simple_ai":
            index = random.randint(0, game.left_round)  # 随机出一张牌
        # 高级电脑
        elif self.intellegence == "advanced_ai":
            # 针对reward排序
            handcards_dicts = sorted(handcards_dicts, key = lambda i: i["reward"])
            # 打出reward最低的牌
            # 可能有相同 reward 情况，当前先不考虑更细分的优先级，注释中有描述，算法后面再补充
            card = handcards_dicts[0]["card"]
            index = self.handCards.index(card)
        # 人类玩家
        elif self.intellegence == "human":
            # 最后一局，不必询问
            if game.left_round == 0:
                return self.handCards[0], 0
            # 手牌多于一张，提示玩家选牌
            else:
                self.showHandCards()
                while True:
                    a = input("%s: Please choose a card to play..." % self.name)
                    for card in self.handCards:
                        if str(card.value) == a:
                            index = self.handCards.index(card)
                            return card, index
        # 神经网络
        elif self.intellegence == "network":
            self.showHandCards()
            # 列出所有可能的action
            action_list = []
            for i in range(len(self.handCards)):
                action_list.append(i)  # 手牌的脚标
            # 计算最优 action
            index = self.neuronNetworkCalc(self.NN_data_0, action_list)
        
        return self.handCards[index], index, handcards_dicts 
        

    # 当打出最小牌时，选择收哪一行
    def chooseRowWhenSmallest(self, game, card):
        # 更新 State 样本集，场景=1（收一整行）
        self.played_smallest = True
        self.getGameStateToNNData(game, situation=1)
        
        # 计算回收每行的预期分数
        display = False
        if self.intellegence == "advanced_ai":
            display = True
        bullheads_list = self.advAiCalcRowReward(game, display)

        # 普通电脑，随机收一行
        if self.intellegence == "simple_ai":
            ret = random.randint(1,4)
        # 高级电脑：计算每一行牛头数，收牛头最少的，如果并列，收靠前的行
        elif self.intellegence == "advanced_ai":
            ret = bullheads_list.index(min(bullheads_list)) + 1
        # 人类玩家
        elif self.intellegence == "human":
            while True:
                a = input("%s: You played a smallest card! (%s) Please choose a row to clean... (1,2,3,4)" % (self.name, card.name))
                for r in range(1,5):
                    if str(r) == a:
                        self.NN_data_1.action = r  # 更新 Action 样本集
                        return r
        # 神经网络
        elif self.intellegence == "network":
            # 列出所有可能的action
            action_list = [1,2,3,4]  # 要收牌的行号，注意从1开始
            # 计算最优 action，注意结果也要+1
            ret = self.neuronNetworkCalc(self.NN_data_1, action_list) + 1
        
        # 更新 Action 样本集
        if not self.intellegence == "network":
            self.NN_data_1.action = ret
        else:
            self.NN_data_1.action = -1  # 如果玩家是神经网络，用-1标记，后续不会加入样本集

        # 记录 Reward 样本集
        self.NN_data_1.reward = bullheads_list[ret - 1]

        return ret

    # 高级电脑的算法

    # 计算每张手牌的预期分数
    def advAiCalcPlayCardReward(self, game, cardDeck, display=False):
        # 读取每行的空位数量
        each_row_blanks = self.calcEachRowBlanks(game)
        # 读取每行最后一张牌
        each_row_last_card_value = self.calcEachRowLastCardValue(game)
        # 读取每行的牛头总数
        bullheads_list = self.calcEachRowBullheads(game)

        # 策略：遍历手牌，计算每张手牌的预期分值
        # 场上每行最大的牌 0       1       2       3
        #                |       |       |       |
        # 手牌      0   1   2   3   4   5   6   7   8   9
        #                |       |       |       |
        #     smallest   |safe|X |safe|X |safe|X |safe|X

        handcards_dicts = []
        for handcard in self.handCards:
            # 计算“最小的正差值”以确定手牌会被放进哪一行
            closest_positive_diff = 0
            closest_row_index = 0
            for i in range(4):
                diff = handcard.value - each_row_last_card_value[i]
                if (diff > 0) and \
                    (not closest_row_index or (closest_row_index and (diff < closest_positive_diff))):
                    closest_positive_diff = diff
                    closest_row_index = i + 1
            # 0. smallest：手牌 < min(每行最大牌)，预期分值=场上所有行的牛头最小值，
            #    可能不止一张，预期分值小时，先出小牌，反之先出大牌（尽量搭别人便车） 
            if not closest_row_index:
                handcards_dicts.append({"card": handcard, "class": "smallest", "reward": min(bullheads_list)})
            else:
                # 1. safe：0 < 手牌-某行最大牌 <= 该行空位数，绝对安全，分值=0，
                #    组内优先级：1.手牌距离场上牌最近的 2.该行空位少的 3.先出小牌（大的那行不容易被人占）
                # 1A. 0 < 手牌-某行最大牌 <= 该行空位数+两者之间曾出现过的牌数量，同上（算法后续补充）
                if closest_positive_diff <= each_row_blanks[closest_row_index-1]:
                    handcards_dicts.append({"card": handcard, "class": "safe", "target_row": closest_row_index, "reward": 0})
                # 2. X(danger)：除了上述两种，预期分值=该行已有牛头数+空格数*(手牌-该行最大牌(不含两端)之间的牛头数)/104 (暂不考虑已出现过的牌)
                else:
                    reward_exp = bullheads_list[closest_row_index-1] + each_row_blanks[closest_row_index-1]*float(cardDeck.calcBullheadsBetween(each_row_last_card_value[closest_row_index-1]+1,handcard.value-1))/104
                    handcards_dicts.append({"card": handcard, "class": "danger", "target_row": closest_row_index, "reward": reward_exp})
        
        if display:
            self.showHandCards()
            print("\n" + self.name + ": Expected reward of each handcard:")
            for item in handcards_dicts:
                print(item["reward"])
            print("")

        return handcards_dicts

    # 计算回收每行的预期分数
    def advAiCalcRowReward(self, game, display):
        bullheads_list = self.calcEachRowBullheads(game)
        if display:
            print("\n" + self.name + ": Bullheads of each row: " + str(bullheads_list) + "\n")
        return bullheads_list

    def calcEachRowBlanks(self, game):
        each_row_blanks = []
        for row in range(4):
            blanks = 0
            for col in game.table[row]:
                if not col:
                    blanks += 1
            each_row_blanks.append(blanks)
        return each_row_blanks

    def calcEachRowLastCard(self, game):
        each_row_last_card = []
        for row in range(4):
            last_card = None
            for col in game.table[row]:
                if col:
                    last_card = col
            each_row_last_card.append(last_card)
        return each_row_last_card

    def calcEachRowLastCardValue(self, game):
        each_row_last_card = self.calcEachRowLastCard(game)
        each_row_last_card_value = []
        for last_card in each_row_last_card:
            each_row_last_card_value.append(last_card.value)
        return each_row_last_card_value
    
    def calcEachRowBullheads(self, game):
        bullheads_list = []
        for row in range(4):
            bullheads = 0
            for col in game.table[row]:
                if col:
                    bullheads += col.bullheads
            bullheads_list.append(bullheads)
        return bullheads_list

    # 神经网络的算法
    def neuronNetworkCalc(self, NN_data, action_list):
        # 提供神经网络的输入
        x_list = []
        s_i = list(NN_data.state)  # 当前state信息
        # print(s_i)
        for a in action_list:
            x_i = s_i + [a]  # x_i = state + 每种可能的action
            x_list.append(x_i)
        x = torch.Tensor(x_list)  # 将x由二维list转为二维张量
        # print(x)

        # 使用 model 预测结果 h, 表示每一种action对应的预测reward
        h = self.NN_model(x).data   #.data()可以提取张量部分，舍弃梯度函数部分
        print("\n" + self.name + "'s neural network output:\n" + str(h[:]) + "\n")
        
        # 将张量 h 变形为 list
        h_list = []
        for h_i in h:  # 将二维张量拆解成一维
            h_list.append(h_i[0].item())  #.item()将一维张量转为数值
        # print(h_list)
            
        # 输出预测reward（罚分）最小的action
        return h_list.index(min(h_list))


# 定义“牌”类
class Card():
    def __init__(self, value):
        self.name = "Card_" + str(value)
        self.value = value
        self.bullheads = 1
        if value == 55:
            self.bullheads = 7
        elif value % 10 == 5:
            self.bullheads = 2
        elif value % 10 == 0:
            self.bullheads = 3
        elif value % 11 == 0:
            self.bullheads = 5
    
    # 重载比较操作符"<"，用于比较类成员大小
    def __lt__(self, other):
        if self.value < other.value:
            return True
        else:
            return False
    
    def showInfo(self):
        print("%s, Bullheads: %d" %(self.name, self.bullheads))


# 定义“牌堆”类，继承自列表类
class CardDeck(list):
    def __init__(self, players=10):
        # 创建104张牌对象 
        # for i in range(1, 105):
        # 创建"玩家数量*10+4"张牌，玩家数默认10个
        for i in range(1, players*10+5):
            exec("Card_%d = Card(%d)" %(i, i))  # 需要创建新变量时，用 exec，否则可以用 exec 或 eval
            eval("self.append(Card_%d)" %i)
        # 备份 “影子牌堆” 防止被打乱顺序
        self.shadow = self[:]
        # 常量：所有牌的牛头数 = 171
        # self.total_bullheads = self.calcBullheadsBetween(1 , 104)

    # 显示牌堆顺序
    def showCards(self):
        cardlist = ""
        for card in self:
            cardlist += (str(card.value) + ", ")
        print("CardDeck: (%s)" % cardlist.strip(", "))

    # 计算任意两张牌之间的牛头数量，包含输入两端的牌
    def calcBullheadsBetween(self, start, end):
        bullheads = 0
        for card in self.shadow[start-1 : end]:
            bullheads += card.bullheads
        return bullheads


# 定义“游戏”类
class Game():
    # ====================
    # [0,0] | ... | [0,4]
    #  ...  | ... |  ...
    # [3,0] | ... | [3,4]
    # ====================
    def __init__(self, players, rounds=10):
        # 定义桌面（4*5网格）
        # self.table = [[None,]*5]*4  # 这样生成的4行会产生联动，不行
        self.table = [None,]*5, [None,]*5, [None,]*5, [None,]*5

        # 定义缓存区，存放玩家一回合中打出的牌
        # 其中元素示例 {"player":P1, "card":Card_1}
        self.stash = []
        # 当前桌面牌型的 NN_data 样本集格式（前40位）
        self.table_data = []
        # 游戏玩家数
        self.players = players
        # 总回合数，默认10
        self.max_round = rounds
        # 剩余回合数，默认10-1
        self.left_round = rounds - 1
    
    # 整理打出的牌（每回合结算）
    def arrangeCard(self):
        print("Sorting Cards...")
        self.stash = sorted(self.stash, key = lambda i: i["card"])
        for item in self.stash:
            # 计算当前牌与每行最后一张牌的差值
            diffs = []
            for row in range(4):
                for col in self.table[row]:
                    if col:
                        last_card_value = col.value
                    else:
                        break
                diffs.append(item["card"].value-last_card_value)
            # 如果是场上最小的牌，玩家自行选择清除一行
            if max(diffs) < 0:
                target_row = item["player"].chooseRowWhenSmallest(self, item["card"])
                print(item["player"].name + " plays " + item["card"].name + ", it is the smallest card! cleaned row %d as %s's Penalty." % (target_row, item["player"].name))
                # 传入的参数为 1-4 行，转换为脚标 0-3
                row = target_row - 1
                for i in range(5):
                    if self.table[row][i]:
                        item["player"].penaltyCards.append(self.table[row][i])
                        self.table[row][i] = None
                self.table[row][0] = item["card"]
            # 不是最小的牌，按照规则放在正确的行
            else:
                last_d = 104  # 当总牌数小于104时，该算法不受影响
                for d in diffs:
                    if 0 < d < last_d:
                        last_d = d
                        target_row = diffs.index(d)+1
                
                # 传入的参数为 1-4 行，转换为脚标 0-3
                row = target_row - 1
                # 显示信息
                print("%s puts %s to Row %d." % (item["player"].name, item["card"].name, target_row))
                # 该行有空位
                if None in self.table[row]:
                    for col in self.table[row]:
                        if not col:
                            self.table[row][self.table[row].index(col)] = item["card"]
                            break
                # 该行已满
                else:
                    print("Row %d is full, cleaned this row as %s's Penalty." % (target_row, item["player"].name))
                    for i in range(5):
                        item["player"].penaltyCards.append(self.table[row][i])
                        self.table[row][i] = None
                    self.table[row][0] = item["card"]
     
    def showTable(self):
        toDisplayNN = []
        print("Show Table...")
        for row in self.table:
            toDisplay = "| "
            for col in row:
                if col:
                    toDisplay += (("%3d(%d)" % (col.value, col.bullheads)) + "| ")
                    toDisplayNN += [col.value, col.bullheads]
                else:
                    toDisplay += "      | "
                    toDisplayNN += [0, 0]
            print(toDisplay)
        # 返回桌面牌型，用于训练样本集的输入
        return toDisplayNN
    
    def leftRoundDecrement(self):
        print("Current_Round_left: %d" % self.left_round)
        self.left_round -= 1


# 游戏主进程
def run_game(players, random_seed, statistic):

    # 玩家数量 (2-10)
    PLAYERS = players
    # 每人手牌数 = 回合数，默认10
    HANDCARDS = 10

    # 人类玩家列表
    human_player_indexes = []
    # human_player_indexes = [0]
    # 高级电脑玩家列表
    advanced_ai_indexes = []
    # advanced_ai_indexes = [1]
    # 神经网络玩家列表
    network_player_indexes = []
    # network_player_indexes = [-1]

    # 强制随机数种子
    # random_seed = 1

    # 初始化神经网络样本集，用于打印
    NN_Sample_Data = []

    print("\n=================== Init Game =========================")

    # 创建游戏
    game = Game(PLAYERS, HANDCARDS)

    # 创建所有玩家对象
    playerList = []
    for i in range(1, PLAYERS+1):
        exec("P%d = Player('P%d')" %(i, i))  # 需要创建新变量时，用 exec，否则可以用 exec 或 eval
        eval("playerList.append(P%d)" %i)
    
    # 赋予玩家不同身份
    # 人类
    for i in human_player_indexes:
        playerList[i].intellegence = "human"
    # 高级电脑
    for i in advanced_ai_indexes:
        playerList[i].intellegence = "advanced_ai"
    # 神经网络
    for i in network_player_indexes:
        playerList[i].intellegence = "network"
        playerList[i].NN_model = load_model()

    # 创建牌堆
    # cardDeck = CardDeck()  # 默认情况，104张牌都发出
    cardDeck = CardDeck(players=PLAYERS)  # 只发出和玩家数量对应的牌
    
    # 显示所有牌的信息
    # for card in cardDeck:
    #     card.showInfo()

    # 设置牌局随机数种子
    if random_seed != -1:
        random.seed(random_seed)

    # 洗牌
    random.shuffle(cardDeck)

    # 发牌
    for p in playerList:
        for i in range(game.max_round):
            p.handCards.append(cardDeck.pop(0))
        # 人类玩家的手牌将被排序
        if p.intellegence == "human":
            p.sortHandCards()
        p.showHandCards()

    # 翻4张底牌
    for i in range(4):
        game.table[i][0] = cardDeck.pop(0)
    game.showTable()

    # 显示剩余牌堆
    cardDeck.showCards()

    # 游戏开始
    for i in range(game.max_round):
        print("\n=============== Start Round %s ===================" % str(i+1))

        # 显示当前桌面牌型，并存入样本集：前40位
        game.table_data = game.showTable()

        # 玩家出牌，并将桌面牌型和手牌加入样本集
        for p in playerList:
            p.played_smallest = False  # 重置玩家状态
            p.playCard(game, cardDeck)

        # 处理缓存区：比较玩家出牌大小，并按顺序放置牌
        game.arrangeCard()
        game.stash = []  # 清空缓存区
        
        for p in playerList:
            p.showPenaltyCards()
            # 生成当前回合，当前玩家的训练样本集
            if not p.NN_data_0.action == -1:  # 神经网络玩家的动作，不加入样本
                p.NN_data_0.calcFinalList()
                # 将当前回合的样本加入总样本集，最后统一打印
                NN_Sample_Data.append(str(p.NN_data_0.final_list).strip("[").strip("]") + "\n")
            if (not p.NN_data_1.action == -1) and p.played_smallest:  # 如果本回合打出了最小牌
                p.NN_data_1.calcFinalList()
                NN_Sample_Data.append(str(p.NN_data_1.final_list).strip("[").strip("]") + "\n")

        # 游戏剩余回合数-1
        game.leftRoundDecrement()

    # 游戏结束，显示桌面和分数
    print("\n=================== Game End =======================")
    game.showTable()
    for p in playerList:
        p.showPenaltyCards()
        
    # 额外打印游戏结果summary
    game_result_filename = "game_log/game_result.txt"
    if random_seed != -1:
        game_result_filename = "game_log/autoplay/game_result_%d.txt" % random_seed
    bullhead_list = []
    with open(game_result_filename, "w") as f:
        for i in range(PLAYERS):
            bullhead_list.append(playerList[i].bullheads)
            f.write("P%d's Bullheads: %d\n" % (i+1, bullhead_list[i]))
        winner = bullhead_list.index(min(bullhead_list))
        f.write("P%s wins." % str(winner + 1))
        f.close()
    
    if statistic:
        # 在已有的文件后面添加行
        with open("game_log/00_statistics.csv", "a") as f:
            f.write("%d," % random_seed)
            for p in playerList:
                f.write(str(p.bullheads) + ',')
            f.write("P%s\n" % str(winner + 1))
    
    # 生成神经网络训练样本集
    # 每局游戏
    nn_sample_data_filename = "game_log/nn_sample_data.csv"
    if random_seed != -1:
        nn_sample_data_filename = "game_log/autoplay/nn_sample_data_%d.csv" % random_seed
    
    # 将记录打乱后再保存
    random.shuffle(NN_Sample_Data)

    # csv_headers = "Table11,,,,,,,,,,Table21,,,,,,,,,,Table31,,,,,,,,,,Table41,,,,,,,,,,\
    #     HandCard0,,,,,,,,,,,,,,,,,,HandCard9,,leftHandCard,CurrBullheads,Situation,Action,Reward"
    csv_headers = "HandCard0,,,,,,,,,,,,,,,,,,HandCard9,,BlanksRow1,,,BlanksRow4,LastCardRow1,,,,,,LastCardRow4,,\
        BullheadsRow1,,,BullheadsRow4,Players,leftHandCard,CurrBullheads,Situation,Action,Reward"
    with open(nn_sample_data_filename, "w") as f:
        f.write(csv_headers + "\n")
        f.writelines(NN_Sample_Data)
        f.close()
    # 历史总表
    with open("game_log/02_nn_sample_data_full.csv", "a") as f:
        f.writelines(NN_Sample_Data)
        f.close()

if __name__ == "__main__":

    # 默认值
    players = 2
    random_seed = -1
    statistic = False
    
    # 如果有参数输入
    if len(sys.argv) > 3:
        players = int(sys.argv[1])
        random_seed = int(sys.argv[2])
        statistic = sys.argv[3] == "statistic"
    
    run_game(players, random_seed, statistic)
