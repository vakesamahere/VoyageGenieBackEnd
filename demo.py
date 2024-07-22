import pygame
import random

# 初始化pygame
pygame.init()

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# 游戏板大小
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLOCK_SIZE = 30

# 屏幕大小
SCREEN_WIDTH = BOARD_WIDTH * BLOCK_SIZE
SCREEN_HEIGHT = BOARD_HEIGHT * BLOCK_SIZE + 40  # 增加40像素用于显示分数

# 创建屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("俄罗斯方块")

# 定义方块形状
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

# 定义颜色
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, RED, GREEN, BLUE, ORANGE]

# 创建游戏板
board = [[BLACK for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

# 当前方块
current_shape = None
current_color = None
current_x = 0
current_y = 0

# 分数
score = 0

# 创建新方块
def new_shape():
    global current_shape, current_color, current_x, current_y
    current_shape = random.choice(SHAPES)
    current_color = random.choice(SHAPE_COLORS)
    current_x = BOARD_WIDTH // 2 - len(current_shape[0]) // 2
    current_y = 0

# 检查碰撞
def check_collision(shape, x, y):
    for i in range(len(shape)):
        for j in range(len(shape[0])):
            if shape[i][j]:
                if (y + i >= BOARD_HEIGHT or
                    x + j < 0 or x + j >= BOARD_WIDTH or
                    board[y + i][x + j] != BLACK):
                    return True
    return False

# 将当前方块固定到游戏板上
def place_shape():
    for i in range(len(current_shape)):
        for j in range(len(current_shape[0])):
            if current_shape[i][j]:
                board[current_y + i][current_x + j] = current_color

# 消除已填满的行
def clear_lines():
    global board, score
    full_lines = [i for i in range(BOARD_HEIGHT) if all(cell != BLACK for cell in board[i])]
    for line in full_lines:
        del board[line]
        board.insert(0, [BLACK for _ in range(BOARD_WIDTH)])
    score += len(full_lines) * 100  # 每消除一行得100分

# 绘制游戏板
def draw_board():
    for i in range(BOARD_HEIGHT):
        for j in range(BOARD_WIDTH):
            pygame.draw.rect(screen, board[i][j], (j * BLOCK_SIZE, i * BLOCK_SIZE + 40, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(screen, WHITE, (j * BLOCK_SIZE, i * BLOCK_SIZE + 40, BLOCK_SIZE, BLOCK_SIZE), 1)

# 绘制当前方块
def draw_current_shape():
    for i in range(len(current_shape)):
        for j in range(len(current_shape[0])):
            if current_shape[i][j]:
                pygame.draw.rect(screen, current_color, 
                                 ((current_x + j) * BLOCK_SIZE, (current_y + i) * BLOCK_SIZE + 40, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, WHITE, 
                                 ((current_x + j) * BLOCK_SIZE, (current_y + i) * BLOCK_SIZE + 40, BLOCK_SIZE, BLOCK_SIZE), 1)

# 绘制分数
def draw_score():
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

# 游戏主循环
new_shape()
clock = pygame.time.Clock()
fall_time = 0
fall_speed = 0.5  # 每秒下落的格子数

running = True
while running:
    fall_time += clock.get_rawtime()
    clock.tick()

    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and not check_collision(current_shape, current_x - 1, current_y):
                current_x -= 1
            if event.key == pygame.K_RIGHT and not check_collision(current_shape, current_x + 1, current_y):
                current_x += 1
            if event.key == pygame.K_DOWN and not check_collision(current_shape, current_x, current_y + 1):
                current_y += 1
            if event.key == pygame.K_UP:
                rotated = list(zip(*current_shape[::-1]))
                if not check_collision(rotated, current_x, current_y):
                    current_shape = rotated

    # 自动下落
    if fall_time / 1000 > fall_speed:
        fall_time = 0
        if not check_collision(current_shape, current_x, current_y + 1):
            current_y += 1
        else:
            place_shape()
            clear_lines()
            new_shape()
            if check_collision(current_shape, current_x, current_y):
                running = False  # 游戏结束

    # 绘制
    screen.fill(BLACK)
    draw_board()
    draw_current_shape()
    draw_score()
    pygame.display.flip()

pygame.quit()
