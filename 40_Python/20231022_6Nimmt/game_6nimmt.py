# -*- coding: utf-8 -*-

import random, sys


# 用于神经网络训练的样本集，每个回合，每个玩家出牌时，更新一组
# State / Action 在玩家的 playCard() 方法中更新
# Reward 在玩家的 showPenaltyCard() 方法中更新
class NNSampleData():
    def __init__(self):
        # 成员全都是int，格式为：
        ### State ###
        # 0-39位：桌面20张牌的数字（偶数位）和牛头数量（奇数位）
        # 40-59位：10张手牌的数字（偶数位）和牛头数量（奇数位）
        # 60位：剩余手牌数量
        # 61位：当前分数（惩罚牛头数）
        self.state = []
        ### Action ###
        # 62位：打出的手牌index（0-9）
        self.action = 0
        ### Reward ###
        # 63位：打出手牌后的分数（或者分数delta？）
        self.reward = 0
        # 总表
        self.final_list = []
    
    def calcFinalList(self):
        self.final_list = self.state + [self.action, self.reward]


# 定义玩家类
class Player():
    def __init__(self, name, handcardsmax, is_smart=False):
        self.name = name
        self.handCardsMax = handcardsmax
        self.handCards = []
        self.penaltyCards = []
        self.bullheads = 0
        # 区分电脑玩家的智能程度
        self.is_smart = is_smart
        # 用于训练神经网络的指令集
        self.NN_Data = NNSampleData()
    
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
        self.NN_Data.reward = self.bullheads  # 更新训练样本集 - Reward
    
    def playCard(self, game, init_table_data, human=False):
        # 更新 State 样本集
        # 桌面牌型
        self.NN_Data.state = init_table_data[:]  # 注意list的赋值要加上[:]，否则将成为对原list的引用，无法修改
        # 出牌前的手牌
        for card in self.handCards:
            self.NN_Data.state += [card.value, card.bullheads]
        # 手牌不足10张，补足空位
        for i in range(self.handCardsMax - len(self.handCards)):
            self.NN_Data.state += [0, 0]
        # 出牌前的手牌数
        self.NN_Data.state += [len(self.handCards)]
        # 出牌前的牛头数
        self.NN_Data.state += [self.bullheads]

        # 选择出哪张牌
        if human:
            card, index = self.HumanChooseCardToPlay(game)
        else:
            card, index = self.AiChooseCardToPlay(game)
        self.handCards.pop(index)
        print("%s plays %s. (index: %d)" % (self.name, card.name, index))
        game.stash.append({"player":self, "card":card})
        
        # 将出牌的脚标加入 Action 样本集
        self.NN_Data.action = index

    # 电脑思考该出哪张牌
    def AiChooseCardToPlay(self, game):
        index = random.randint(0, game.left_round)
        return self.handCards[index], index  # 随机出一张牌

    # 人类出牌
    def HumanChooseCardToPlay(self, game):
        # 最后一局，不必询问
        if game.left_round == 0:
            return self.handCards[0], 0
        # 手牌多于一张，提示玩家选牌
        else:
            self.showHandCards()
            a = "0"
            while True:
                for card in self.handCards:
                    if str(card.value) == a:
                        index = self.handCards.index(card)
                        return card, index
                a = input("%s: Please choose a card to play..." % self.name)
        

    # 电脑思考当打出最小牌时，选择收哪一行
    def AiChooseWhenSmallest(self, game):
        # 普通电脑玩家，随机收一行
        if not self.is_smart:
            return random.randint(1,4)
        # 智能电脑玩家：计算每一行牛头数，收牛头最少的，如果并列，收靠前的行
        else:
            bullheads_list = []
            for row in range(4):
                bullheads = 0
                for col in game.table[row]:
                    if col:
                        bullheads += col.bullheads
                bullheads_list.append(bullheads)
            # print(bullheads_list)
            return(bullheads_list.index(min(bullheads_list)) + 1)
    
    # 人类：当打出最小牌时，选择收哪一行
    def HumanChooseWhenSmallest(self, game):
        pass


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

# 定义“游戏”类
class Game():
    # ====================
    # [0,0] | ... | [0,4]
    #  ...  | ... |  ...
    # [3,0] | ... | [3,4]
    # ====================
    def __init__(self, rounds=10):
        # 定义桌面（4*5网格）
        # self.table = [[None,]*5]*4  # 这样生成的4行会产生联动，不行
        self.table = [None,]*5, [None,]*5, [None,]*5, [None,]*5

        # 定义缓存区，存放玩家一回合中打出的牌
        # 其中元素示例 {"player":P1, "card":Card_1}
        self.stash = []
        # 剩余回合数，默认为10-1，可通过参数改变
        self.left_round = rounds-1
    
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
                target_row = item["player"].AiChooseWhenSmallest(self)
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
                last_d = 104
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


# 显示牌堆顺序
def showLeftCards(leftCards):
    cardlist = ""
    for card in leftCards:
        cardlist += (str(card.value) + ", ")
    print("leftCards: (%s)" % cardlist.strip(", "))

def run_game(players, random_seed, statistic):

    # 玩家数量 (2-10)
    PLAYERS = players
    # 每人手牌数 = 回合数，默认10
    HANDCARDS = 10
    # 人类玩家数量
    HUMAN_PLAYERS = 0

    # 强制随机数种子
    # random_seed = 1

    # 初始化神经网络样本集，用于打印
    NN_Sample_Data = []

    print("\n=================== Init Game =========================")

    # 创建游戏
    game = Game(HANDCARDS)

    # 创建104张牌对象
    leftCards = []
    for i in range(1,105):
        exec("Card_%d = Card(%d)" %(i, i))  # 需要创建新变量时，用 exec，否则可以用 exec 或 eval
        eval("leftCards.append(Card_%d)" %i)
    
    # 显示所有牌的信息
    # for card in leftCards:
    #     card.showInfo()

    # 创建所有玩家对象，最后一名玩家更智能 (is_smart=True)
    playerList = []
    for i in range(1, PLAYERS+1):
        if not i == PLAYERS:
            exec("P%d = Player('P%d', HANDCARDS)" %(i, i))
        else:
            exec("P%d = Player('P%d', HANDCARDS, is_smart=True)" %(i, i))
        eval("playerList.append(P%d)" %i)

    # 固定牌局
    if random_seed != -1:
        # print(random_seed)
        random.seed(random_seed)

    # 洗牌
    random.shuffle(leftCards)

    # 发牌
    for p in playerList:
        for i in range(HANDCARDS):
            p.handCards.append(leftCards.pop(0))
        # 人类玩家的手牌将被排序
        if i <= HUMAN_PLAYERS:
            p.sortHandCards()
        p.showHandCards()

    # 翻4张底牌
    for i in range(4):
        game.table[i][0] = leftCards.pop(0)
    game.showTable()

    # 显示剩余牌堆
    showLeftCards(leftCards)

    # 游戏开始
    for i in range(HANDCARDS):
        print("\n=============== Start Round %s ===================" % str(i+1))

        # 显示当前桌面牌型
        init_table_data = game.showTable()  # 准备样本集：前40位

        # 玩家出牌，并将桌面牌型和手牌加入样本集
        # 人类玩家出牌
        for i in range(HUMAN_PLAYERS):
            playerList[i].playCard(game, init_table_data, human=True)
        # 电脑玩家出牌
        for i in range(HUMAN_PLAYERS, PLAYERS):
            playerList[i].playCard(game, init_table_data)

        # 比较大小，并按顺序放置牌
        game.arrangeCard()
        game.stash = []  # 清空缓存区
        
        for p in playerList:
            p.showPenaltyCards()
            # 显示当前回合的训练样本集
            p.NN_Data.calcFinalList()
            # 将当前回合的样本加入总样本集，最后统一打印
            NN_Sample_Data.append(str(p.NN_Data.final_list).strip("[").strip("]") + "\n")

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
        game_result_filename = "game_log/game_result_%d.txt" % random_seed
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
        nn_sample_data_filename = "game_log/nn_sample_data_%d.csv" % random_seed
    with open(nn_sample_data_filename, "w") as f:
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
