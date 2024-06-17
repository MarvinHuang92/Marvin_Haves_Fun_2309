"""
将1米长的绳子随机剪成n段，最长一段的平均长度是多少？
"""

import random

def game(n):
    
    break_points = []
    for i in range(n-1):
        break_points.append(random.random())
    break_points.sort()

    break_points.append(1.0)  # the last point

    segments = []
    last_bp = 0.0
    for bp in break_points:
        segments.append(bp - last_bp)
        last_bp = bp
    
    return max(segments)
    

if __name__ =="__main__":

    n = 3
    game_round = 1000000

    ret_list = []
    for i in range(game_round):
        ret_list.append(game(n))

    # for line in ret_list:
    #     print(line)
    
    average = sum(ret_list) / len(ret_list)
    print(average)