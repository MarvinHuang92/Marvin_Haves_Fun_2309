# -*- coding: utf-8 -*-

import time

# 定义格子类（细胞）
class Cell():
    def __init__(self, world, position, state="dead"):
        self.state = state          # "alive" or "dead"
        self.next_state = ""
        self.position = position    # [x, y]
        self.world = world
        self.neighbors = 0          # min:0, max:8
    
    def calc_neighbors(self, print_info):
        x, y = self.position
        # do not use interation like "for cell in self.world.cells" which is too slow.
        neighbors_position = []
        # exception: top left corner
        if x > 0 and y > 0:
            neighbors_position.append([x-1, y-1])
        # exception: bottom left corner
        if x > 0 and y < self.world.scope[1] - 1:
            neighbors_position.append([x-1, y+1])
        # exception: top right corner
        if x < self.world.scope[0] - 1 and y > 0:
            neighbors_position.append([x+1, y-1])
        # exception: bottom right corner
        if x < self.world.scope[0] - 1 and y < self.world.scope[1] - 1:
            neighbors_position.append([x+1, y+1])

        # exception: left mergin
        if x > 0:
            neighbors_position.append([x-1, y])
        # exception: right margin
        if x < self.world.scope[0] - 1:
            neighbors_position.append([x+1, y])
        # exception: top margin
        if y > 0:
            neighbors_position.append([x, y-1])
        # exception: bottom margin
        if y < self.world.scope[1] - 1:
            neighbors_position.append([x, y+1])

        alive_neighbors = 0
        for pos in neighbors_position:
            msg = "Checking cell at position %s: " % pos
            if self.world.get_cell_state_by_position(pos) == "alive":
                msg += "It's alive."
                alive_neighbors += 1
            else:
                msg += "It's dead."
            if print_info:
                print(msg)
        self.neighbors = alive_neighbors
        if print_info:
            print("Cell %s's neighbors: %d" % (self.position, alive_neighbors))

    def calc_next_state(self):
        if self.state == "alive" and (self.neighbors < 2 or self.neighbors > 3):
            self.next_state = "dead"
        elif self.state == "dead" and self.neighbors == 3:
            self.next_state = "alive"
        else:
            self.next_state = self.state
            
    
    def update_state(self):
        self.state = self.next_state


# 定义世界类
class World():
    def __init__(self, scope):
        self.scope = scope      # [x, y], max number of cells
        self.cells = []
        self.init_cells()
        self.time = 0
        self.state = "stopped"  # "stopped" or "running"
    
    def init_cells(self):
        x, y = self.scope
        for j in range(y):
            cells_row_i = []
            for i in range(x):
                cells_row_i.append(Cell(self, [i, j]))
            self.cells.append(cells_row_i)

    # this function should only be called when the world is "stopped"
    def set_cell_state_by_position(self, position, state="dead"):
        x, y = position
        self.cells[y][x].state = state
    
    def get_cell_state_by_position(self, position):
        x, y = position
        return self.cells[y][x].state
    
    def get_cell_neighbors_by_position(self, position, print_info=True):
        x, y = position
        self.cells[y][x].calc_neighbors(print_info)
        return self.cells[y][x].neighbors

    def display_cell_states(self, format="matrix"):
        x, y = self.scope
        to_display_matrix = []
        to_display = []
        for j in range(y):
            cells_row_i_matrix = []
            cells_row_i = ""
            for i in range(x):
                if self.cells[j][i].state == "alive":
                    cells_row_i_matrix.append(1)
                    cells_row_i += "■ "
                elif self.cells[j][i].state == "dead":
                    cells_row_i_matrix.append(0)
                    cells_row_i += "  "
                else:
                    cells_row_i_matrix.append(-1)  # for bugfix
                    cells_row_i += "□ "
            to_display_matrix.append(cells_row_i_matrix)
            to_display.append(cells_row_i)
        if format == "matrix":
            for row in to_display_matrix:
                print(row)
        else:
            for row in to_display:
                print("| %s|" % row)
    
    def display_cell_next_states(self):
        x, y = self.scope
        to_display = []
        for j in range(y):
            cells_row_i = []
            for i in range(x):
                if self.cells[j][i].next_state == "alive":
                    cells_row_i.append(1)
                elif self.cells[j][i].next_state == "dead":
                    cells_row_i.append(0)
                else:
                    cells_row_i.append(-1)  # for bugfix
            to_display.append(cells_row_i)
        for row in to_display:
            print(row)
    
    def display_cell_neighbors(self):
        x, y = self.scope
        to_display = []
        for j in range(y):
            cells_row_i = []
            for i in range(x):
                cells_row_i.append(self.get_cell_neighbors_by_position([i, j], print_info=False))
            to_display.append(cells_row_i)
        for row in to_display:
            print(row)
    
    def display_world(self):
        print("Current time: %d" % self.time)
        # self.display_cell_states(format="matrix")
        self.display_cell_states(format="string")
        # print("")
        # self.display_cell_neighbors()
        # print("")
        # self.display_cell_next_states()
        print("")

    def evolution(self, interval=0):
        time.sleep(interval)
        x, y = self.scope
        for j in range(y):
            for i in range(x):
                self.cells[j][i].calc_neighbors(print_info=False)
        for j in range(y):
            for i in range(x):
                self.cells[j][i].calc_next_state()
        for j in range(y):
            for i in range(x):
                self.cells[j][i].update_state()
        # self.display_world()
        self.time += 1

# 快速创建模块
def create_module(world, base_pos, pos_config, mirror_horizon=False, mirror_vertical=False):
    for pos in pos_config:
        x, y = base_pos
        x += pos[0]
        y += pos[1]
        world.set_cell_state_by_position([x, y], "alive")

# 常用模块参数
# 蜂王梭
config_queen_bee_shuttle = [
    # 方块1
    [1, 4], [2, 4],
    [1, 5], [2, 5],
    # 方块2
    [21, 4], [22, 4],
    [21, 5], [22, 5],
    # 方块3
    [7, 3], [8, 3],
    [7, 4], [8, 4],
    [7, 5], [8, 5],

    [9, 2],
    [9, 6],

    [11, 1],
    [11, 2],
    [11, 6],
    [11, 7],
]
    
# 滑翔机关枪

# 长度为2^n的直线
def config_vertical_line(length):
    ret = []
    for i in range(length):
        ret.append([0, i])
    return ret


# 游戏主进程
def run_game():
    # init the world
    world = World([50, 40])

    # manually set some cells state
    # 蜂王梭
    # base_pos = [0, 0]  # 左上角起始点
    # create_module(world, base_pos, pos_config=config_queen_bee_shuttle)
    # base_pos = [20, 3]  # 左上角起始点
    # create_module(world, base_pos, pos_config=config_queen_bee_shuttle)

    # 长度为32的直线
    base_pos = [25, 4]  # 左上角起始点
    create_module(world, base_pos, pos_config=config_vertical_line(32))

    # manually check some cells neighbors
    # world.get_cell_neighbors_by_position([2, 0])

    world.display_world()
    
    # start evolustion
    for i in range(100):
        world.evolution(interval=0.02)
        world.display_world()

    

if __name__ == "__main__":

    run_game()
