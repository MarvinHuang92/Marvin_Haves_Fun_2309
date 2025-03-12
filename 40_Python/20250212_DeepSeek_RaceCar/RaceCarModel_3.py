import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 设置屏幕大小
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# 设置颜色
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# 设置字体
font = pygame.font.Font(None, 36)

# 设置时钟
clock = pygame.time.Clock()

# 设置小车的大小
car_width = 40
car_height = 100

# 设置道路参数
road_width = 80
dash_width = 8
dash_length = 160
dash_gap = 120

# 初始化EgoCar和TargetCar的位置和速度
ego_car_x = screen_width // 2 - car_width // 2
ego_car_y = screen_height - car_height - 20
ego_car_speed = 50  # 初始速度为50km/h

target_car_x = screen_width // 2 - car_width // 2
target_car_y = 100
target_car_speed = random.randint(20, 100)  # 初始速度为20-100km/h之间的随机值

# 道路偏移量（用于实现道路向后退的效果）
road_offset = 0

# 内部时钟（单位为秒）
internal_clock = 0

# 游戏主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 获取按键状态
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        ego_car_speed += 1
    if keys[pygame.K_s]:
        ego_car_speed = max(0, ego_car_speed - 1)

    # 更新TargetCar的速度
    target_car_speed += random.choice([-1, 0, 1])
    target_car_speed = max(20, min(100, target_car_speed))  # 限制速度在20-100km/h之间

    # 更新道路偏移量（模拟道路向后退）
    road_offset += ego_car_speed * 0.02
    if road_offset >= dash_length + dash_gap:
        road_offset = 0

    # 更新TargetCar的位置
    target_car_y += (ego_car_speed - target_car_speed) * 0.02

    # 更新内部时钟
    internal_clock += 1 / 50  # 每秒50个时钟刻

    # 检查是否撞车
    if ego_car_y <= target_car_y + car_height and ego_car_y + car_height >= target_car_y:
        running = False
        print("撞车")

    # 清屏
    screen.fill(BLACK)

    # 画道路虚线
    dash_start = road_offset - (dash_length + dash_gap)  # 确保第一段虚线也能显示
    while dash_start < screen_height:
        # 左侧虚线
        pygame.draw.rect(screen, WHITE, (screen_width // 2 - road_width // 2 - dash_width, dash_start, dash_width, dash_length))
        # 右侧虚线
        pygame.draw.rect(screen, WHITE, (screen_width // 2 + road_width // 2, dash_start, dash_width, dash_length))
        dash_start += dash_length + dash_gap

    # 画EgoCar
    pygame.draw.rect(screen, RED, (ego_car_x, ego_car_y, car_width, car_height))
    # 显示EgoCar的速度（右侧，距离小车右侧边缘30像素）
    speed_text = font.render(f"EgoCar: {int(ego_car_speed)} km/h", True, WHITE)
    screen.blit(speed_text, (ego_car_x + car_width + 30, ego_car_y))

    # 画TargetCar
    pygame.draw.rect(screen, WHITE, (target_car_x, target_car_y, car_width, car_height))
    # 显示TargetCar的速度（右侧，距离小车右侧边缘30像素）
    speed_text = font.render(f"TargetCar: {int(target_car_speed)} km/h", True, WHITE)
    screen.blit(speed_text, (target_car_x + car_width + 30, target_car_y))

    # 显示内部时钟（左上角）
    clock_text = font.render(f"Time: {internal_clock:.1f} s", True, WHITE)
    screen.blit(clock_text, (10, 10))

    # 更新屏幕
    pygame.display.flip()

    # 控制游戏时钟频率
    clock.tick(50)

# 退出游戏
pygame.quit()
sys.exit()