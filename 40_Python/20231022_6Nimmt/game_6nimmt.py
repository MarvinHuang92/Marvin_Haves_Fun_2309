# -*- coding: utf-8 -*-

import random, sys


# 定义玩家类
class Player():
    def __init__(self, name):
        self.name = name
        self.handCards = []
        self.penaltyCards = []
        self.bullheads = 0
    
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
    
    def playCard(self, game, human=False):
        if human:
            card = self.HumanChooseCardToPlay(game)
        else:
            card = self.AiChooseCardToPlay(game)
        self.handCards.pop(self.handCards.index(card))
        print("%s plays %s." % (self.name, card.name))
        game.stash.append({"player":self, "card":card})

    # 电脑思考该出哪张牌
    def AiChooseCardToPlay(self, game):
        return self.handCards[0]  # 直接出第一张牌

    # 人类出牌
    def HumanChooseCardToPlay(self, game):
        # 当仅剩一张牌时，不必询问
        if len(self.handCards) == 1:
            return self.handCards[0]
        # 手牌多于一张，提示玩家选牌
        else:
            self.showHandCards()
            a = 0
            while True:
                for card in self.handCards:
                    if str(card.value) == a:
                        return card
                a = input("%s: Please choose a card to play..." % self.name)
        

    # 电脑思考当打出最小牌时，选择收哪一行
    def AiChooseWhenSmallest(self, game):

        return random.randint(1,4)  # 随机收一行

        # 计算每一行牛头数，收牛头最少的，如果并列，收靠前的行
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
    def __init__(self):
        # 定义桌面（4*5网格）
        # self.table = [[None,]*5]*4  # 这样生成的4行会产生联动，不行
        self.table = [None,]*5, [None,]*5, [None,]*5, [None,]*5

        # 定义缓存区，存放玩家一回合中打出的牌
        # 其中元素示例 {"player":P1, "card":Card_1}
        self.stash = []
    
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
        print("Show Table...")
        for row in self.table:
            toDisplay = "| "
            for col in row:
                if col:
                    toDisplay += (("%3d(%d)" % (col.value, col.bullheads)) + "| ")
                else:
                    toDisplay += "      | "
            print(toDisplay)


# 显示牌堆顺序
def showLeftCards(leftCards):
    cardlist = ""
    for card in leftCards:
        cardlist += (str(card.value) + ", ")
    print("leftCards: (%s)" % cardlist.strip(", "))

def run_game(random_seed='-1', statistic=False):

    # 玩家数量 (2-10)
    PLAYERS = 4
    # 每人手牌数，默认10
    HANDCARDS = 10
    # 人类玩家数量
    HUMAN_PLAYERS = 0

    # 强制随机数种子
    # random_seed = 1

    print("\n=================== Init Game =========================")

    # 创建游戏
    game = Game()
    # game.showTable()

    # 创建104张牌对象
    leftCards = []
    for i in range(1,105):
        exec("Card_%d = Card(%d)" %(i, i))  # 需要创建新变量时，用 exec，否则可以用 exec 或 eval
        eval("leftCards.append(Card_%d)" %i)
    
    # 显示所有牌的信息
    # for card in leftCards:
    #     card.showInfo()

    # 创建所有玩家对象
    for i in range(1, PLAYERS+1):
        exec("P%d = Player('P%d')" %(i, i))

    # 固定牌局
    if random_seed != -1:
        # print(random_seed)
        random.seed(random_seed)

    # 洗牌
    random.shuffle(leftCards)

    # 发牌
    for i in range(1, PLAYERS+1):
        for j in range(HANDCARDS):
            eval("P%d.handCards.append(leftCards.pop(0))" % i)
        # 人类玩家的手牌将被排序
        if i <= HUMAN_PLAYERS:
            eval("P%d.sortHandCards()" % i)
        eval("P%d.showHandCards()" % i)

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
        game.showTable()

        # 人类玩家出牌
        for i in range(1, HUMAN_PLAYERS+1):
            eval("P%d.playCard(game, human=True)" % i)
        # 电脑玩家出牌
        for i in range(HUMAN_PLAYERS+1, PLAYERS+1):
            eval("P%d.playCard(game)" % i)

        # 比较大小，并按顺序放置牌
        game.arrangeCard()
        game.stash = []  # 清空缓存区
        
        for i in range(1, PLAYERS+1):
            eval("P%d.showPenaltyCards()" % i)

    # 游戏结束，显示桌面和分数
    print("\n=================== Game End =======================")
    game.showTable()
    for i in range(1, PLAYERS+1):
        eval("P%d.showPenaltyCards()" % i)
        
    # 额外打印游戏结果summary
    game_result_filename = "game_log/game_result.txt"
    if random_seed != -1:
        game_result_filename = "game_log/game_result_%d.txt" % random_seed
    bullhead_list = []
    with open(game_result_filename, "w") as f:
        for i in range(1, PLAYERS+1):
            eval("bullhead_list.append(P%d.bullheads)" % i)
            f.write("P%d's Bullheads: %d\n" % (i, bullhead_list[i-1]))
        winner = bullhead_list.index(min(bullhead_list))
        f.write("P%s wins." % str(winner + 1))
        f.close()
    
    if statistic:
        # 在已有的文件后面添加行
        with open("game_log/00_statistics.csv", "a") as f:
            f.write("%d," % random_seed)
            for i in range(1, PLAYERS+1):
                eval("f.write(str(P%d.bullheads) + ',')" % i)
            f.write("P%s\n" % str(winner + 1))

if __name__ == "__main__":

    random_seed = -1
    statistic = False
    if len(sys.argv) > 2:
        random_seed = int(sys.argv[1])
        statistic = sys.argv[2] == "statistic"
    
    run_game(random_seed, statistic)
