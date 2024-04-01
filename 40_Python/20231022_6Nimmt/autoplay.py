# -*- coding: utf-8 -*-

# import game_6nimmt
import os


# 定义可变长度的列表类，元素都是 int， 支持直接对列表本身进行加法运算
# 为什么不是元组类：元组的元素不可以被改写，无法进行加法运算 （'tuple' object does not support item assignment）
class VariableLengthIntList():
    def __init__(self, *kw_members):
        # 格式转换：如果输入str，强制转成int
        int_value = []
        for i in kw_members:
            int_value.append(int(i))
        self.value = list(int_value)
        self.length = len(self.value)
    
    # 定义加法运算，将两个list的每个元素各自相加
    # 用于赋值运算，相当于 C = A + B
    def add(self, otherVLIlist):
        # 如果两个list长度不同，取两者较小值作为相加的长度
        num = min(self.length, otherVLIlist.length)
        # 复制一个list，防止修改自身
        # ret = self  # 这样不行，会使新的list和旧的值联动
        ret = VariableLengthIntList(*self.value)
        for i in range(num):
            ret.value[i] = self.value[i] + otherVLIlist.value[i]
        return ret

    # 定义自加运算，直接对自身进行操作，无法对外赋值
    # 相当于 A += B
    def add_self(self, otherVLIlist):
        # add方法不会改变自身length，仅改变value，故ret.length = self.length
        ret = self.add(otherVLIlist)
        self.value = ret.value
    
    # 对list中特定的位做加法 A[index] += b
    def add_self_by_index(self, index, add_value):
        self.value[index] += add_value


def game_result_statistics(csv_input, csv_output, players):
    contents = []
    with open(csv_input) as f:
        contents = f.readlines()
        f.close()
    
    # remove the first line
    contents.pop(0)
    
    game_num = 0
    total_bullheads = VariableLengthIntList(*([0]*players))
    wins = VariableLengthIntList(*([0]*players))
    for line in contents:
        # print(line)
        line_splited = line.split(",")
        # remove first member (game_round)
        line_splited.pop(0)
        # extract the last member (winner)
        winner = line_splited.pop(-1)
        # make the rest members as VLIlsit
        bullheads = VariableLengthIntList(*line_splited)
        # add bullheads of current game into total
        total_bullheads.add_self(bullheads)
        
        # convert winner format: P1 -> 0, P2 -> 1...
        winner_index = int(winner.replace("P", "")) - 1
        # add winner into total
        wins.add_self_by_index(winner_index, 1)
        # wins.value[winner_index] += 1  # 这样也可以，但使用类自带的方法更安全

        game_num += 1
    
    print("\nTotal games: " + str(game_num))
    print("Bullheads of each player: " + str(total_bullheads.value))
    print("Win times of each player: " + str(wins.value))

    headers = ""
    for i in range(players):
        headers += ("P%d," % (i+1))
    headers = headers.strip(",")
    
    with open(csv_output, "w") as f:
        f.write("---- Total games ----\n")
        f.write("%d\n\n" % game_num)
        f.write("---- Total Bullheads ----\n")
        f.write("%s\n" % headers)
        f.write("%s\n\n" % str(total_bullheads.value).strip("[").strip("]"))
        f.write("---- Total Wins ----\n")
        f.write("%s\n" % headers)
        f.write("%s\n\n" % str(wins.value).strip("[").strip("]"))
        f.close()

def init_record_folder(game_log_folder, game_result_stat_path, players):
    os.system("if not exist %s md %s" % (game_log_folder, game_log_folder))
    with open(game_result_stat_path, "w") as f:
        f.write("Game_id,")
        for a in range(players):
            f.write("P%s_Bullheads," % str(a+1))
        f.write("Winner\n")
        f.close()

def autorun_game(game_num, players):
    for i in range(game_num):
        print("\n==================== Start Game %d =======================" % i)

        # 内部函数调用，不好用，随机数种子不会刷新
        # game_6nimmt.run_game(logfile="game_log/game_log_%d.txt" % i, random_seed=i)
        
        # 外部参数调用，OK，随机数种子=游戏局数
        os.system("python game_6nimmt.py %d statistic > game_log\\game_log_%d.txt" % (i, i))

        # 游戏结束
        print("\n=================== Finish Game %d =======================" % i)



if __name__ == "__main__":

    # 连续进行局数
    GAME_NUM = 20
    # 玩家数量
    PLAYERS = 4

    # 游戏结果的保存位置
    game_log_folder = "game_log"
    game_result_stat_path = game_log_folder + "/00_statistics.csv"
    game_result_summary_path = game_log_folder + "/01_result_summary.csv"

    # 初始化目录和csv统计表
    init_record_folder(game_log_folder, game_result_stat_path, PLAYERS)

    # 自动运行多局游戏
    ### todo：允许传入玩家数量参数 - 当前的参数没有被使用
    autorun_game(GAME_NUM, PLAYERS)

    # 结果统计
    game_result_statistics(game_result_stat_path, game_result_summary_path, PLAYERS)

