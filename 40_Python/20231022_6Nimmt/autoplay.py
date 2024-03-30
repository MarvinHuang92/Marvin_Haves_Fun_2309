# -*- coding: utf-8 -*-

import game_6nimmt, os

if __name__ == "__main__":

    # 连续进行局数
    GAME_NUM = 10

    for i in range(GAME_NUM):
        print("\n==================== Start Game %d =======================" % i)

        # game_6nimmt.run_game(logfile="game_log_%d.txt" % i, random_seed=i)
        os.system("python game_6nimmt.py %d > game_log_%d.txt" % (i, i))

        # 游戏结束
        print("\n=================== Finish Game %d =======================" % i)

