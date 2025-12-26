import pygame
import datetime
import BoardWindow
from GameConfig import *  # 引用全局字体

class ChatBox:
    
    def __init__(self, x, y, width, height, connection,font=TEXT_FONT,
                 bg_color=(235, 235, 235), text_color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.connection = connection

        self.chat = ""
        self.chat_flag = 1
        self.action_chat = 1

        # 聊天信息区域偏移
        self.scroll_offset_y = 0
        self.scroll_offset_x = 0  # ✅ 水平滚动偏移量
        self.scroll_speed_y = 30
        self.scroll_speed_x = 40

        # 输入框
        self.input_height = 40
        self.input_rect = pygame.Rect(x + 5, y + height - self.input_height - 5,
                                      width - 10, self.input_height)
        self.input_text = ""
        self.input_active = False
        self.input_color_active = (255, 255, 255)
        self.input_color_inactive = (220, 220, 220)
        self.input_cursor_offset = 0  # 输入框水平滚动偏移

        # 消息记录
        self.messages = []

    # sender: int
    def add_message(self, sender, text,timestamp = datetime.datetime.now().strftime("%H:%M:%S")):
        """添加消息"""
        sys_color = (200, 80, 80)
        sender_str = "Black" if sender == BLACK_PLAYER else "White" if sender == WHITE_PLAYER else "System"
        prefix = f"[{sender_str} {timestamp}]"
        if sender == SYSTEM:
            sender_color = sys_color
        else:
            sender_color = (0, 0, 160) if sender == BoardWindow.get_this_player() else (160, 0, 0)

        # ✅ 第一行：prefix
        self.messages.append((prefix, sender_color))

        # ✅ 第二行：消息内容（自动换行）
        wrapped_lines = self.wrap_text(text, self.rect.width * 2)
        for line in wrapped_lines:
            self.messages.append((line, self.text_color))
        # ✅ 自动滚到底部
        self.scroll_offset_y = max(0, len(self.messages) * 22 - (self.rect.height - self.input_height - 60))

    def wrap_text(self, text, max_width):
        """自动换行"""
        words = text.split(' ')
        lines, current_line = [], ""
        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        return lines

    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 判断是否点击输入框
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
            else:
                self.input_active = False

            # 聊天记录垂直滚动
            if self.rect.collidepoint(event.pos):
                if event.button == 4:  # 滚轮上
                    self.scroll_offset_y = max(0, self.scroll_offset_y - self.scroll_speed_y)
                elif event.button == 5:  # 滚轮下
                    self.scroll_offset_y += self.scroll_speed_y

        elif event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_RETURN:
                    self.chat = str(self.input_text)
                    self.chat_flag = BoardWindow.current_player
                    self.action_chat += 1
                    if self.input_text.strip():
                        
                        self.add_message(BoardWindow.this_player, self.input_text)

                        self.connection.send_chat_message(BoardWindow.this_player, self.input_text, datetime.datetime.now().strftime("%H:%M:%S"))
                        self.input_text = ""
                        self.input_cursor_offset = 0
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                    self.input_cursor_offset = max(0, self.input_cursor_offset - 1)
                else:
                    self.input_text += event.unicode
                    # 如果输入文字超出输入框，增加偏移量
                    if self.font.size(self.input_text)[0] - self.input_cursor_offset > self.input_rect.width - 20:
                        self.input_cursor_offset += 10

            # ✅ 允许用方向键控制聊天框水平滚动
            if event.key == pygame.K_LEFT:
                self.scroll_offset_x = max(0, self.scroll_offset_x - self.scroll_speed_x)
            elif event.key == pygame.K_RIGHT:
                self.scroll_offset_x += self.scroll_speed_x

    def draw(self, screen):
        """绘制聊天框"""
        # 背景
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (180, 180, 180), self.rect, 2, border_radius=10)

        # 标题栏
        title_surf = self.font.render("Chat Box", True, (50, 50, 50))
        screen.blit(title_surf, (self.rect.x + 10, self.rect.y + 8))
        instruction_surf = self.font.render("Horizontally: ← →", True, (50, 50, 50))
        screen.blit(instruction_surf, (self.rect.x + 10, self.rect.y + 30))
        instruction_surf = self.font.render("Vertically: Mouse", True, (50, 50, 50))
        screen.blit(instruction_surf, (self.rect.x + 10, self.rect.y + 50))


        # 聊天显示区域
        clip_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 74,
                                self.rect.width - 20, self.rect.height - self.input_height - 45)
        surface = pygame.Surface((clip_rect.width, clip_rect.height))
        surface.fill(self.bg_color)

        y_offset = -self.scroll_offset_y
        for line, color in self.messages:
            text_surf = self.font.render(line, True, color)
            surface.blit(text_surf, (-self.scroll_offset_x, y_offset))  # ✅ 水平偏移生效
            y_offset += 22

        screen.blit(surface, (clip_rect.x, clip_rect.y))

        # 输入框
        color = self.input_color_active if self.input_active else self.input_color_inactive
        pygame.draw.rect(screen, color, self.input_rect, border_radius=8)
        pygame.draw.rect(screen, (150, 150, 150), self.input_rect, 1, border_radius=8)

        # 输入框文字（水平滚动）
        text_surf = self.font.render(self.input_text, True, (0, 0, 0))
        text_width = text_surf.get_width()
        visible_surface = pygame.Surface((self.input_rect.width - 20, self.input_rect.height - 10))
        visible_surface.fill(color)

        # 裁剪显示区域
        start_x = max(0, text_width - visible_surface.get_width())
        visible_surface.blit(text_surf, (-start_x, 0))
        screen.blit(visible_surface, (self.input_rect.x + 10, self.input_rect.y + 8))
