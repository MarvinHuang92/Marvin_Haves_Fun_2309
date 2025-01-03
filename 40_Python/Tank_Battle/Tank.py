#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""坦克大战复刻版"""

__author__ = 'Marvin Huang'

# ver 0.4
# 增加了横向对齐：每次转向都会重新确定侧向位置
# 优化炮弹贴图

# ver 0.5
# 修改敌人出生机制
# Todo：解决无法对炮问题(canon_flag)、计分板（精确每种敌人的name才能区分分数）、会卡进墙里的问题

# ver 0.6
# 坦克炮弹数量设定修改，允许多于一枚炮弹存在，为道具做准备
# 更新“过热”机制，用于解决炮弹连击太快的问题
# 更新横向对齐的最小单位 12 -> 24，不容易卡进墙里了
# 去掉炮弹的无敌属性，允许对炮

# Todo: 墙体一次只能打掉一角的问题


"""
Class 类别
    世界类 World
    对象类 GameEntity -> {Tank, Terran, Canon}
    状态机 StateMachine
    状态   State
"""


import pygame
import time
import copy
from pygame.locals import *
from sys import exit
from random import randint, shuffle
from Vec2d import Vec2d

SCREEN_SIZE = (900, 624)
W = SCREEN_SIZE[0]
H = SCREEN_SIZE[1]

# 战场尺寸
BATTLEFIELD = (624, 624)
Bx = BATTLEFIELD[0]
By = BATTLEFIELD[1]

# 计分板尺寸
BB_SIZE = (W - Bx, By)
BW = BB_SIZE[0]
BH = BB_SIZE[1]

# U1 地形最小单位边长（像素）
# U2 横向对齐的最小单位
# U4 坦克和基地边长
U1 = 12
U2 = 24
U4 = 48

# 基地位置
BASE_POSITION = (Bx/2 - U4/2, By - U4)
BASEx = BASE_POSITION[0]
BASEy = BASE_POSITION[1]

# 敌人的数量
ENEMY_COUNT = 20
ENEMY_COUNT2 = int(0.003 * randint(0, 100) * ENEMY_COUNT)
ENEMY_COUNT3 = int(0.003 * randint(0, 100) * ENEMY_COUNT)
ENEMY_COUNT4 = int(0.003 * randint(0, 100) * ENEMY_COUNT)
ENEMY_COUNT1 = ENEMY_COUNT - ENEMY_COUNT2 - ENEMY_COUNT3 - ENEMY_COUNT4
ENEMY_ORDER = []

# 未出生的敌人（排队中）数量
ENEMY_QUEUE = 20
ENEMY_ALIVE = 0
NEXT_PLACE = 0

# 奖励出现的概率
bonus_prob = 1000

# 记分牌的内容（全局变量）
GAMEOVER = False
ENEMY_NUMBER = ENEMY_COUNT  # 剩余敌人的数目
TIME = 0.
CANON_AMOUNT = 0
PTS = 0
LIVES = 2  # 玩家剩余生命
OVERHEAT_CD = 2  # 炮管过热时长(帧)

# 以下State和StateMachine两个类是不变的，只改变后续的就可以
from StateMachine import *

class World(object):  # 世界地图
    def __init__(self):
        self.entities = {}  # 存储所有的实例
        self.entities2 = {}  # 备用目录
        self.entity_id = 0  # 上一个实例的编号
        # 画黑色背景
        self.background = pygame.surface.Surface(SCREEN_SIZE).convert()
        self.background.fill((0, 0, 0))
        # 画计分板
        pygame.draw.rect(self.background, (180, 180, 180), (Bx, 0, BB_SIZE[0], BB_SIZE[1]))
        # 画基地的【位置】，但并没有添加真正的基地上去
        # pygame.draw.rect(self.background, (255, 255, 255), (BASEx, BASEy, U4, U4))

# 以下几个方法是通用的

    def add_entity(self, entity):  # 增加一个新的实体
        self.entities[self.entity_id] = entity
        entity.id = self.entity_id
        self.entity_id += 1

    def remove_entity(self, entity):  # 删除一个实体
        del self.entities[entity.id]

    def get(self, entity_id):  # 通过id给出实体，没有的话返回None
        if entity_id in self.entities:
            return self.entities[entity_id]
        else:
            return None

    def process(self, time_passed_seconds):  # 处理世界中的每一个实体
        time_passed_seconds = time_passed_seconds * 1.5  # 时间加速器
        self.entities2 = copy.copy(self.entities)
        # 先把dict复制一份，对后者迭代，不然会改变原dict长度，导致报错
        for entity in self.entities2.values():
            entity.process(time_passed_seconds)

    def render(self, surface):
        # 绘制背景和每一个实体
        surface.blit(self.background, (0, 0))
        self.entities2 = copy.copy(self.entities)
        for entity in self.entities2.values():
            entity.render(surface)

# 额外的方法

    def collision(self, name, location, direction, size, id):
        # 碰撞判定
        # 这里的entity可以表示对方，但self是指world而不是我自己，所以自己的值全都需要传入：位置、方向、尺寸和id
        location = Vec2d(*location)  # 传入的值可能不符合Vec2d格式，这里规范一下
        direction = Vec2d(*direction)
        self.entities2 = copy.copy(self.entities)
        for entity in self.entities2.values():
            # 先检查对方不是自己！
            if id != entity.id:
                # 是否有碰撞体积
                if (name in ("tank_user", "tank_enemy") and entity.collision_to_tank)\
                        or (name == "canon" and entity.collision_to_canon):  # 注意分类的集合，不重复也不缺少
                    # 获得自身到对方的距离向量
                    distance = entity.location - location
                    # 获得距离向量到自身朝向的投影
                    proj_x = distance.projection(direction)
                    # 距离向量到自身侧向的投影
                    proj_y = distance.projection(direction.perpendicular())
                    if proj_y.get_length() < (size + entity.size - 4)/2:  # 这里标量化了，不用担心方向，-4是为了让侧面不容易被卡住
                        if direction.dot(proj_x) > 0:  # dot表示点积，确保是向前的
                            if proj_x.get_length() < (size + entity.size)/2:
                                return entity
        return None

# 下面定义所有的对象类


class GameEntity(object):
    # 游戏中所有对象基类, 具有若干通用属性（在init里面）
    # 只有两个通用方法：render和process: render就是绘画自身, process包括调用state的think，和执行其他的通用动作两部分
    def __init__(self, world, name, image):  # 定义通用属性，每一个都要赋予初始值
        self.world = world
        self.name = name
        self.image = image
        self.id = 0
        self.location = Vec2d(0, 0)  # 赋予初值，但是没什么意义，只是表示存在这个属性，后面还要修改
        self.speed = 0.
        self.direction = Vec2d(0, -1)  # 默认是朝下的（敌人）
        self.hp = 1  # 所有对象默认生命值 = 1
        self.size = U4
        self.invincible = False  # 默认不是无敌的
        self.collision_to_tank = True  # 默认对坦克有碰撞体积
        self.collision_to_canon = True  # 默认对炮弹有碰撞体积
        self.flag = 0  # 所属阵营（0表示中立，1表示玩家，2表示敌人）
        self.brain = StateMachine()
        self.canThink = True  # 默认True，如果对象无法思考，设为False不运行状态机，节约资源

    def render(self, surface):
        angle = -self.direction.get_angle() - 90
        rotated_image = pygame.transform.rotate(self.image, angle)
        x, y = self.location
        w, h = rotated_image.get_size()
        surface.blit(rotated_image, (x-w/2, y-h/2))

    def process(self, time_passed_seconds):
        if self.canThink:
            self.brain.think()
        # 这里的think可以在后面的各个state里面定义内容
        # 也可以定义一些在state之外的通用动作，或者不定义，全都放在state的think里面
        # 通常，每一步都要让可以移动的东西继续移动
        if self.speed > 0:
            self.location += time_passed_seconds * self.speed * self.direction
        # 防止坦克和炮弹（会移动的东西）超出边框范围
        if self.name == "tank_user" or self.name == "tank_enemy":  # 如果是坦克，就停止移动
            if self.location.x < 0 + U4 / 2:
                self.location.x = 0 + U4 / 2
            if self.location.x > BATTLEFIELD[0] - U4 / 2:
                self.location.x = BATTLEFIELD[0] - U4 / 2
            if self.location.y < 0 + U4 / 2:
                self.location.y = 0 + U4 / 2
            if self.location.y > BATTLEFIELD[1] - U4 / 2:
                self.location.y = BATTLEFIELD[1] - U4 / 2
        if self.name == "canon": # 如果是炮弹，就直接消失
            if (self.location.x < 0 + U1 / 2)\
                or (self.location.x > BATTLEFIELD[0] - U1 / 2)\
                or (self.location.y < 0 + U1 / 2)\
                or (self.location.y > BATTLEFIELD[1] - U1 / 2):
                self.world.remove_entity(self)
                self.shooter.reload_canon()  # 炮弹发射者补充炮弹
        # 刷新所有坦克炮管冷却时间
        if self.name == "tank_user" or self.name == "tank_enemy":
            if self.overheat > 0:
                self.overheat -= 1
        # 刷新炮弹库存
        global CANON_AMOUNT
        if self.name == "tank_user":
            CANON_AMOUNT = self.canon_amount

    def got_shot(self):  # 如果被击中，会触发此动作,但默认没有效果，对于基地等特殊对象才有效果
        pass


class Tank(GameEntity):
    # 坦克大类（包括玩家和敌人）
    # 具有的新属性：炮弹速度、炮弹库存、转弯和开火的概率，新方法：开炮fire，转向turn
    # 3个状态：前进going、停止stopping、被玩家控制controlled，在后面详细设置
    def __init__(self, world, name, image):  # 这里容易混淆，这一行的name是外界传入的
        # 执行基类构造方法
        GameEntity.__init__(self, world, name, image)  # 这里的name是上面那行传过来的，world同理
        # 创建各种状态
        going_state = TankStateGoing(self)
        stopping_state = TankStateStopping(self)
        controlled_state = TankStateControlled(self)
        self.brain.add_state(going_state)
        self.brain.add_state(stopping_state)
        self.brain.add_state(controlled_state)
        # 所有坦克默认速度48（每秒移动一个车身长度）
        self.normal_speed = 48  # 额定的速度
        self.speed = self.normal_speed  # 当前速度（可能不等于额定速度）
        # 新属性：炮弹速度、炮弹库存、转弯和开火的概率
        self.canon_speed = 120
        self.canon_amount_max = 1  # 可以同时存在场上的炮弹数量，上一发炮弹爆炸后会补充回来
        self.canon_amount = self.canon_amount_max  # 剩余炮弹数量
        self.turning_prob = 40  # 实际上是它的倒数，prob表示probability
        self.fire_prob = 50
        self.overheat = 0  # 所谓过热，用于防止连击太快

    # 定义开火动作
    def fire(self):
        if not self.overheat:
            if self.canon_amount > 0:
                canon_image = pygame.image.load("canon.png").convert_alpha()
                canon = Canon(self.world, canon_image)  # 建立一个实例
                canon.brain.set_state("flying")
                canon.shooter = self  # 记录炮弹的发射者
                canon.location = self.location + self.direction * (U4 / 2)
                canon.direction = self.direction
                canon.flag = self.flag  # 阵营和发射者的阵营相同
                canon.speed = self.canon_speed  # 速度由发射者赋予它
                self.world.add_entity(canon)  # 向世界添加炮弹，并使发射者的炮弹库存减少1
                self.canon_amount -= 1
                self.overheat = OVERHEAT_CD
    
    # 定义装填炮弹
    def reload_canon(self):
        if self.canon_amount < self.canon_amount_max:
            self.canon_amount += 1  # 炮弹发射者补充炮弹

    # 定义拐弯
    def turn(self):
        # 随机数决定拐弯方向
        a = randint(1, 5)
        if a == 1 or a == 2:
            self.lateral_correct()
            self.direction = self.direction.perpendicular()
        elif a == 3 or a == 4:
            self.lateral_correct()
            self.direction = - self.direction.perpendicular()
        else:
            self.direction = - self.direction  # 调头不需要侧向修正

    # 修正侧向位置
    def lateral_correct(self):
        # 先判断原始方向
        if self.direction in (Vec2d(-1, 0), Vec2d(1, 0)):  # 横向的
            s1 = self.location[0] // U2  # 取商的整数部分
            s2 = self.location[0] % U2  # 余数
            if s2 <= U1:
                self.location[0] = s1 * U2
            else:
                self.location[0] = s1 * U2 + U2
        else:  # 纵向的
            s1 = self.location[1] // U2
            s2 = self.location[1] % U2
            if s2 <= U1:
                self.location[1] = s1 * U2
            else:
                self.location[1] = s1 * U2 + U2


class TankUser(Tank):  # 玩家的坦克
    def __init__(self, world, image):  # 这里少了name属性，因为单个的个体不需要区分name，只是一类坦克整体有name
        # 首先继承父类的构造方法
        Tank.__init__(self, world, "tank_user", image) # 这里的name被固定下来，作为每一个创建的对象的标记
        # 对和父类不同的属性进行修改
        # self.canon_amount = 2
        # self.canon_amount_max = 2
        self.canon_speed = 240
        self.flag = 1
        self.hp = LIVES + 1

    def got_shot(self):
        global LIVES, GAMEOVER
        time.sleep(0.2)  # 延迟0.2秒，注意使用前要先import time
        LIVES -= 1
        self.location = Vec2d(9 * 24 , 25 * 24)
        self.direction = Vec2d(0, -1)
        if LIVES < 0:
            GAMEOVER = True


class TankEnemy1(Tank):  # 第一类敌人，所有属性都是默认的
    def __init__(self, world, image):
        Tank.__init__(self, world, "tank_enemy", image)  # 四类敌人都统称为tank_enemy，这里就不再建一个敌人大类了
        self.flag = 2


class TankEnemy2(Tank):  # 第二类敌人（高速装甲车，靠撞击造成伤害，每0.5秒撞击一次，防止连续伤害）
    def __init__(self, world, image):
        Tank.__init__(self, world, "tank_enemy", image)
        self.canon_amount = 0  # 禁止开炮
        self.normal_speed = 120  # 移动速度比其它坦克快
        self.flag = 2

    def collide(self):  # 撞击动作，和canon的动作类似，后面补充
        pass


class TankEnemy3(Tank):  # 第三类敌人，开炮比较快
    def __init__(self, world, image):
        Tank.__init__(self, world, "tank_enemy", image)
        self.canon_speed = 240  # 炮弹速度比其它坦克快一倍
        self.flag = 2


class TankEnemy4(Tank):  # 第四类敌人，4重装甲，受伤有加成，有生命槽
    def __init__(self, world, image):
        Tank.__init__(self, world, "tank_enemy", image)
        self.hp = 4
        self.flag = 2

    # 受伤加成
    def got_shot(self):
        if self.hp > 1:
            self.normal_speed += 36
            self.canon_speed += 48

    # 具有生命槽，长32，宽4，与坦克本身有10的空隙
    def render(self, surface):
        Tank.render(self, surface)
        x, y = self.location
        w, h = self.image.get_size()
        bar_x = x - 16
        bar_y = y - h / 2 - 10
        surface.fill((255, 0, 0), (bar_x, bar_y, 32, 4))
        surface.fill((0, 255, 0), (bar_x, bar_y, 8 * self.hp, 4))


class Terran(GameEntity):  # 地形对象，不可以动，中立阵营
    def __init__(self, world, name, image):  # 这不是最低级class，所以不能定义确定的name，等待传入
        GameEntity.__init__(self, world, name, image)
        self.flag = 0  # 虽然默认也是0，但还是保险一些啦
        self.canThink = False  # 不运行状态机，节约资源
        

class Base(Terran):  # 基地
    def __init__(self, world, image):  # 最低一级的class在__init__中定义name属性
        Terran.__init__(self, world, "base", image)
        self.flag = 0  # 并不是属于玩家阵营的，玩家也可以自己摧毁它

    def got_shot(self):  # 如果被击中，会导致游戏结束
        global GAMEOVER  # 引用全局变量的声明
        time.sleep(0.2)  # 延迟0.2秒，注意使用前要先import time
        GAMEOVER = True


class Wall(Terran):  # 墙
    def __init__(self, world, image):
        Terran.__init__(self, world, "wall", image)
        self.size = U2  # 尺寸24
        # self.size = U1  # 尺寸12


class Iron(Terran):  # 铁皮，无敌的，尺寸24
    def __init__(self, world, image):
        Terran.__init__(self, world, "iron", image)
        self.size = 2 * U1
        self.invincible = True


class Forrest(Terran):  # 树，没有碰撞体积
    def __init__(self, world, image):
        Terran.__init__(self, world, "forrest", image)
        self.collision_to_tank = False
        self.collision_to_canon = False


class River(Terran):  # 河水，没有炮弹碰撞体积
    def __init__(self, world, image):
        Terran.__init__(self, world, "river", image)
        self.collision_to_canon = False


class Border(Terran):  # 屏幕边界，是无敌的
    def __init__(self, world, image):
        Terran.__init__(self, world, "border", image)
        self.invincible = True


class Bonus(Terran):  # 奖励包，没有炮弹碰撞体积
    def __init__(self, world, image):
        Terran.__init__(self, world, "bonus", image)
        self.size = 32
        self.collision_to_canon = False


class Canon(GameEntity):  # 炮弹类
    def __init__(self, world, image):
        GameEntity.__init__(self, world, "canon", image)
        # 创建各种状态
        flying_state = CanonStateFlying(self)
        self.brain.add_state(flying_state)
        self.size = U1
        self.shooter = None  # 炮弹的发射者


# 下面定义所有的状态STATE

class CanonStateFlying(State):  # 炮弹的飞行状态，只有中途动作，因为只有这一个状态，没有进出动作
    def __init__(self, canon):
        State.__init__(self, "flying")
        self.canon = canon

    def do_actions(self):  # 唯一的动作，撞上什么东西然后爆炸
        goal = self.canon.world.collision("canon", self.canon.location, self.canon.direction, U1, self.canon.id)
        if goal is not None:
            self.canon.world.remove_entity(self.canon)
            self.canon.shooter.reload_canon()  # 炮弹发射者补充炮弹
            if (self.canon.flag != goal.flag) and not goal.invincible:
                goal.hp -= 1
                goal.got_shot()
                if goal.hp <= 0:
                    if goal.name == "tank_enemy":
                        global ENEMY_NUMBER, ENEMY_ALIVE
                        ENEMY_NUMBER -= 1
                        ENEMY_ALIVE -= 1
                    self.canon.world.remove_entity(goal)


class TankStateGoing(State):  # 包括完整的中途动作、转移条件、进出动作
    def __init__(self, tank):
        State.__init__(self, "going")
        self.tank = tank

    def do_actions(self):  # 随机的转向和开火
        self.tank.speed = self.tank.normal_speed
        if randint(1, self.tank.fire_prob) == 1:
            self.tank.fire()
        if randint(1, self.tank.turning_prob) == 1:
            self.tank.turn()

    def check_conditions(self):  # 撞到什么东西，进入stopping状态
        goal = self.tank.world.collision("tank_enemy", self.tank.location, self.tank.direction, U4, self.tank.id)
        if goal is not None:
            if goal.name == "bonus":
                self.tank.world.remove_entity(goal)  # 如果撞到的东西是bonus，就去掉它，并给自己加速（假设所有的bonus都是加速器）
                self.tank.normal_speed += 48
            return "stopping"
        return None

    def entry_actions(self):  # 进入动作，当然这也可以放进do_action里面去
        self.tank.turning_prob = 40


class TankStateStopping(State):
    def __init__(self, tank):
        State.__init__(self, "stopping")
        self.tank = tank

    def do_actions(self):  # 同样是随机的转向和开火，但不能移动了
        self.tank.speed = 0
        if randint(1, self.tank.fire_prob) == 1:
            self.tank.fire()
        if randint(1, self.tank.turning_prob) == 1:
            self.tank.turn()

    def check_conditions(self):
        goal = self.tank.world.collision("tank_enemy", self.tank.location, self.tank.direction, U4, self.tank.id)
        if goal is None:
            return "going"
        return None

    def entry_actions(self):  # 进入动作，当然这也可以放进do_action里面去
        self.tank.turning_prob = 10


class TankStateControlled(State):
    def __init__(self, tank):
        State.__init__(self, "controlled")
        self.tank = tank

    def do_actions(self):
        goal = self.tank.world.collision("tank_user", self.tank.location, self.tank.direction, U4, self.tank.id)
        # 控制方向，and遇到阻挡会停下来
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]:
            if self.tank.direction not in (Vec2d(-1, 0), Vec2d(1, 0)):
                self.tank.lateral_correct()
            self.tank.direction = Vec2d(-1, 0)
            self.collision_with_goal(goal)
        elif pressed_keys[K_RIGHT]:
            if self.tank.direction not in (Vec2d(-1, 0), Vec2d(1, 0)):
                self.tank.lateral_correct()
            self.tank.direction = Vec2d(1, 0)
            self.collision_with_goal(goal)
        elif pressed_keys[K_UP]:
            if self.tank.direction not in (Vec2d(0, -1), Vec2d(0, 1)):
                self.tank.lateral_correct()
            self.tank.direction = Vec2d(0, -1)
            self.collision_with_goal(goal)
        elif pressed_keys[K_DOWN]:
            if self.tank.direction not in (Vec2d(0, -1), Vec2d(0, 1)):
                self.tank.lateral_correct()
            self.tank.direction = Vec2d(0, 1)
            self.collision_with_goal(goal)
        # 不按方向键时，停止
        else:
            self.tank.speed = 0
        # 控制开火
        if pressed_keys[K_SPACE]:
            self.tank.fire()

    # 处理与目标的碰撞
    def collision_with_goal(self, goal):
        if goal is None:
            self.tank.speed = self.tank.normal_speed
        elif goal.name == "bonus":
            self.tank.world.remove_entity(goal)  # 如果撞到的东西是bonus，就去掉它，并给自己加速（假设所有的bonus都是加速器）
            self.tank.normal_speed += 48
            self.tank.canon_amount += 1
            self.tank.canon_amount_max += 1
        else:
            self.tank.speed = 0  # 如果撞到别的东西，就停下来


# 游戏主进程

def run():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
    pygame.display.set_caption('Tank Battle v0.6')  # pygame下的窗口标题，和python主体的设置方法不一样
    world = World()  # 这里定义的小写world变量名是一个实例，用来在后面传递给其他类。当然，World类只有这一个实例
    w, h = BATTLEFIELD
    clock = pygame.time.Clock()
    tank_user_image = pygame.image.load("tank_user.png").convert_alpha()
    wall_image = pygame.image.load("wall.jpg").convert()
    wall_small_image = pygame.image.load("wall_small.jpg").convert()
    iron_image = pygame.image.load("iron.jpg").convert()
    forrest_image = pygame.image.load("forrest.png").convert_alpha()
    river_image = pygame.image.load("river.jpg").convert()
    border_image = pygame.image.load("border.png").convert_alpha()
    tank_enemy1_image = pygame.image.load("tank_enemy1.png").convert_alpha()
    tank_enemy2_image = pygame.image.load("tank_enemy2.png").convert_alpha()
    tank_enemy3_image = pygame.image.load("tank_enemy3.png").convert_alpha()
    tank_enemy4_image = pygame.image.load("tank_enemy4.png").convert_alpha()
    canon_image = pygame.image.load("canon.png").convert_alpha()
    base_image = pygame.image.load("base.png").convert_alpha()
    bonus_image = pygame.image.load("bonus.png").convert_alpha()
 
    # 放置玩家坦克
    tank_user = TankUser(world, tank_user_image)
    tank_user.location = Vec2d(9 * 24, 25 * 24)
    tank_user.brain.set_state("controlled")
    world.add_entity(tank_user)
    # 设置CANON_AMOUNT的初始值
    global CANON_AMOUNT
    CANON_AMOUNT = tank_user.canon_amount

    # 确定敌人的出场顺序
    for enemy_no in range(ENEMY_COUNT1):
        ENEMY_ORDER.append(1)
    for enemy_no in range(ENEMY_COUNT2):
        ENEMY_ORDER.append(2)
    for enemy_no in range(ENEMY_COUNT3):
        ENEMY_ORDER.append(3)
    for enemy_no in range(ENEMY_COUNT4):
        ENEMY_ORDER.append(4)
    shuffle(ENEMY_ORDER)


    # 放置地形
    wall_location = []  # 先创建一个空的list
    for x in (3, 4, 7, 8, 19, 20, 23, 24):
        u = x * 24 - 12
        for y in range (3*24-12, 11*24, 24):
            z = (u, y)
            wall_location.append(z)
        for y in range (18*24-12, 24*24, 24):
            z = (u, y)
            wall_location.append(z)
    for x in (11, 12, 15, 16):
        u = x * 24 - 12
        for y in range (3*24-12, 9*24, 24):
            z = (u, y)
            wall_location.append(z)
        for y in (12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26):
            v = y * 24 - 12
            z = (u, v)
            wall_location.append(z)
    for x in (1, 2, 5, 6, 7, 8, 19, 20, 21, 22, 25, 26):
        u = x * 24 - 12
        z = (u, 14*24-12)
        wall_location.append(z)
    for x in (5, 6, 7, 8, 19, 20, 21, 22):
        u = x * 24 - 12
        z = (u, 15 * 24 - 12)
        wall_location.append(z)
    for x in (13, 14):
        u = x * 24 - 12
        for y in (17, 18, 23, 24):
            v = y * 24 - 12
            z = (u, v)
            wall_location.append(z)
    # 大块的墙体
    for pos in wall_location:
        wall = Wall(world, wall_image)
        wall.location = Vec2d(*pos)
        world.add_entity(wall)
    # 小块的墙体：将每个pos分割成4个小的墙体
    # for pos in wall_location:
    #     small_wall_location = []
    #     small_wall_location.append((pos[0]-6, pos[1]-6))
    #     small_wall_location.append((pos[0]-6, pos[1]+6))
    #     small_wall_location.append((pos[0]+6, pos[1]-6))
    #     small_wall_location.append((pos[0]+6, pos[1]+6))
    #     for small_pos in small_wall_location:
    #         wall = Wall(world, wall_small_image)
    #         wall.location = Vec2d(*small_pos)
    #         world.add_entity(wall)

    iron_location = []
    for x in (1, 2, 25, 26):
        u = x * 24 - 12
        z = (u, 15*24-12)
        iron_location.append(z)
    for x in (13, 14):
        u = x * 24 - 12
        for y in (7, 8):
            v = y * 24 - 12
            z = (u, v)
            iron_location.append(z)
    for pos in iron_location:
        iron = Iron(world, iron_image)
        iron.location = Vec2d(*pos)
        world.add_entity(iron)

    base = Base(world, base_image)
    base.location = (BASEx + U4 / 2, BASEy + U4 / 2)
    world.add_entity(base)
 
    # 开始循环
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
                    # 让ESC也可以退出程序

        time_passed = clock.tick(30)  # 毫秒
        # 可以改变帧率

        time_passed_seconds = time_passed / 1000.  # 转成秒(浮点数)
        global TIME
        TIME += time_passed_seconds
        # 记录时间

        # 当场上敌人少于6个时，添加敌人坦克
        global ENEMY_ALIVE, ENEMY_QUEUE, NEXT_PLACE
        if ENEMY_ALIVE < 6 and ENEMY_QUEUE > 0:
            # 敌人出生地点
            place_x = 288 * NEXT_PLACE + 24
            place_y = 24
            NEXT_PLACE += 1
            if NEXT_PLACE > 2:
                NEXT_PLACE = 0
            # 建立实例
            if ENEMY_ORDER[0] == 1:
                tank_enemy = TankEnemy1(world, tank_enemy1_image)
            elif ENEMY_ORDER[0] == 2:
                tank_enemy = TankEnemy2(world, tank_enemy2_image)
            elif ENEMY_ORDER[0] == 3:
                tank_enemy = TankEnemy3(world, tank_enemy3_image)
            elif ENEMY_ORDER[0] == 4:
                tank_enemy = TankEnemy4(world, tank_enemy4_image)
            tank_enemy.location = Vec2d(place_x, place_y)  # 放置位置
            tank_enemy.brain.set_state("going")  # 默认状态
            world.add_entity(tank_enemy)  # 添加进地图
            ENEMY_QUEUE -= 1
            ENEMY_ALIVE += 1
            ENEMY_ORDER.pop(0)
            # print(ENEMY_ORDER)
            # print("QUEUE = "+ str(ENEMY_QUEUE))

        # 随机时间和地点出现奖励
        if randint(1, bonus_prob) == 1:
            bonus = Bonus(world, bonus_image)
            bonus.location = Vec2d(randint(0, w), randint(0, h))
            world.add_entity(bonus)

        # 处理世界中每一个entity
        world.process(time_passed_seconds)
        world.render(screen)

        # 显示计分板信息
        font = pygame.font.SysFont(None, 24)  # 准备小字号
        font3 = pygame.font.SysFont(None, 48)  # 准备大字号
        text_surface1 = font.render('Time: %d' % TIME, True, (255, 255, 255))  # 显示时间
        text_surface2 = font.render('Enemies: %d' % ENEMY_NUMBER, True, (255, 255, 255))  # 显示剩余敌人数量
        text_surface3 = font3.render('YOU WIN!', True, (255, 255, 255))
        text_surface4 = font3.render('GAME OVER!', True, (255, 255, 255))
        text_surface5 = font.render('Canons: %d' % CANON_AMOUNT, True, (255, 255, 255))  # 显示剩余弹药
        text_surface6 = font.render('Player Tanks: %d' % LIVES, True, (255, 255, 255))  # 显示剩余生命
        screen.blit(text_surface1, (BATTLEFIELD[0] + 15, 5))
        screen.blit(text_surface2, (BATTLEFIELD[0] + 15, 35))
        screen.blit(text_surface5, (BATTLEFIELD[0] + 15, 65))
        if not GAMEOVER:
            screen.blit(text_surface6, (BATTLEFIELD[0] + 15, 125))
        if ENEMY_NUMBER == 0:
            screen.blit(text_surface3, (BATTLEFIELD[0] + 65, 185))
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[K_SPACE]:
                exit()
        if GAMEOVER:
            screen.blit(text_surface4, (BATTLEFIELD[0] + 35, 185))
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[K_SPACE]:
                exit()

        pygame.display.update()


if __name__ == "__main__":
    run()
