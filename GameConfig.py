import pygame

# Initialize pygame
pygame.init()

# --- Fonts ---
TITLE_FONT = pygame.font.SysFont("verdana", 50, bold=True)
SUB_FONT = pygame.font.SysFont("arial", 24)
TEXT_FONT = pygame.font.SysFont("arial", 18)

BOARD_BACKGROUND_COLOR = (240, 200, 120)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (240, 240, 240)
BLUE = (0, 120, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
DARK_BLUE = (0, 80, 200)
GOLD = (230, 180, 60)
DARK_WOOD = (100, 70, 40)
LIGHT_WOOD = (190, 150, 100)
DARK_GRAY = (50, 50, 50, 128)  # 半透明黑色遮罩
DARK_GREEN = (0, 150, 0)
DARK_RED = (200, 0, 0)

# players
BLACK_PLAYER = 1
WHITE_PLAYER = 2
SYSTEM = 0
