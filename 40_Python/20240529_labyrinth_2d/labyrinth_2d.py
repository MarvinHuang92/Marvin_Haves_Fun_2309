# -*- coding: utf-8 -*-

# import random, sys
# import torch  
# from neural_network_6nimmt import load_model

# 定义“墙”类
class Wall():
    def __init__(self, direction, start_point):
        # 方向：0 = horizontal, 1 = vertical
        self.direction = direction
        # 起始点：左/上格点坐标
        self.start_point = start_point

# 定义“游戏”类
class Game():
    def __init__(self, width, height, walls_list):
        self.map_range = [width, height]
        self.map_for_display = self.init_map()  # 用于显示的地图
        self.cells = self.init_cells()
        self.walls = self.init_walls(walls_list)
        self.spirits = []   # 精灵
        self.time = 0       # 时间戳
    
    # 初始化格子
    def init_cells(self):
        return []
     
    # 初始化墙
    def init_walls(self, walls_list):
        walls = []
        for w in walls_list:
            direction = w.pop(0)
            walls.append(Wall(direction, w))
        return walls
    
    # 初始化显示地图
    def init_map(self):
        map_for_display = []
        row = " " * (2 * self.map_range[0] + 1)
        for i in range(2 * self.map_range[1] + 1):
            map_for_display.append(row)
        return map_for_display

    # 更新地图
    def update_map(self):
        # self.map_for_display.append()
        for wall in self.walls:
            pass
    
    # 显示地图
    def show_map(self):
        for line in self.map_for_display:
            print(line)



# 游戏主进程
def run_game():
    walls_list = [
        [0, 0, 0],
        [1, 0, 0]
    ]
    game = Game(10, 10, walls_list)
    game.update_map()
    game.show_map()

if __name__ == "__main__":

    run_game()
