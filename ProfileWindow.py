from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

PROFILE_WINDOW_WIDTH = 450
PROFILE_WINDOW_HEIGHT = 600


class ProfileWindow(tk.Tk):
    DEFAULT_USER_NAME = "player"
    def __init__(self):
        super().__init__()
        self.title("User Profile")
        self.configure(bg="white")
        self.resizable(False, False)
        self.center_window(PROFILE_WINDOW_WIDTH, PROFILE_WINDOW_HEIGHT)
        self.attributes("-topmost", True)
        self.user_id = self.DEFAULT_USER_NAME
        self.avatar_text_id = None

        # ===== Header =====
        self.header_frame = tk.Frame(self, bg="white")
        self.header_frame.pack(fill="x", pady=15, padx=20)

        image_dir = Path("Images")
        self.avatar_canvas = self.make_circle_avatar(self.header_frame, size=(70, 70), text=self.user_id[0])
        self.avatar_canvas.pack(side="left", padx=(0, 20))

        info_frame = tk.Frame(self.header_frame, bg="white")
        info_frame.pack(side="left", fill="both", expand=True)

        tk.Label(
            info_frame,
            text="Player Profile",
            font=("Helvetica", 18, "bold"),
            bg="white",
            anchor="w"
        ).pack(anchor="w")

        self.player_label = tk.Label(
            info_frame,
            text="Username: player",
            font=("Helvetica", 12),
            bg="white",
            fg="gray",
            anchor="w"
        )
        self.player_label.pack(anchor="w", pady=(5, 0))

        tk.Button(
            info_frame,
            text="Change Username",
            command=self.rename_user,
            font=("Helvetica", 10),
            bg="lightblue"
        ).pack(anchor="w", pady=(5, 0))

        # ===== Scroll Area =====
        self.scroll_frame = self.create_scrollable_frame()
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # ===== Load Data =====
        self.load_player_data()

    # ------------------------------------------------------------------

    def rename_user(self):
        dialog = tk.Toplevel(self)
        dialog.title("Change Username")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)

        # Center the dialog on the screen
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 300) // 2
        y = (dialog.winfo_screenheight() - 150) // 2  
        dialog.geometry(f"300x150+{x}+{y}")

        tk.Label(dialog, text="Enter new username:", font=("Helvetica", 12)).pack(pady=10)

        entry = tk.Entry(dialog, font=("Helvetica", 12))
        entry.pack(padx=20, fill="x")
        entry.focus()

        def save_username():
            new_username = entry.get().strip()
            self.user_id = new_username
            if not new_username:
                return

            player_file = "player_data/player_data.txt"
            try:
                with open(player_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["username"] = new_username
                with open(player_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                self.player_label.config(text=f"Username: {new_username}")
                self.update_avatar_text(new_username[0])
                self.load_player_data()

            except Exception as e:
                messagebox.showerror("Error", str(e))

            dialog.destroy()

        tk.Button(dialog, text="Save", command=save_username).pack(pady=10)

    # ------------------------------------------------------------------

    def center_window(self, w, h):
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def make_circle_avatar(self, parent, size, text):
        canvas = tk.Canvas(parent, width=size[0], height=size[1], bg="white", highlightthickness=0)
        canvas.create_oval(2, 2, size[0]-2, size[1]-2, fill="lightblue", outline="gray")
        self.avatar_text_id = canvas.create_text(size[0]//2, size[1]//2, text=text, font=("Helvetica", 20, "bold"), fill="white")
        return canvas

    def update_avatar_text(self, text):
        if self.avatar_text_id is not None:
            self.avatar_canvas.itemconfig(self.avatar_text_id, text=text)

    # ------------------------------------------------------------------

    def create_scrollable_frame(self):
        container = ttk.Frame(self)
        canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        container.scrollable_frame = frame # type: ignore
        return container

    # ------------------------------------------------------------------

    def load_player_data(self):
        frame = self.scroll_frame.scrollable_frame # type: ignore

        for w in frame.winfo_children():
            w.destroy()

        os.makedirs("player_data", exist_ok=True)
        path = "player_data/player_data.txt"

        if not os.path.exists(path):
            self.create_default_player_data()

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.user_id = data.get('username')
        self.player_label.config(text=f"Username: {data.get('username', 'player')}")
        self.update_avatar_text(self.user_id[0])

        self.display_statistics(frame, data)
        self.display_game_history(frame, data)

    # ------------------------------------------------------------------

    def create_default_player_data(self):
        data = {
            "username": self.DEFAULT_USER_NAME,
            "stats": {
                "games_played": 0,
                "games_won": 0,
                "games_lost": 0,
                "games_drawn": 0,
                "win_streak": 0,
                "max_win_streak": 0,
                "total_moves": 0
            },
            "game_history": []
        }
        with open("player_data/player_data.txt", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # ------------------------------------------------------------------

    def display_statistics(self, frame, data):
        stats = data["stats"]
        total = stats["games_played"]
        win_rate = (stats["games_won"] / total * 100) if total else 0

        box = tk.Frame(frame, relief="solid", borderwidth=1)
        box.pack(fill="x", pady=10)

        tk.Label(box, text="Player Statistics",
                 font=("Helvetica", 14, "bold")).pack(anchor="w", padx=10, pady=10)

        tk.Label(
            box,
            text=(
                f"Total Games: {total}\n"
                f"Wins: {stats['games_won']} | "
                f"Losses: {stats['games_lost']} | "
                f"Draws: {stats['games_drawn']}\n"
                f"Win Rate: {win_rate:.1f}%\n"
                f"Win Streak: {stats['win_streak']} (Max {stats['max_win_streak']})\n"
                f"Total Moves: {stats['total_moves']}"
            ),
            justify="left"
        ).pack(anchor="w", padx=10, pady=(0, 10))

    # ------------------------------------------------------------------

    def display_game_history(self, frame, data):
        tk.Label(frame, text="Recent Games",
                 font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(10, 5))

        history = data.get("game_history", [])
        if not history:
            tk.Label(frame, text="No games played yet.",
                     font=("Helvetica", 10), fg="gray").pack(anchor="w")
            return

        for i, g in enumerate(reversed(history[-10:]), 1):
            result = g.get("result", "draw")
            color = {"win": "green", "loss": "red"}.get(result, "gray")
            text = f"{i}. vs {g.get('opponent', 'Unknown')} - {result.capitalize()}"
            tk.Label(frame, text=text, fg=color).pack(anchor="w")


# ----------------------------------------------------------------------

if __name__ == "__main__":
    ProfileWindow().mainloop()
