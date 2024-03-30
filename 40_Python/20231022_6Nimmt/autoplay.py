# -*- coding: utf-8 -*-

import game_6nimmt, os

if __name__ == "__main__":

    # 连续进行局数
    GAME_NUM = 10

    os.system("if not exist game_log md game_log")
    with open("game_log/00_statistics.csv", "w") as f:
        f.write("Game_id,")
        for a in range(4):
            f.write("P%s_Bullheads," % str(a+1))
        f.write("Winner\n")
        f.close()

    for i in range(GAME_NUM):
        print("\n==================== Start Game %d =======================" % i)

        # game_6nimmt.run_game(logfile="game_log/game_log_%d.txt" % i, random_seed=i)
        os.system("python game_6nimmt.py %d statistic > game_log\\game_log_%d.txt" % (i, i))

        # 游戏结束
        print("\n=================== Finish Game %d =======================" % i)

