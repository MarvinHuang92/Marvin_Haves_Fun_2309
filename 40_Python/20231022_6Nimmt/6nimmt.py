# -*- coding: utf-8 -*-

import random

# 定义玩家类
class Player():
    def __init__(self, name):
        self.name = name
        self.handCards = []
        self.penaltyCards = []
    
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
    
    def playCard(self, table):
        card = self.chooseCardToPlay(table)
        self.handCards.pop(self.handCards.index(card))
        print("%s plays %s." % (self.name, card.name))
        table.stash.append({"player":self, "card":card})

    # 玩家思考该出哪张牌
    def chooseCardToPlay(self, table):
        return self.handCards[0]

    # 玩家思考当打出最小牌时，选择收哪一行
    def chooseWhenSmallest(self, table):

        # return random.randint(1,4)

        bullheads_list = []
        for row in range(4):
            bullheads = 0
            for col in table.table[row]:
                if col:
                    bullheads += col.bullheads
            bullheads_list.append(bullheads)
        # print(bullheads_list)
        return(bullheads_list.index(min(bullheads_list)) + 1)


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

# 定义“桌面”类（4*5网格）
class Table():
    # ====================
    # [0,0] | ... | [0,4]
    #  ...  | ... |  ...
    # [3,0] | ... | [3,4]
    # ====================
    def __init__(self):
        # self.table = [[None,]*5]*4  # 这样生成的4行会产生联动，不行
        self.table = [None,]*5, [None,]*5, [None,]*5, [None,]*5
        self.stash = []  # 缓存区，元素示例 {"player":P1, "card":Card_1}
    
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
                target_row = item["player"].chooseWhenSmallest(table)
                print(item["player"].name, item["card"].name, "is the smallest card! cleaned row %d as %s's Penalty." % (target_row, item["player"].name))
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



if __name__ == "__main__":

    # 玩家数量 (2-10)
    PLAYERS = 10
    # 每人手牌数，默认10
    HANDCARDS = 10

    print("\n=================== Init Game =========================")

    # 创建桌面
    table = Table()
    # table.showTable()

    # 创建104张牌对象
    leftCards = []
    for i in range(1,105):
        exec("Card_%d = Card(%d)" %(i, i))  # 需要创建新变量时，用 exec，否则可以用 exec 或 eval
        eval("leftCards.append(Card_%d)" %i)
    
    # 显示所有牌的信息
    # for card in leftCards:
    #     card.showInfo()

    # 创建10名玩家对象
    for i in range(1,11):
        exec("P%d = Player('P%d')" %(i, i))

    # 洗牌
    random.shuffle(leftCards)

    # 发牌，PLAYERS名玩家，每人HANDCARDS张牌
    for i in range(1, PLAYERS+1):
        for j in range(HANDCARDS):
            eval("P%d.handCards.append(leftCards.pop(0))" % i)
        # eval("P%d.sortHandCards()" % i)
        eval("P%d.showHandCards()" % i)

    # 翻4张底牌
    for i in range(4):
        table.table[i][0] = leftCards.pop(0)
    table.showTable()

    # 显示剩余牌堆
    showLeftCards(leftCards)

    # 游戏开始
    for i in range(HANDCARDS):
        print("\n=================== Start Game %s =======================" % str(i+1))
        # 玩家出牌
        for i in range(1, PLAYERS+1):
            eval("P%d.playCard(table)" % i)

        # 比较大小，并按顺序放置牌
        table.arrangeCard()
        table.stash = []  # 清空缓存区
        table.showTable()
        
        for i in range(1, PLAYERS+1):
            eval("P%d.showPenaltyCards()" % i)

