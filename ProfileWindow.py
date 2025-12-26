from pathlib import Path
import tkinter as tk
from tkinter import ttk
import json
import os
from PIL import Image, ImageTk, ImageDraw

PROFILE_WINDOW_WIDTH = 450
PROFILE_WINDOW_HEIGHT = 600


class ProfileWindow(tk.Tk):
    def __init__(self, player_id="player1"):
        super().__init__()
        self.player_id = player_id
        self.title(f"User Profile - {player_id}")
        self.configure(bg="white")
        self.resizable(width=False, height=False)
        self.center_window(PROFILE_WINDOW_WIDTH, PROFILE_WINDOW_HEIGHT)
        self.attributes("-topmost", True)

        # top title bar
        header_frame = tk.Frame(self, bg="white")
        header_frame.pack(fill="x", pady=15, padx=20)

        # load avatar
        image_dir = Path("Images")
        avatar = self.make_circle_avatar(image_dir/"DefaultUser.png", size=(70, 70))
        avatar_label = tk.Label(header_frame, image=avatar, bg="white")
        avatar_label.image = avatar # type: ignore
        avatar_label.pack(side="left", padx=(0, 20))

        # title and player's detail
        info_frame = tk.Frame(header_frame, bg="white")
        info_frame.pack(side="left", fill="both", expand=True)

        title_label = tk.Label(
            info_frame,
            text="Player Profile",
            font=("Helvetica", 18, "bold"),
            bg="white",
            anchor="w"
        )
        title_label.pack(anchor="w")

        player_label = tk.Label(
            info_frame,
            text=f"ID: {player_id}",
            font=("Helvetica", 12),
            bg="white",
            anchor="w",
            fg="gray"
        )
        player_label.pack(anchor="w", pady=(5, 0))

        # 滚动区域
        self.scroll_frame = self.create_scrollable_frame()
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 加载游戏历史和统计数据
        self.load_player_data()

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def make_circle_avatar(self, image_path, size=(70, 70)):
        """生成圆形头像"""
        try:
            img = Image.open(image_path).resize(size, Image.LANCZOS).convert("RGBA") # type: ignore
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            img.putalpha(mask)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading avatar: {e}")
            # 创建默认灰色圆形头像
            default_img = Image.new("RGBA", size, (200, 200, 200, 255))
            draw = ImageDraw.Draw(default_img)
            draw.ellipse((0, 0, size[0], size[1]), fill=(150, 150, 150, 255))
            return ImageTk.PhotoImage(default_img)

    def create_scrollable_frame(self):
        """创建可滚动内容区"""
        container = ttk.Frame(self)
        canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        container.scrollable_frame = scrollable_frame # type: ignore
        return container

    def load_player_data(self):
        """从玩家数据文件加载游戏历史和统计信息"""
        frame = self.scroll_frame.scrollable_frame # type: ignore

        # 清空旧内容
        for widget in frame.winfo_children():
            widget.destroy()

        # 检查玩家数据文件是否存在
        player_file = f"player_data/{self.player_id}.txt"
        if not os.path.exists(player_file):
            # 创建默认玩家数据
            self.create_default_player_data()

        # 加载玩家数据
        player_data = self.load_player_data_from_file(player_file)
        if not player_data:
            ttk.Label(frame, text="No player data available.", padding=10).pack(anchor="w")
            return

        # 显示统计信息
        self.display_statistics(frame, player_data)

        # 显示游戏历史
        self.display_game_history(frame, player_data)

    def create_default_player_data(self):
        """创建默认玩家数据"""
        default_data = {
            "player_id": self.player_id,
            "username": self.player_id,
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

        # 确保目录存在
        os.makedirs("player_data", exist_ok=True)

        # 保存默认数据
        with open(f"player_data/{self.player_id}.txt", "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)

    def load_player_data_from_file(self, file_path):
        """从文件加载玩家数据"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading player data: {e}")
            return None

    def display_statistics(self, frame, player_data):
        """显示玩家统计信息"""
        stats = player_data["stats"]
        total_games = stats["games_played"]
        wins = stats["games_won"]
        losses = stats["games_lost"]
        draws = stats["games_drawn"]

        # 计算胜率
        win_rate = (wins / total_games * 100) if total_games > 0 else 0

        # 统计信息框架
        stats_frame = ttk.Frame(frame, relief="solid", borderwidth=1)
        stats_frame.pack(fill="x", pady=(0, 15), padx=5)

        # 标题
        stats_title = ttk.Label(
            stats_frame,
            text="Player Statistics",
            font=("Helvetica", 14, "bold"),
            padding=10
        )
        stats_title.pack(anchor="w")

        # 统计内容
        stats_content = ttk.Label(
            stats_frame,
            text=(
                f"Total Games: {total_games}\n"
                f"Wins: {wins} | Losses: {losses} | Draws: {draws}\n"
                f"Win Rate: {win_rate:.1f}%\n"
                f"Current Win Streak: {stats['win_streak']}\n"
                f"Best Win Streak: {stats['max_win_streak']}\n"
                f"Total Moves: {stats['total_moves']}"
            ),
            font=("Helvetica", 11),
            padding=(0, 0, 0, 10)
        )
        stats_content.pack(anchor="w", padx=10)

    def display_game_history(self, frame, player_data):
        """显示游戏历史"""
        game_history = player_data.get("game_history", [])

        # 历史标题
        history_title = ttk.Label(
            frame,
            text="Recent Games",
            font=("Helvetica", 14, "bold"),
            padding=(0, 10, 0, 5)
        )
        history_title.pack(anchor="w")

        if not game_history:
            ttk.Label(
                frame,
                text="No games played yet.",
                font=("Helvetica", 10),
                padding=5
            ).pack(anchor="w")
            return

        # 显示最近的游戏（最多10个）
        recent_games = list(reversed(game_history))[:10]

        for i, game in enumerate(recent_games):
            # 确定结果颜色
            result = game.get("result", "unknown")
            if result == "win":
                result_color = "green"
                result_text = "Victory"
            elif result == "loss":
                result_color = "red"
                result_text = "Defeat"
            else:
                result_color = "gray"
                result_text = "Draw"

            # 游戏信息
            opponent = game.get("opponent", "Unknown")
            moves_count = game.get("moves_count", 0)
            timestamp = game.get("timestamp", "")[:16]  # 只显示日期和时间

            game_text = f"{i + 1}. vs {opponent} - {result_text} ({moves_count} moves)"

            # 游戏项目框架
            game_frame = ttk.Frame(frame)
            game_frame.pack(fill="x", pady=2)

            # 结果标签
            result_label = ttk.Label(
                game_frame,
                text=game_text,
                foreground=result_color,
                font=("Helvetica", 10),
                padding=5
            )
            result_label.pack(side="left", anchor="w")

            # 时间标签
            time_label = ttk.Label(
                game_frame,
                text=timestamp,
                foreground="gray",
                font=("Helvetica", 8),
                padding=5
            )
            time_label.pack(side="right", anchor="e")

def open_profile_window(player_id="player1"):
    """在您的主程序中调用此函数来打开个人资料窗口"""
    app = ProfileWindow(player_id)
    app.mainloop()

if __name__ == "__main__":
    # 检查是否提供了玩家ID参数
    import sys

    player_id = sys.argv[1] if len(sys.argv) > 1 else "player1"

    app = ProfileWindow(player_id)
    app.mainloop()
