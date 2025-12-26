from GameConfig import *

def load_and_crop_to_circle(image_path, radius):
        """
        加载图片并裁剪成圆形
        
        参数:
            image_path: 图片文件路径
            radius: 圆形半径
        
        返回:
            circular_surface: 裁剪后的圆形图片表面
        """
        try:
            # 加载图片
            original_image = pygame.image.load(image_path).convert_alpha()
            
            # 计算直径
            diameter = radius * 2
            
            # 缩放图片到圆形大小
            scaled_image = pygame.transform.scale(original_image, (diameter, diameter))
            
            # 创建一个透明的表面用于最终结果
            circular_surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            
            # 方法1：使用圆形遮罩
            # 创建圆形遮罩
            mask = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)
            
            # 应用遮罩
            circular_surface.blit(scaled_image, (0, 0))
            circular_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            
            return circular_surface
            
        except pygame.error as e:
            print(f"无法加载图片: {e}")
            # 如果加载失败，返回一个默认的红色圆形
            default_surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA) # type: ignore
            pygame.draw.circle(default_surface, (255, 0, 0), (radius, radius), radius)
            return default_surface



class Button:
    def __init__(self, x, y, width, height = 0, is_circle = False, text = "", color=BLUE, hover_color=DARK_BLUE, 
                 text_color=WHITE, font_size=24, border_radius=8,image_path = "",enabled = True):
        if is_circle:
            self.image_path = image_path
            self.active = False
            self.coordinate = (x,y)
            self.width = width
            self.text = text
            self.is_hovered = False
            self.is_circle = True
        else:
            self.rect = pygame.Rect(x, y, width, height)
            self.text = text
            self.color = color
            self.hover_color = hover_color
            self.text_color = text_color
            self.font = pygame.font.Font(None, font_size)
            self.border_radius = border_radius
            self.is_hovered = False
        self.is_circle = is_circle
        self.enabled = enabled
        
    
    def draw(self, surface):
        """绘制按钮"""
        if self.is_circle:
            circular_image = load_and_crop_to_circle(self.image_path, 30)
            if self.check_hover(pygame.mouse.get_pos()):
                circular_image.fill((50, 50, 50, 0), special_flags=pygame.BLEND_RGB_SUB)  # 变暗
            image_rect = circular_image.get_rect(center=self.coordinate)
            surface.blit(circular_image, image_rect)
            draw_text(surface,self.text,(self.coordinate[0]+50,self.coordinate[1]-15))
        else:
            color = self.hover_color if self.check_hover(pygame.mouse.get_pos()) else self.color
            pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
            pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=self.border_radius)
            
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
    
    
    def check_hover(self, pos):
        if not self.enabled:
            return False
        if self.is_circle:
            """检查鼠标悬停"""
            # 计算鼠标位置与按钮圆心的距离
            distance = ((pos[0] - self.coordinate[0]) ** 2 + (pos[1] - self.coordinate[1]) ** 2) ** 0.5
            self.is_hovered = distance <= self.width
            return self.is_hovered
        else:
            self.is_hovered = self.rect.collidepoint(pos)
            return self.is_hovered
    
    def is_clicked(self, pos, event):
        if not self.enabled:
            print("a")
            return False
        if self.is_circle:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 计算鼠标位置与按钮圆心的距离
                distance = ((pos[0] - self.coordinate[0]) ** 2 + (pos[1] - self.coordinate[1]) ** 2) ** 0.5
                clicked = distance <= self.width
                return clicked
            return False
        else:

            """检查按钮是否被点击"""
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return self.rect.collidepoint(pos)
            return False
import pygame



def draw_text(surface, text, position, font_size=36, color=BLACK, font_name=None):
    """
    在指定表面绘制文字
    
    参数:
        surface: 要绘制文字的surface
        text: 要显示的文字
        position: 文字位置 (x, y)
        font_size: 字体大小
        color: 文字颜色
        font_name: 字体名称，None为默认字体
    """
    font = pygame.font.Font(font_name, font_size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)
    return text_surface.get_rect(topleft=position)

class Dialog:
    def __init__(self, base_surface,width=400, height=300, title="", has_input=False):
        """
        模态对话框类
        
        参数:
            base_surface: 基础界面（对话框将显示在这个界面上方）
            width: 对话框宽度
            height: 对话框高度
            title: 对话框标题
            has_input: 是否包含输入框
            input_text: 输入框默认文本
        """
        self.base_surface = base_surface
        self.width = width
        self.height = height
        self.title = title
        self.has_input = has_input
        self.visible = False
        self.result = None 
        
        # 计算对话框位置（居中）
        screen_rect = base_surface.get_rect()
        self.rect = pygame.Rect(
            (screen_rect.width - width) // 2,
            (screen_rect.height - height) // 2,
            width, height
        )
        
        
        # 创建按钮
        button_width = 100
        button_height = 40
        button_y = self.rect.bottom - 60
        button_x = self.rect.centerx - 120
        self.ok_button = Button(button_x, button_y, width = button_width, height = button_height,text="OK",color=GREEN,hover_color=DARK_GREEN)
        self.cancel_button = Button(button_x + 150,button_y,width = button_width, height = button_height,text="CANCEL",color=RED, hover_color=DARK_RED)

        # 输入框
        if has_input:
            self.input_rect = pygame.Rect(
                self.rect.left + 50,
                self.rect.top + 140,
                self.width - 100,
                40
            )
            self.input_active = False
        else:
            self.input_rect = None
            self.input_active = False
            
        # 消息文本
        self.message_lines = []
    

    def show(self, message=""):
        """显示对话框"""
        self.visible = True
        self.result = None
        self.input_text = ""
        self.set_message(message)
        
    def hide(self):
        """隐藏对话框"""
        self.visible = False
    
    def set_title(self, title):
        self.title = title

    def set_message(self, message):
        """设置对话框消息文本"""
        if not message:
            self.message_lines = []
            return
            
        # 简单的文本换行
        font = pygame.font.Font(None, 24)
        words = message.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = current_line + [word]
            test_text = ' '.join(test_line)
            test_width = font.size(test_text)[0]
            
            if test_width < self.width - 100:  # 留出边距
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                
        if current_line:
            lines.append(' '.join(current_line))
            
        self.message_lines = lines
        
    def handle_event(self, event):
        """处理对话框事件"""
        if not self.visible:
            return None
            
        mouse_pos = pygame.mouse.get_pos()
        
        # 处理鼠标点击
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 检查输入框点击
            if self.has_input and self.input_rect and self.input_rect.collidepoint(mouse_pos):
                self.input_active = True
            else:
                self.input_active = False
                
            # 检查按钮点击
            if self.ok_button.is_clicked(mouse_pos,event):
                self.hide()
                self.result = "OK"
                return "OK"
                
            if self.cancel_button.is_clicked(mouse_pos,event):
                self.hide()
                self.result = "CANCEL"
                return "CANCEL"
                
        # 处理键盘输入
        if event.type == pygame.KEYDOWN:
            if self.input_active and self.has_input:
                if event.key == pygame.K_RETURN:
                    self.input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.hide()
                    self.result = "CANCEL"
                    return "CANCEL"
                else:
                    # 限制输入长度
                    if len(self.input_text) < 20:
                        self.input_text += event.unicode
                        
            # 按ESC关闭对话框
            elif event.key == pygame.K_ESCAPE:
                self.hide()
                self.result = "CANCEL"
                return "CANCEL"
                
        return "BLOCKED"  # 阻止事件传递到基础界面

    def draw(self):
        """绘制对话框"""
        if not self.visible:
            return
            
        # 创建半透明遮罩表面
        overlay = pygame.Surface(self.base_surface.get_size(), pygame.SRCALPHA)
        overlay.fill(DARK_GRAY)
        self.base_surface.blit(overlay, (0, 0))
        
        # 绘制对话框背景
        pygame.draw.rect(self.base_surface, WHITE, self.rect, border_radius=12)
        pygame.draw.rect(self.base_surface, BLACK, self.rect, 3, border_radius=12)
        
        # 绘制标题栏
        title_rect = pygame.Rect(self.rect.left, self.rect.top, self.width, 50)
        pygame.draw.rect(self.base_surface, BLUE, title_rect, border_radius=12)
        pygame.draw.rect(self.base_surface, BLACK, title_rect, 2, border_radius=12)
        
        # 绘制标题文字
        font_title = pygame.font.Font(None, 28)
        title_surface = font_title.render(self.title, True, WHITE)
        title_text_rect = title_surface.get_rect(center=title_rect.center)
        self.base_surface.blit(title_surface, title_text_rect)
        
        # 绘制消息文本
        font_text = pygame.font.Font(None, 24)
        for i, line in enumerate(self.message_lines):
            text_surface = font_text.render(line, True, BLACK)
            text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.top + 90 + i * 30))
            self.base_surface.blit(text_surface, text_rect)
            
        # 绘制输入框（如果有）
        if self.has_input and self.input_rect:
            # 输入框背景
            input_color = BLUE if self.input_active else LIGHT_GRAY
            pygame.draw.rect(self.base_surface, input_color, self.input_rect, border_radius=6)
            pygame.draw.rect(self.base_surface, BLACK, self.input_rect, 2, border_radius=6)
            
            # 输入文本
            input_surface = font_text.render(self.input_text, True, BLACK)
            text_x = self.input_rect.x + 10
            text_y = self.input_rect.y + (self.input_rect.height - input_surface.get_height()) // 2
            self.base_surface.blit(input_surface, (text_x, text_y))
            
        # 绘制按钮
        self.ok_button.draw(self.base_surface)
        self.cancel_button.draw(self.base_surface)
        

    def get_result(self):
        """获取对话框结果"""
        return self.result
        
    def get_input_text(self):
        """获取输入框文本（仅当有输入框时有效）"""
        return self.input_text if self.has_input else ""
    
class ColorSelectDialog (Dialog):
    FONT = pygame.font.SysFont("arial", 15)
    def __init__(self, screen):
        super().__init__(screen, width=400, height=250, title="Choose your side", has_input=False)
        self.screen = screen
        self.selected = "black"  # 默认选择黑色
        self.running = True

    def get_selected_color(self):
        return self.selected
    
    def draw_radio(self, center, text, selected):
        pygame.draw.circle(self.screen, (0, 0, 0), center, 7, 2)
        if selected:
            pygame.draw.circle(self.screen, (0, 0, 0), center, 4)
        label = self.FONT.render(text, True, (0, 0, 0))
        self.screen.blit(label, (center[0] + 15, center[1] - 9))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # radio buttons
            if pygame.Rect(self.rect.x + 135, self.rect.y + 135, 200, 30).collidepoint(mx, my):
                self.selected = "black"
            if pygame.Rect(self.rect.x + 135, self.rect.y + 150, 200, 30).collidepoint(mx, my):
                self.selected = "white"
        return super().handle_event(event)
    
    def draw(self):
        super().draw()
        if self.visible:
            self.draw_radio(
                (self.rect.x + 145, self.rect.y + 135),
                "Black (First)",
                self.selected == "black"
            )
            self.draw_radio(
                (self.rect.x + 145, self.rect.y + 160),
                "White (Second)",
                self.selected == "white"
            )

import math
import pygame

class LoadingDialog(Dialog):
    def __init__(self, screen, width=400, height=200, title="Loading", message="Please wait..."):
        super().__init__(screen, width, height, title, has_input=False)
        self.screen = screen
        self.set_message(message)


        

        # override buttons: only CANCEL
        button_width = 100
        button_height = 40
        self.cancel_button = Button(
            self.rect.centerx - button_width // 2,
            self.rect.bottom - 55,
            width=button_width,
            height=button_height,
            text="CANCEL",
            color=RED,
            hover_color=DARK_RED
        )

         # loading animation config
        self.start_time = pygame.time.get_ticks()
        self.center = (self.rect.centerx - 80,
            self.rect.bottom - 35,)
        self.radius = 15
        self.dot_radius = 4
        self.dot_count = 8
        self.speed = 120  # ms per frame

    def handle_event(self, event):
        if not self.visible:
            return None

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.cancel_button.is_clicked(mouse_pos, event):
                self.hide()
                self.result = "CANCEL"
                return "CANCEL"

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide()
            self.result = "CANCEL"
            return "CANCEL"

        return "BLOCKED"

    def draw_loading_animation(self):
        """旋转圆点动画"""
        now = pygame.time.get_ticks()
        step = (now - self.start_time) // self.speed

        for i in range(self.dot_count):
            angle = 2 * math.pi * (i / self.dot_count)
            x = self.center[0] + math.cos(angle) * self.radius
            y = self.center[1] + math.sin(angle) * self.radius

            alpha = 255 if i == step % self.dot_count else 80
            dot_surface = pygame.Surface((self.dot_radius * 2, self.dot_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot_surface, (0, 0, 0, alpha), (self.dot_radius, self.dot_radius), self.dot_radius)

            self.screen.blit(dot_surface, (x - self.dot_radius, y - self.dot_radius))

    def draw(self):
        if not self.visible:
            return

        # 半透明遮罩
        overlay = pygame.Surface(self.base_surface.get_size(), pygame.SRCALPHA)
        overlay.fill(DARK_GRAY)
        self.base_surface.blit(overlay, (0, 0))

        # 对话框背景
        pygame.draw.rect(self.base_surface, WHITE, self.rect, border_radius=12)
        pygame.draw.rect(self.base_surface, BLACK, self.rect, 3, border_radius=12)

        # 标题栏
        title_rect = pygame.Rect(self.rect.left, self.rect.top, self.width, 50)
        pygame.draw.rect(self.base_surface, BLUE, title_rect, border_radius=12)
        pygame.draw.rect(self.base_surface, BLACK, title_rect, 2, border_radius=12)

        font_title = pygame.font.Font(None, 28)
        title_surface = font_title.render(self.title, True, WHITE)
        self.base_surface.blit(title_surface, title_surface.get_rect(center=title_rect.center))

        # message
        font_text = pygame.font.Font(None, 24)
        for i, line in enumerate(self.message_lines):
            text_surface = font_text.render(line, True, BLACK)
            self.base_surface.blit(
                text_surface,
                text_surface.get_rect(center=(self.rect.centerx, self.rect.top + 90 + i * 30))
            )

        # loading animation
        self.draw_loading_animation()

        # ❗️只画 CANCEL
        self.cancel_button.draw(self.base_surface)

class NotificationDialog(Dialog):
    def __init__(self, screen, width=400, height=200, title="Loading", message="Please wait..."):
        super().__init__(screen, width, height, title, has_input=False)
        self.screen = screen
        self.set_message(message)

        # override buttons: only CANCEL
        button_width = 100
        button_height = 40
        self.ok_button = Button(
            self.rect.centerx - button_width // 2,
            self.rect.bottom - 55,
            width=button_width,
            height=button_height,
            text="OK",
            color=GREEN,
            hover_color=DARK_GREEN
        )

    def handle_event(self, event):
        if not self.visible:
            return None

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.ok_button.is_clicked(mouse_pos, event):
                self.hide()
                self.result = "OK"
                return "OK"

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide()
            self.result = "OK"
            return "OK"

        return "BLOCKED"

    def draw(self):
        if not self.visible:
            return

        # 半透明遮罩
        overlay = pygame.Surface(self.base_surface.get_size(), pygame.SRCALPHA)
        overlay.fill(DARK_GRAY)
        self.base_surface.blit(overlay, (0, 0))

        # 对话框背景
        pygame.draw.rect(self.base_surface, WHITE, self.rect, border_radius=12)
        pygame.draw.rect(self.base_surface, BLACK, self.rect, 3, border_radius=12)

        # 标题栏
        title_rect = pygame.Rect(self.rect.left, self.rect.top, self.width, 50)
        pygame.draw.rect(self.base_surface, BLUE, title_rect, border_radius=12)
        pygame.draw.rect(self.base_surface, BLACK, title_rect, 2, border_radius=12)

        font_title = pygame.font.Font(None, 28)
        title_surface = font_title.render(self.title, True, WHITE)
        self.base_surface.blit(title_surface, title_surface.get_rect(center=title_rect.center))

        # message
        font_text = pygame.font.Font(None, 24)
        for i, line in enumerate(self.message_lines):
            text_surface = font_text.render(line, True, BLACK)
            self.base_surface.blit(
                text_surface,
                text_surface.get_rect(center=(self.rect.centerx, self.rect.top + 90 + i * 30))
            )

        # self.draw_loading_animation()

        # ❗️只画 OK
        self.ok_button.draw(self.base_surface)
