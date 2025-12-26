import subprocess
import sys
from Connection import Connection
import GameLogic
from GameConfig import *
from UIComponents import *
from SoundControl import *
import BoardWindow
import time


#internet connection
connection = Connection()


STEP_TIME_DIALOG_TITLE = "Room Settings - Step Time"
CHOOSE_SIDE_DIALOG_TITLE = "Room Settings - Choose Side"
CREATE_ROOM_DIALOG_TITLE = "Create a room"
JOIN_ROOM_DIALOG_TITLE = "Join a room"
JOIN_LOADING_DIALOG_TITLE = "Joining Room"
WAITING_DIALOG_TITLE = f"Room {BoardWindow.room_id}"
CREATE_ROOM_FAILED_DIALOG_TITLE = "Invalid Room Settings"
ROOM_VERIFICATION_TITLE = "Room Verification"


# UI constants
MAIN_UI = 1
BOARD_UI = 2




# --- Screen settings ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

def initialize_mainUI():
    main_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Online Gobang - The Five Stones Legend")
    this_player = None
    return main_screen

main_screen = initialize_mainUI()
global game_screen


# --- Create UI Elements ---
title_text = TITLE_FONT.render("The Five Stones Legend", True, GOLD)
subtitle_text = SUB_FONT.render("Online Gobang", True, WHITE)

profile_label = SUB_FONT.render("Profile", True, WHITE)

profile_box = Button(100, 250, 20, is_circle=True, image_path="Images/DefaultUser.png")
sound_box = Button(100, 350, 30, is_circle= True, image_path ="Images/EnableSound.jpeg")

btn_create = Button(300, 280, 200, height=50, text="Create Room")
btn_join = Button(300, 350, 200, height=50, text="Join Room")

mainUI_buttons = [profile_box, sound_box, btn_create, btn_join]

# 创建对话框实例（在循环外创建）
myDialog = Dialog(main_screen, width=400, height=250, title="输入用户名", has_input=True)

# --- Main Loop ---
clock = pygame.time.Clock()
running = True
show_dialog = False  # 控制对话框显示状态




def set_buttons_enabled(buttons, enabled):
    for button in buttons:
        button.enabled = enabled


def draw_mainUI():
    # 更新鼠标位置（在事件循环外）
    MOUSE_POS = pygame.mouse.get_pos()
    # --- 绘制界面 ---
    main_screen.fill(DARK_WOOD)  # background base color
    pygame.draw.rect(main_screen, LIGHT_WOOD, (50, 50, 700, 500), border_radius=25)  # main panel

    # --- Decorative Title Area ---
    main_screen.blit(title_text, title_text.get_rect(center=(400, 120)))
    main_screen.blit(subtitle_text, subtitle_text.get_rect(center=(400, 180)))

    # --- CircularButton Section ---
    profile_box.draw(main_screen)
    sound_box.draw(main_screen)

    # --- Buttons ---
    btn_create.draw(main_screen)
    btn_join.draw(main_screen)

    # --- 绘制对话框（必须在所有其他绘制之后）---
    myDialog.draw()

    pygame.display.flip()
    clock.tick(30)

current_UI = MAIN_UI
hover_pos = None


play_bgm()
i = 0
while running:
    # --- Event Handling ---
    if myDialog.visible:
        set_buttons_enabled(mainUI_buttons, False)
    else:
        set_buttons_enabled(mainUI_buttons, True)
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            if current_UI == MAIN_UI:
                running = False

            elif current_UI == BOARD_UI:
                current_UI = MAIN_UI
                connection_flag = False
                initialize_mainUI()
            break
        
        if current_UI == MAIN_UI:
            

            # 如果对话框可见，优先处理对话框事件
            if myDialog.visible:
                result = myDialog.handle_event(event)
                step_time_str = 0
                # If connected, switch to board UI
                if connection.is_connected:
                    print("fffffff")
                    myDialog.hide()
                    current_UI = BOARD_UI
                    game_screen: pygame.Surface = BoardWindow.initialize(BoardWindow.chat_box)
                    # connection.start()
                    continue
                if myDialog.title == ROOM_VERIFICATION_TITLE:
                    if connection.has_existing_room:
                        myDialog = NotificationDialog(main_screen, title=CREATE_ROOM_FAILED_DIALOG_TITLE)
                        myDialog.show(f"Room {BoardWindow.room_id} already exists")
                    elif not connection.is_timeout:
                        continue
                    else:
                        myDialog = LoadingDialog(main_screen, title=WAITING_DIALOG_TITLE)
                        myDialog.show(f"Waiting for opponent...; Settings: step time: {BoardWindow.step_time}s, side: {"black" if BoardWindow.get_this_player() == BLACK_PLAYER else "white"}")
                        connection.wait_for_joining(BoardWindow.room_id)

                if connection.is_timeout and myDialog.title == JOIN_LOADING_DIALOG_TITLE:
                    myDialog = NotificationDialog(main_screen, title="Notification")
                    myDialog.show("Join room timeout. Please try again.")
                    connection.is_timeout = False
                    continue
                if result == "OK":
                    
                    if myDialog.title == JOIN_ROOM_DIALOG_TITLE:
                        # join room dialog handling
                        BoardWindow.room_id = myDialog.get_input_text()
                        if not BoardWindow.room_id:
                            myDialog = NotificationDialog(main_screen, title=CREATE_ROOM_FAILED_DIALOG_TITLE)
                            myDialog.show("Empty room id is not accepted")
                            continue
                        
                        # connecting & joining room
                        myDialog = LoadingDialog(main_screen, title=JOIN_LOADING_DIALOG_TITLE)
                        myDialog.show(f"Connecting to the room {BoardWindow.room_id}, please wait...")
                        connection.join_room(BoardWindow.room_id)

                        # successfully joined


                    elif myDialog.title == CREATE_ROOM_DIALOG_TITLE:
                        # create room handling
                        
                        BoardWindow.room_id = myDialog.get_input_text()
                        if not BoardWindow.room_id:
                            myDialog = NotificationDialog(main_screen, title=CREATE_ROOM_FAILED_DIALOG_TITLE)
                            myDialog.show("Empty room id is not accepted")
                            continue
                        myDialog.set_title(STEP_TIME_DIALOG_TITLE)
                        myDialog.show("Enter step time (5-300s, integer)")

                    elif myDialog.title == STEP_TIME_DIALOG_TITLE:
                        # step time TEXT handling
                        step_time_str = myDialog.get_input_text()
                        if not step_time_str.isdigit() or int(step_time_str) < 5 or int(step_time_str) > 300:
                            myDialog = NotificationDialog(main_screen, title=CREATE_ROOM_FAILED_DIALOG_TITLE)
                            myDialog.show("Step time must be an integer between 5 and 300")
                            continue
                        BoardWindow.step_time = int(step_time_str)
                        myDialog = ColorSelectDialog(main_screen)
                        myDialog.set_title(CHOOSE_SIDE_DIALOG_TITLE)
                        myDialog.show("Black or White? (black goes first)")
                    elif myDialog.title == CHOOSE_SIDE_DIALOG_TITLE:
                        BoardWindow.this_player = BLACK_PLAYER if myDialog.get_selected_color() == "black" else WHITE_PLAYER # type: ignore
                        # wait for opponent to join
                        WAITING_DIALOG_TITLE = f"Room {BoardWindow.room_id}"
                        myDialog = LoadingDialog(main_screen, title=ROOM_VERIFICATION_TITLE)
                        myDialog.show("Verifing your room...")
                        connection.existing_room_detection(room_id=BoardWindow.room_id)
                        
                    if myDialog.visible:
                        continue
                    print("用户点击了确定")

                elif result == "CANCEL":
                    if myDialog.title == JOIN_LOADING_DIALOG_TITLE or myDialog.title == WAITING_DIALOG_TITLE or ROOM_VERIFICATION_TITLE:
                        connection.cancle_waiting()
                    print("用户点击了取消")
                continue  # 阻止关闭对话框时进行其他事件处理


            # 主窗口事件处理（只有在对话框不可见时才执行）
            MOUSE_POS = pygame.mouse.get_pos()

            # 检查按钮点击
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_create.is_clicked(MOUSE_POS, event):
                    print("创建房间按钮被点击")
                    myDialog.set_title("Create a room")
                    myDialog = Dialog(main_screen, width=400, height=250, title=CREATE_ROOM_DIALOG_TITLE, has_input=True)
                    myDialog.show("Enter a room id to create a room, cannot be empty")

                if btn_join.is_clicked(MOUSE_POS, event):
                    print("加入房间按钮被点击")
                    myDialog = Dialog(main_screen, width=400, height=250, title=JOIN_ROOM_DIALOG_TITLE, has_input=True)
                    myDialog.set_title("Join a room")
                    myDialog.show("Enter the room's id you want to join, cannot be empty")

                # 检查其他圆形按钮的点击
                if profile_box.is_clicked(MOUSE_POS, event):
                    print("个人资料按钮被点击")
                    # 启动 profile 窗口（tkinter）为独立进程
                    subprocess.run(["python3", "ProfileWindow.py"])

                if sound_box.is_clicked(MOUSE_POS, event):
                    print("声音设置按钮被点击")
                    GameSound = not GameSound
                    if not GameSound:
                        sound_box.image_path = "Images/DisenableSound.jpg"
                        mixer.music.set_volume(0)
                        for s in all_sounds:
                            s.set_volume(0)
                    else:
                        sound_box.image_path = "Images/EnableSound.jpeg"
                        mixer.music.set_volume(0.5)
                        for s in all_sounds:
                            s.set_volume(0.5)
        elif current_UI == BOARD_UI:

            BoardWindow.chat_box.handle_event(event = event)
            if not BoardWindow.board_enabled:
                continue
            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                ix, iy = BoardWindow.pixel_to_board(mx, my)
                hover_pos = (ix, iy) if ix is not None else None

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hover_pos:
                    hx, hy = hover_pos
                    # 数组行与列是相反的
                    if BoardWindow.board[hy][hx] == 0: # type: ignore
                        BoardWindow.place_stone(hx,hy)
                        connection.send_move_message(hx,hy,BoardWindow.current_player)
                        has_winner = False
                        if GameLogic.check_win(BoardWindow.board,hx,hy,BoardWindow.BOARD_SIZE) == 1:
                            BoardWindow.winner = BLACK_PLAYER
                            
                            has_winner = True

                        if GameLogic.check_win(BoardWindow.board,hx,hy,BoardWindow.BOARD_SIZE) == 2:
                            BoardWindow.winner = WHITE_PLAYER
                            
                            has_winner = True

                        if GameLogic.check_win(BoardWindow.board,hx,hy,BoardWindow.BOARD_SIZE) == 2:
                            BoardWindow.winner = WHITE_PLAYER
                            
                            has_winner = True
                        if has_winner:
                            if BoardWindow.get_this_player() == BoardWindow.winner:
                                win_sound.play()
                            else:
                                lose_sound.play()
                            connection.send_win_message(BoardWindow.winner)
                            BoardWindow.board_enabled = False
                            continue
                        BoardWindow.board_enabled = False
                        BoardWindow.current_player = WHITE_PLAYER if BoardWindow.current_player == BLACK_PLAYER else BLACK_PLAYER
                    else:
                        print(f"落子失败: ({hx},{hy}) 已有棋子")
    
    now_time = int(round(time.time() * 1000))
    if BoardWindow.step_time <= 0:
        if BoardWindow.current_player == 1:
            BoardWindow.winner = WHITE_PLAYER
        else:
            BoardWindow.winner = BLACK_PLAYER
        BoardWindow.board_enabled = False

    if current_UI == MAIN_UI:
        draw_mainUI()
    elif current_UI == BOARD_UI:
        BoardWindow.draw_board(game_screen,chat_box=BoardWindow.chat_box,hover_pos=hover_pos) # type: ignore



pygame.quit()
sys.exit()
