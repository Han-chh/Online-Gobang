import subprocess
import sys
from Connection import Connection
import GameLogic
from GameConfig import *
from UIComponents import *
from SoundControl import *
import BoardWindow
import time
import json
import os


#internet connection
# 程序启动时检查 player_data.txt
player_data_file = "player_data/player_data.txt"
os.makedirs("player_data", exist_ok=True)
if os.path.exists(player_data_file):
    try:
        with open(player_data_file, "r", encoding="utf-8") as f:
            player_data = json.load(f)
        player_id = player_data.get("username", "player1")
    except json.JSONDecodeError:
        player_id = "player1"
        # 如果文件损坏，创建默认
        player_data = {
            "player_id": player_id,
            "username": player_id,
            "registration_date": "2024-01-01T00:00:00",
            "last_login": "2024-01-01T00:00:00",
            "stats": {
                "games_played": 0,
                "games_won": 0,
                "games_lost": 0,
                "games_drawn": 0,
                "win_streak": 0,
                "max_win_streak": 0,
                "total_moves": 0,
                "total_time_played": 0
            },
            "preferences": {
                "theme": "default",
                "sound_enabled": True,
                "auto_save_replays": True
            },
            "game_history": []
        }
        with open(player_data_file, "w", encoding="utf-8") as f:
            json.dump(player_data, f, indent=2, ensure_ascii=False)
else:
    # 创建默认数据
    player_data = {
        "player_id": "player1",
        "username": "player1",
        "registration_date": "2024-01-01T00:00:00",
        "last_login": "2024-01-01T00:00:00",
        "stats": {
            "games_played": 0,
            "games_won": 0,
            "games_lost": 0,
            "games_drawn": 0,
            "win_streak": 0,
            "max_win_streak": 0,
            "total_moves": 0,
            "total_time_played": 0
        },
        "preferences": {
            "theme": "default",
            "sound_enabled": True,
            "auto_save_replays": True
        },
        "game_history": []
    }
    with open(player_data_file, "w", encoding="utf-8") as f:
        json.dump(player_data, f, indent=2, ensure_ascii=False)
    player_id = player_data.get("username", "player1")

connection = Connection(player_id)

# 移除全局标志，使用 connection 的属性
connection_lost_shown = False


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


# 添加定时器事件常量（在其他常量附近）
STEP_TIMER_EVENT = pygame.USEREVENT + 2

# 添加倒计时启动函数
def start_step_timer():
    """
    启动 step_time 倒计时，根据当前玩家减少相应时间，直到 0。
    """
    if BoardWindow.winner is not None:
        return  # 如果已有赢家，不启动计时器
    if BoardWindow.current_player == BoardWindow.this_player:
        if BoardWindow.player_step_time > 0:
            pygame.time.set_timer(STEP_TIMER_EVENT, 1000)
        else:
            # 己方时间到 0
            BoardWindow.winner = WHITE_PLAYER if BoardWindow.this_player == BLACK_PLAYER else BLACK_PLAYER
            BoardWindow.board_enabled = False
    else:
        if BoardWindow.opponent_step_time > 0:
            pygame.time.set_timer(STEP_TIMER_EVENT, 1000)
        else:
            # 对方时间到 0
            BoardWindow.winner = BoardWindow.this_player
            BoardWindow.board_enabled = False


def save_game_data(result, opponent="Unknown", moves_count=0):
    """保存游戏数据到玩家文件"""
    os.makedirs("player_data", exist_ok=True)
    
    # 加载现有数据
    if os.path.exists(player_data_file):
        try:
            with open(player_data_file, "r", encoding="utf-8") as f:
                player_data = json.load(f)
        except json.JSONDecodeError:
            player_data = None
    else:
        player_data = None
    
    if not player_data:
        # 创建默认数据
        player_data = {
            "player_id": player_id,
            "username": player_id,
            "registration_date": "2024-01-01T00:00:00",
            "last_login": "2024-01-01T00:00:00",
            "stats": {
                "games_played": 0,
                "games_won": 0,
                "games_lost": 0,
                "games_drawn": 0,
                "win_streak": 0,
                "max_win_streak": 0,
                "total_moves": 0,
                "total_time_played": 0
            },
            "preferences": {
                "theme": "default",
                "sound_enabled": True,
                "auto_save_replays": True
            },
            "game_history": []
        }
    
    # 更新统计
    stats = player_data["stats"]
    stats["games_played"] += 1
    stats["total_moves"] += moves_count
    
    if result == "win":
        stats["games_won"] += 1
        stats["win_streak"] += 1
        if stats["win_streak"] > stats["max_win_streak"]:
            stats["max_win_streak"] = stats["win_streak"]
    elif result == "loss":
        stats["games_lost"] += 1
        stats["win_streak"] = 0
    elif result == "draw":
        stats["games_drawn"] += 1
        stats["win_streak"] = 0
    
    # 添加游戏历史
    from datetime import datetime
    game_entry = {
        "opponent": opponent,
        "result": result,
        "moves_count": moves_count,
        "timestamp": datetime.now().isoformat()
    }
    player_data["game_history"].append(game_entry)
    
    # 保存数据
    with open(player_data_file, "w", encoding="utf-8") as f:
        json.dump(player_data, f, indent=2, ensure_ascii=False)


def initialize_mainUI():
    main_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Online Gobang - The Five Stones Legend")
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
                connection.disconnect()
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
                    myDialog.hide()
                    current_UI = BOARD_UI
                    game_screen: pygame.Surface = BoardWindow.initialize(connection)
                    connection.start()
                    start_step_timer()  # 启动倒计时
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

                elif result == "OK":
                    if connection_lost_shown:
                        current_UI = MAIN_UI
                        connection.disconnect()
                        connection_lost_shown = False
                        myDialog.hide()
                        continue

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
                    subprocess.run(["python3", "ProfileWindow.py", player_id])

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

            # 添加：处理倒计时事件
            if event.type == STEP_TIMER_EVENT:
                if BoardWindow.winner is not None:
                    pygame.time.set_timer(STEP_TIMER_EVENT, 0)  # 停止定时器
                    continue
                if BoardWindow.current_player == BoardWindow.this_player:
                    if BoardWindow.player_step_time > 0:
                        BoardWindow.player_step_time -= 1
                    else:
                        # 己方时间到 0
                        pygame.time.set_timer(STEP_TIMER_EVENT, 0)
                        BoardWindow.winner = WHITE_PLAYER if BoardWindow.this_player == BLACK_PLAYER else BLACK_PLAYER
                        BoardWindow.board_enabled = False
                        play_win_lose_draw_sound(BoardWindow.this_player, BoardWindow.winner)
                        connection.send_win_message(BoardWindow.winner)
                else:
                    if BoardWindow.opponent_step_time > 0:
                        BoardWindow.opponent_step_time -= 1
                    else:
                        # 对方时间到 0
                        pygame.time.set_timer(STEP_TIMER_EVENT, 0)
                        BoardWindow.winner = BoardWindow.this_player
                        BoardWindow.board_enabled = False
                        play_win_lose_draw_sound(BoardWindow.this_player, BoardWindow.winner)
                        connection.send_win_message(BoardWindow.winner)

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
                        BoardWindow.place_stone(hx,hy,BoardWindow.this_player)
                        connection.send_move_message(hx,hy,BoardWindow.current_player)
                        # 完成 move 后立即重置己方时间为初始值
                        BoardWindow.player_step_time = BoardWindow.step_time
                        has_winner = False
                        if GameLogic.check_win(BoardWindow.board,hx,hy,BoardWindow.BOARD_SIZE) == BLACK_PLAYER:
                            BoardWindow.winner = BLACK_PLAYER
                            
                            has_winner = True

                        if GameLogic.check_win(BoardWindow.board,hx,hy,BoardWindow.BOARD_SIZE) == WHITE_PLAYER:
                            BoardWindow.winner = WHITE_PLAYER
                            has_winner = True
                        if GameLogic.check_win(BoardWindow.board,hx,hy,BoardWindow.BOARD_SIZE) == DRAW:
                            has_winner = True
                            BoardWindow.winner = DRAW
                        if has_winner:
                            pygame.time.set_timer(STEP_TIMER_EVENT, 0)  # 停止定时器
                            # 计算移动数
                            moves_count = sum(1 for row in BoardWindow.board for cell in row if cell != 0)
                            # 确定结果
                            if BoardWindow.winner == BoardWindow.this_player:
                                result = "win"
                            elif BoardWindow.winner == DRAW:
                                result = "draw"
                            else:
                                result = "loss"
                            # 保存游戏数据
                            save_game_data(result, opponent=connection.opponent_user_id or "Unknown", moves_count=moves_count)
                            play_win_lose_draw_sound(BoardWindow.this_player,BoardWindow.winner)
                            connection.send_win_message(BoardWindow.winner)
                            BoardWindow.board_enabled = False
                            continue
                        BoardWindow.board_enabled = False
                        BoardWindow.current_player = WHITE_PLAYER if BoardWindow.current_player == BLACK_PLAYER else BLACK_PLAYER
                        # 重置对方时间并启动倒计时
                        if BoardWindow.current_player != BoardWindow.this_player:
                            BoardWindow.opponent_step_time = BoardWindow.step_time
                        step_timer_trigger = True
                    else:
                        print(f"落子失败: ({hx},{hy}) 已有棋子")
    
    # 移除旧的超时检查，使用新的倒计时逻辑

    # 检查倒计时触发
    if connection.step_timer_trigger:
        connection.step_timer_trigger = False
        start_step_timer()
    if connection.stop_timer_trigger:
        connection.stop_timer_trigger = False
        pygame.time.set_timer(STEP_TIMER_EVENT, 0)
    if connection.connection_lost and not connection_lost_shown:
        connection_lost_shown = True
        myDialog = NotificationDialog(main_screen, title="Connection Lost")
        myDialog.show("Connection to opponent lost. Click OK to return to main menu.")
        # 不立即切换 UI，等待 OK

    if current_UI == MAIN_UI:
        draw_mainUI()
    elif current_UI == BOARD_UI:
        BoardWindow.draw_board(game_screen,chat_box=BoardWindow.chat_box,hover_pos=hover_pos) # type: ignore



pygame.quit()
sys.exit()
