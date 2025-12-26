import pygame
from GameConfig import *
import sys
import ChatBox
import SoundControl

# ---------------- 游戏配置 ----------------
BOARD_SIZE = 15
CELL_SIZE = 40
MARGIN = 40
INFO_WIDTH = 200  # 右侧信息栏宽度
WINDOW_WIDTH = MARGIN * 2 + CELL_SIZE * (BOARD_SIZE - 1) + INFO_WIDTH
WINDOW_HEIGHT = MARGIN * 2 + CELL_SIZE * (BOARD_SIZE - 1)
FPS = 30

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLACK = (100, 100, 100)
LIGHT_WHITE = (200, 200, 200)
BOARD_BG = (240, 200, 120)
INFO_BG = (220, 220, 220)
HIGHLIGHT_COLOR = (180, 0, 0)



# ---------------- 棋盘状态 ----------------

board : list[list[int]] = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]  # 0 空 1 黑 2 白
current_player = None  # 1=黑, 2=白, BLACK_PLAYER = 1, WHITE_PLAYER = 2
step_time = 30  # 每步时间，秒
board_enabled = True
winner = None
highlight_piece = None
room_id = None
this_player = None
chat_box = None

# ---------------- 初始化 ----------------
def initialize(connection):
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Gobang Board")
    global board, current_player, step_time, board_enabled, winner,highlight_piece
    board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]  # 0 空 1 黑 2 白
    current_player = this_player  # 1=黑, 2=白, BLACK_PLAYER = 1, WHITE_PLAYER = 2
    board_enabled = this_player == BLACK_PLAYER
    winner = None
    highlight_piece = None
    global chat_box, room_id
    chat_box = ChatBox.ChatBox(x = 640,y=280,width = 200, height = 340,connection=connection)
    chat_box.add_message(SYSTEM,"Game start")
    return screen

# ---------------- 工具函数 ----------------
def board_to_pixel(ix, iy):
    x = MARGIN + ix * CELL_SIZE
    y = MARGIN + iy * CELL_SIZE
    return x, y


def pixel_to_board(mx, my):
    """将鼠标像素位置转换为棋盘索引"""
    ix = round((mx - MARGIN) / CELL_SIZE)
    iy = round((my - MARGIN) / CELL_SIZE)
    if 0 <= ix < BOARD_SIZE and 0 <= iy < BOARD_SIZE:
        return ix, iy
    return None, None

def show_winner (screen):
    if not winner:
        return
    font_winner = pygame.font.SysFont(None, 36)
    gold_color = (255, 215, 0)
    winner_name = ""
    if winner == BLACK_PLAYER :
        winner_name = "Black" 
    if winner == WHITE_PLAYER:
        winner_name = "White"
    if winner == 3:
        winner_name = "Draw"

    
    # 右侧信息区域起始位置（假设棋盘宽度是 board_width）
    info_x = 640  # 可以根据你的棋盘尺寸微调
    info_y = 200

    # 画一个背景框让文字更显眼
    pygame.draw.rect(screen, (60, 60, 60), (info_x, info_y - 20, 200, 80), border_radius=10)

    # 显示“Winner”标题
    title_text = font_winner.render("Winner:", True, gold_color)
    screen.blit(title_text, (info_x + 10, info_y - 10))

    # 显示赢家名字
    name_text = font_winner.render(winner_name, True, (255, 255, 255))
    screen.blit(name_text, (info_x + 10, info_y + 25))

# ---------------- 绘制函数 ----------------
def draw_board(surface,chat_box:ChatBox.ChatBox, hover_pos=None,):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    surface.fill(BOARD_BG)

    # 横竖线
    for i in range(BOARD_SIZE):
        pygame.draw.line(surface, BLACK, (MARGIN, MARGIN + i * CELL_SIZE),
                         (MARGIN + CELL_SIZE * (BOARD_SIZE - 1), MARGIN + i * CELL_SIZE), 1)
        pygame.draw.line(surface, BLACK, (MARGIN + i * CELL_SIZE, MARGIN),
                         (MARGIN + i * CELL_SIZE, MARGIN + CELL_SIZE * (BOARD_SIZE - 1)), 1)

    # 星位
    for ix in [3, 7, 11]:
        for iy in [3, 7, 11]:
            x, y = board_to_pixel(ix, iy)
            pygame.draw.circle(surface, BLACK, (x, y), 4)

    # 已落棋子
    for iy in range(BOARD_SIZE):
        for ix in range(BOARD_SIZE):
            val = board[iy][ix]
            if val != 0:
                x, y = board_to_pixel(ix, iy)
                color = BLACK if val == BLACK_PLAYER else WHITE
                pygame.draw.circle(surface, color, (x, y), CELL_SIZE // 2 - 2)

    # 鼠标悬浮预览
    if hover_pos:
        hx, hy = hover_pos
        if board[hy][hx] == 0 and board_enabled:
            x, y = board_to_pixel(hx, hy)
            color = LIGHT_BLACK if current_player == BLACK_PLAYER else LIGHT_WHITE
            pygame.draw.circle(surface, color, (x, y), CELL_SIZE // 2 - 2)

    # 右侧信息栏
    info_x = MARGIN * 2 + CELL_SIZE * (BOARD_SIZE - 1)
    pygame.draw.rect(surface, INFO_BG, (info_x, 0, INFO_WIDTH, WINDOW_HEIGHT))
    player_text = font.render(f"Current: {'Black' if current_player == BLACK_PLAYER else 'White'}", True, BLACK)
    
    step_text = font.render(f"Step time: {step_time}s", True, BLACK)
    surface.blit(player_text, (info_x + 20, 50))
    surface.blit(step_text, (info_x + 20, 80))
    if highlight_piece:
        pygame.draw.circle(surface, RED, board_to_pixel(highlight_piece[0],highlight_piece[1]), CELL_SIZE // 2, 3)
    if not board_enabled:
        gray_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        gray_overlay.set_alpha(120)  # 半透明灰
        gray_overlay.fill((150, 150, 150))
        surface.blit(gray_overlay, (0, 0))

    show_winner(surface)

    chat_box.draw(screen=surface)
    
    pygame.display.flip()

# draw and update the board with a new piece
def place_stone(x,y,player = current_player):
    board[y][x] = player
    SoundControl.place_sound.play()
    global highlight_piece
    highlight_piece = (x,y)

def get_this_player():
    return this_player