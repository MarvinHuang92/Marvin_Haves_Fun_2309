"""
在边长为1的正方形中，任意两点的平均距离？
"""

import random
from math import sqrt

def game():
    
    _coordinates = []
    for i in range(4):
        _coordinates.append(random.random())
    
    x1, x2, y1, y2 = _coordinates

    distance = sqrt((x1-x2)**2 + (y1-y2)**2)
    
    return distance
    
    

if __name__ =="__main__":

    game_round = 1000000

    ret_list = []
    for i in range(game_round):
        ret_list.append(game())

    # for line in ret_list:
    #     print(line)
    
    average = sum(ret_list) / len(ret_list)
    print(average)