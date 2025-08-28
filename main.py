import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import random
import os
from collections import Counter
import string
import json
import hashlib
import datetime
import requests  # Add to imports
from tkinter import font as tkfont

COLORS = {
    "bg": "#e3f2fd",           # Soft blue
    "board_bg": "#e3f2fd",     # Match board background
    "tile_empty": "#e0e0e0",   # Lighter tile
    "tile_text": "#22223b",    # Dark text for empty tiles
    "green": "#6aaa64",
    "yellow": "#c9b458",
    "gray": "#bdbdbd",         # Softer gray
    "key_bg": "#bbdefb",       # Soft blue for keys
    "key_fg": "#22223b",       # Dark text for keys
    "key_disabled_bg": "#bdbdbd",
    "tile_border": "#90caf9",  # Soft blue border
    "tile_active": "#64b5f6"   # Slightly darker blue for active
}

ROWS = 6
COLS = 5

FALLBACK_WORDS = [
    "about","other","which","their","there","apple","grape","mango","peach","berry",
    "lemon","melon","chair","table","plant","glass","stone","flame","cloud","dream",
    "crash","trace","place","spare","share","stare","crate","slate","brave","blink",
    "pride","drive","bring","sling","sugar","cider","orbit","vivid","cabin","knock",
    "rinse","smile","snack","track","video","zesty","quick","jazzy","fuzzy","piano"
]

def load_words_from_file(filename="words_5.txt"):
    if not os.path.exists(filename):
        return None
    words = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            w = line.strip().lower()
            if len(w) == 5 and w.isalpha():
                words.append(w)
    return sorted(set(words))

def score_guess(guess, target):
    result = [0] * 5
    counts = Counter(target)
    for i in range(5):
        if guess[i] == target[i]:
            result[i] = 2
            counts[guess[i]] -= 1
    for i in range(5):
        if result[i] == 0 and counts.get(guess[i], 0) > 0:
            result[i] = 1
            counts[guess[i]] -= 1
    return result

def get_daily_word(words):
    today = datetime.date.today().isoformat()
    idx = int(hashlib.sha256(today.encode()).hexdigest(), 16) % len(words)
    return words[idx]

def get_definition(word):
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if isinstance(data, list) and "meanings" in data[0]:
            meanings = data[0]["meanings"]
            if meanings and "definitions" in meanings[0]:
                definition = meanings[0]["definitions"][0].get("definition", "")
                return definition
        return "No definition found."
    except Exception:
        return "No definition found."

# Stats functions
STATS_FILE = "wordle_stats.json"

def load_all_stats():
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_all_stats(all_stats):
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(all_stats, f)
    except Exception:
        pass

def get_player_stats(all_stats, player):
    return all_stats.get(player, {"games": 0, "wins": 0, "streak": 0, "max_streak": 0})

def show_leaderboard_popup(master, all_stats):
    popup = tk.Toplevel(master)
    popup.title("Leaderboard")
    popup.configure(bg=COLORS["bg"])
    popup.grab_set()
    tk.Label(
        popup,
        text="🏆 Leaderboard: Best Streaks",
        font=("Helvetica Neue", 18, "bold"),
        bg=COLORS["bg"],
        fg="#1976d2"
    ).pack(pady=(18, 10))
    sorted_stats = sorted(all_stats.items(), key=lambda x: x[1].get("max_streak", 0), reverse=True)
    for i, (player, stats) in enumerate(sorted_stats[:10], 1):
        rank_color = "#ffd700" if i == 1 else "#c0c0c0" if i == 2 else "#cd7f32" if i == 3 else "#22223b"
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else ""
        tk.Label(
            popup,
            text=f"{emoji} {i}. {player}",
            font=("Helvetica Neue", 14, "bold"),
            bg=COLORS["bg"],
            fg=rank_color,
            anchor="w",
            justify="left"
        ).pack(fill="x", padx=24)
        tk.Label(
            popup,
            text=f"Max Streak: {stats.get('max_streak', 0)}   Games: {stats.get('games', 0)}   Wins: {stats.get('wins', 0)}",
            font=("Helvetica Neue", 12),
            bg=COLORS["bg"],
            fg="#333333",
            anchor="w",
            justify="left"
        ).pack(fill="x", padx=36, pady=(0, 6))
    tk.Button(
        popup,
        text="Close",
        font=("Helvetica Neue", 12, "bold"),
        bg=COLORS["gray"],
        fg="#22223b",
        relief="flat",
        padx=16,
        pady=8,
        command=popup.destroy
    ).pack(pady=16)

def show_stats_popup(master, stats):
    popup = tk.Toplevel(master)
    popup.title("Wordle Stats")
    popup.configure(bg=COLORS["bg"])
    popup.grab_set()
    tk.Label(
        popup,
        text="📊 Your Stats",
        font=("Helvetica Neue", 18, "bold"),
        bg=COLORS["bg"],
        fg="#1976d2"
    ).pack(pady=(18, 10))
    stat_font = ("Helvetica Neue", 14, "bold")
    value_font = ("Helvetica Neue", 14)
    tk.Label(
        popup,
        text=f"Games Played:",
        font=stat_font,
        bg=COLORS["bg"],
        fg="#22223b",
        anchor="w"
    ).pack(fill="x", padx=32)
    tk.Label(
        popup,
        text=f"{stats['games']}",
        font=value_font,
        bg=COLORS["bg"],
        fg="#1976d2",
        anchor="w"
    ).pack(fill="x", padx=48)
    tk.Label(
        popup,
        text=f"Wins:",
        font=stat_font,
        bg=COLORS["bg"],
        fg="#22223b",
        anchor="w"
    ).pack(fill="x", padx=32)
    tk.Label(
        popup,
        text=f"{stats['wins']}",
        font=value_font,
        bg=COLORS["bg"],
        fg="#6aaa64",
        anchor="w"
    ).pack(fill="x", padx=48)
    tk.Label(
        popup,
        text=f"Current Streak:",
        font=stat_font,
        bg=COLORS["bg"],
        fg="#22223b",
        anchor="w"
    ).pack(fill="x", padx=32)
    tk.Label(
        popup,
        text=f"{stats['streak']}",
        font=value_font,
        bg=COLORS["bg"],
        fg="#c9b458",
        anchor="w"
    ).pack(fill="x", padx=48)
    tk.Label(
        popup,
        text=f"Max Streak:",
        font=stat_font,
        bg=COLORS["bg"],
        fg="#22223b",
        anchor="w"
    ).pack(fill="x", padx=32)
    tk.Label(
        popup,
        text=f"{stats['max_streak']}",
        font=value_font,
        bg=COLORS["bg"],
        fg="#6aaa64",
        anchor="w"
    ).pack(fill="x", padx=48)
    tk.Button(
        popup,
        text="Close",
        font=("Helvetica Neue", 12, "bold"),
        bg=COLORS["gray"],
        fg="#22223b",
        relief="flat",
        padx=16,
        pady=8,
        command=popup.destroy
    ).pack(pady=16)

class MainMenu(tk.Frame):
    def __init__(self, master, start_callback, exit_callback, show_stats_callback, toggle_daily_callback, daily_mode, toggle_hard_callback, hard_mode, show_leaderboard_callback, player_name):
        super().__init__(master, bg=COLORS["bg"])
        self.start_callback = start_callback
        self.exit_callback = exit_callback
        self.show_stats_callback = show_stats_callback
        self.toggle_daily_callback = toggle_daily_callback
        self.daily_mode = daily_mode
        self.toggle_hard_callback = toggle_hard_callback
        self.hard_mode = hard_mode
        self.show_leaderboard_callback = show_leaderboard_callback
        self.player_name = player_name

        # Heading
        tk.Label(self, text="WORDLE", font=("Helvetica Neue", 32, "bold"),
                 bg=COLORS["bg"], fg="#22223b").pack(pady=(30, 10))

        # Player name
        tk.Label(self, text=f"Player: {self.player_name}", font=("Helvetica Neue", 14, "bold"),
                 bg=COLORS["bg"], fg="#1976d2").pack(pady=(0, 8))

        # Instructions
        instructions = (
            "Welcome to Wordle!\n\n"
            "Rules:\n"
            "- Guess the 5-letter word in 6 tries.\n"
            "- Each guess must be a valid word.\n"
            "- After each guess, the color of the tiles will change to show how close your guess was to the word.\n"
            "  • Green: Correct letter, correct place\n"
            "  • Yellow: Correct letter, wrong place\n"
            "  • Gray: Letter not in the word\n\n"
            "Hard Mode:\n"
            "- If a letter is revealed as green or yellow, you must use it in your next guess.\n"
            "Controls:\n"
            "- Type letters or use the on-screen keyboard.\n"
            "- Press Enter to submit, Backspace to delete.\n"
        )
        tk.Label(self, text=instructions, font=("Helvetica Neue", 12),
                 bg=COLORS["bg"], fg="#333333", justify="left", wraplength=420).pack(pady=(0, 20))

        btn_style = {"font":("Helvetica Neue", 13, "bold"), "relief":"flat", "padx":18, "pady":10}
        tk.Button(self, text="Start Game", bg=COLORS["green"], fg="white",
                  command=self.start_callback, **btn_style).pack(pady=8)
        tk.Button(self, text="Stats", bg=COLORS["yellow"], fg="#22223b",
                  command=self.show_stats_callback, **btn_style).pack(pady=4)
        tk.Button(self, text="Leaderboard", bg=COLORS["key_bg"], fg="#22223b",
                  command=self.show_leaderboard_callback, **btn_style).pack(pady=4)

        self.daily_btn = tk.Button(self, text=self._daily_text(),
                  font=("Helvetica Neue", 12, "bold"),
                  bg="#fffde7", fg="#22223b", relief="ridge", padx=12, pady=6,
                  command=self.toggle_daily)
        self.daily_btn.pack(pady=4)

        self.hard_btn = tk.Button(self, text=self._hard_text(),
                  font=("Helvetica Neue", 12, "bold"),
                  bg="#fffde7", fg="#22223b", relief="ridge", padx=12, pady=6,
                  command=self.toggle_hard)
        self.hard_btn.pack(pady=4)

        tk.Button(self, text="Exit", font=("Helvetica Neue", 12, "bold"),
                  bg="#e57373", fg="white", relief="flat", padx=18, pady=10,
                  command=self.exit_callback).pack(pady=8)

    def _daily_text(self):
        return "Mode: Daily Challenge" if self.daily_mode else "Mode: Classic"

    def toggle_daily(self):
        self.daily_mode = not self.daily_mode
        self.daily_btn.config(text=self._daily_text())
        self.toggle_daily_callback(self.daily_mode)

    def _hard_text(self):
        return "Hard Mode: ON" if self.hard_mode else "Hard Mode: OFF"

    def toggle_hard(self):
        self.hard_mode = not self.hard_mode
        self.hard_btn.config(text=self._hard_text())
        self.toggle_hard_callback(self.hard_mode)

class WordleApp(tk.Frame):
    def __init__(self, master, back_to_menu_callback, stats, daily_mode_getter, hard_mode_getter, player_name, all_stats):
        super().__init__(master, bg=COLORS["bg"])
        self.master = master
        self.back_to_menu_callback = back_to_menu_callback
        self.stats = stats
        self.daily_mode_getter = daily_mode_getter
        self.hard_mode_getter = hard_mode_getter
        self.player_name = player_name
        self.all_stats = all_stats

        file_words = load_words_from_file("words_5.txt")
        self.allowed_words = file_words if file_words else FALLBACK_WORDS[:]
        self.answers = self.allowed_words

        self.row = 0
        self.col = 0
        self.game_over = False
        self.current_letters = [""] * COLS
        self.target = self._pick_word()
        self.guessed_words = set()
        self.hard_letters = set()

        title = tk.Label(self, text="WORDLE", font=("Helvetica Neue", 26, "bold"),
                         bg=COLORS["bg"], fg="#22223b")
        title.pack(pady=(10, 2))

        self.status = tk.Label(
            self,
            text="Guess the 5-letter word. Press Enter to submit, Backspace to delete.",
            font=("Helvetica Neue", 12),
            bg=COLORS["bg"],
            fg="#1976d2",
            wraplength=420,
            justify="center"
        )
        self.status.pack(pady=(0, 8))

        self.board_frame = tk.Frame(self, bg=COLORS["board_bg"])
        self.board_frame.pack(padx=8, pady=(4, 4), fill="both", expand=True)

        self.tiles = []
        for r in range(ROWS):
            self.board_frame.grid_rowconfigure(r, weight=1)
            row_tiles = []
            for c in range(COLS):
                self.board_frame.grid_columnconfigure(c, weight=1)
                lbl = tk.Label(
                    self.board_frame,
                    text="",
                    font=("Helvetica Neue", 18, "bold"),
                    width=2,
                    height=1,
                    bg=COLORS["tile_empty"],
                    fg=COLORS["tile_text"],
                    relief="ridge",
                    bd=3,
                    highlightbackground=COLORS["tile_border"],
                    highlightthickness=2
                )
                lbl.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
                row_tiles.append(lbl)
            self.tiles.append(row_tiles)

        self.keyboard_frame = tk.Frame(self, bg=COLORS["bg"])
        self.keyboard_frame.pack(pady=(2, 6), fill="x", expand=False)

        self.key_buttons = {}
        kb_rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        for i, keys in enumerate(kb_rows):
            rowf = tk.Frame(self.keyboard_frame, bg=COLORS["bg"])
            rowf.pack(pady=1, fill="x")
            for ch in keys:
                self._add_key_button(rowf, ch)
            if i == 2:
                self._add_key_button(rowf, "ENTER")
                self._add_key_button(rowf, "⌫")

        controls = tk.Frame(self, bg=COLORS["bg"])
        controls.pack(pady=(0, 10))

        btn_style = {"font":("Helvetica Neue", 11, "bold"), "padx":10, "pady":6, "relief":"ridge"}
        self.new_btn = tk.Button(
            controls, text="New Game", command=self.new_game,
            bg=COLORS["green"], fg="white", **btn_style
        )
        self.new_btn.pack(side="left", padx=6)

        self.show_btn = tk.Button(
            controls, text="Show Answer", command=self.show_answer,
            bg=COLORS["yellow"], fg="#22223b", **btn_style
        )
        self.show_btn.pack(side="left", padx=6)

        self.menu_btn = tk.Button(
            controls, text="Main Menu", command=self.back_to_menu_callback,
            bg="#1976d2", fg="white", font=("Helvetica Neue", 11, "bold"),
            relief="ridge", padx=12, pady=6
        )
        self.menu_btn.pack(side="left", padx=6)

        self.wordlist_info = tk.Label(
            controls,
            text=("Using words_5.txt" if file_words else "Using built-in word list"),
            font=("Helvetica Neue", 9), bg=COLORS["bg"], fg="#9a9a9a"
        )
        self.wordlist_info.pack(side="left", padx=6)

        self.master.bind("<Key>", self.on_key_event)
        self.master.bind("<Escape>", lambda e: self.new_game())

        self._update_status("Guess the 5-letter word. You have 6 tries.")
        self._highlight_active_row()

    def _add_key_button(self, parent, text):
        btn = tk.Button(
            parent,
            text=text.upper(),
            font=("Helvetica Neue", 13, "bold"),
            bg=COLORS["key_bg"],
            fg=COLORS["key_fg"],
            relief="ridge",
            width=3,
            height=1,
            padx=2, pady=2,
            command=lambda t=text: self.on_virtual_key(t)
        )
        btn.pack(side="left", padx=2, pady=2, expand=True, fill="both")
        self.key_buttons[text.upper()] = btn

    def _update_status(self, msg):
        self.status.config(text=msg)

    def _highlight_active_row(self):
        for r in range(ROWS):
            for c in range(COLS):
                border = COLORS["tile_active"] if r == self.row and not self.game_over else COLORS["tile_border"]
                self.tiles[r][c].config(highlightbackground=border)

    def on_virtual_key(self, key):
        if self.game_over:
            return
        key = key.upper()
        if key == "ENTER":
            self.submit_guess()
        elif key == "⌫":
            self.backspace()
        elif len(key) == 1 and key in string.ascii_uppercase:
            self.type_letter(key)

    def on_key_event(self, event):
        if self.game_over:
            return
        key = event.keysym
        if key == "Return":
            self.submit_guess()
        elif key in ("BackSpace", "Delete"):
            self.backspace()
        elif len(event.char) == 1 and event.char.isalpha():
            self.type_letter(event.char.upper())
        self._highlight_active_row()

    def type_letter(self, ch):
        if self.col < COLS:
            self.current_letters[self.col] = ch
            self.tiles[self.row][self.col].config(text=ch)
            self.col += 1

    def backspace(self):
        if self.col > 0:
            self.col -= 1
            self.current_letters[self.col] = ""
            self.tiles[self.row][self.col].config(text="")

    def submit_guess(self):
        if self.col != COLS:
            self._update_status("Not enough letters.")
            self._shake_row(self.row)
            return
        guess = "".join(self.current_letters).lower()
        if guess not in self.allowed_words:
            self._update_status("Not in word list.")
            self._shake_row(self.row)
            return
        if guess in self.guessed_words:
            self._update_status("Already guessed.")
            self._shake_row(self.row)
            return

        # Hard mode enforcement
        if self.hard_mode_getter() and self.row > 0 and self.hard_letters:
            missing = [ch for ch in self.hard_letters if ch not in guess]
            if missing:
                self._update_status(f"Hard Mode: Must use {', '.join(missing).upper()}!")
                self._shake_row(self.row)
                return

        self.guessed_words.add(guess)
        marks = score_guess(guess, self.target)
        self._flip_row_animation(self.row, marks, guess)

        # Update hard_letters for next guess
        if self.hard_mode_getter():
            self.hard_letters = set()
            for i in range(COLS):
                if marks[i] in (1, 2):
                    self.hard_letters.add(guess[i])

        if guess == self.target:
            self.game_over = True
            self._update_status(f"Great! You guessed {self.target.upper()} ✅")
            self._highlight_active_row()
            self.update_stats(win=True)
            self.show_win_dialog()
            return

        self.row += 1
        self.col = 0
        self.current_letters = [""] * COLS
        self._highlight_active_row()

        if self.row == ROWS:
            self.game_over = True
            self._update_status(f"Out of tries. Answer: {self.target.upper()}")
            definition = get_definition(self.target)
            messagebox.showinfo("Game Over", f"Out of tries!\n\nAnswer: {self.target.upper()}\n\nMeaning: {definition}")
            self._highlight_active_row()
            self.update_stats(win=False)

    def _shake_row(self, row):
        # Flash border color for shake effect
        def flash(times):
            color = "#ff3333" if times % 2 == 0 else COLORS["tile_border"]
            for c in range(COLS):
                self.tiles[row][c].config(highlightbackground=color)
            if times < 5:
                self.after(60, lambda: flash(times + 1))
            else:
                for c in range(COLS):
                    self.tiles[row][c].config(highlightbackground=COLORS["tile_border"])
        flash(0)

    def _move_row(self, row, offset):
        pass  # No-op, not needed

    def _flip_row_animation(self, row, marks, guess):
        # Flip animation: reveal tiles one by one
        def flip_tile(c):
            lbl = self.tiles[row][c]
            lbl.config(bg=COLORS["tile_active"])
            lbl.after(100, lambda: self._animate_tile_color(row, c, self._get_tile_color(marks[c])))
            self._fade_keyboard_color(guess[c], marks[c])
        for c in range(COLS):
            self.board_frame.after(c * 120, lambda cc=c: flip_tile(cc))

    def _get_tile_color(self, mark):
        return COLORS["gray"] if mark == 0 else (COLORS["yellow"] if mark == 1 else COLORS["green"])

    def _animate_tile_color(self, r, c, color):
        lbl = self.tiles[r][c]
        lbl.config(bg=color, fg="white")

    def _fade_keyboard_color(self, ch, mark):
        # Fade-in effect for keyboard button color
        btn = self.key_buttons.get(ch.upper())
        if not btn:
            return
        target = self._get_tile_color(mark)
        steps = 8
        orig = btn.cget("bg")
        colors = [orig, COLORS["key_bg"], target]
        def fade(step):
            if step >= steps:
                btn.config(bg=target)
                return
            # Simple fade: interpolate between orig and target
            btn.config(bg=target if step > steps//2 else COLORS["key_bg"])
            btn.after(30, lambda: fade(step+1))
        fade(0)

    def _pick_word(self):
        if self.daily_mode_getter():
            return get_daily_word(self.answers)
        else:
            return random.choice(self.answers)

    def new_game(self):
        self.target = self._pick_word()
        self.row = 0
        self.col = 0
        self.game_over = False
        self.current_letters = [""] * COLS
        self.guessed_words.clear()
        self.hard_letters = set()
        self._update_status("New game! Guess the 5-letter word.")
        for r in range(ROWS):
            for c in range(COLS):
                self.tiles[r][c].config(text="", bg=COLORS["tile_empty"], fg=COLORS["tile_text"])
        for text, btn in self.key_buttons.items():
            btn.config(bg=COLORS["key_bg"], fg=COLORS["key_fg"])
        self._highlight_active_row()

    def show_answer(self):
        messagebox.showinfo("Answer", f"The answer is:\n\n{self.target.upper()}")

    def show_win_dialog(self):
        definition = get_definition(self.target)
        win_popup = tk.Toplevel(self)
        win_popup.title("Congratulations!")
        win_popup.configure(bg=COLORS["bg"])
        win_popup.grab_set()
        tk.Label(win_popup, text="You guessed the word!", font=("Helvetica", 16, "bold"),
                 bg=COLORS["bg"], fg=COLORS["green"]).pack(pady=(16, 8))
        tk.Label(win_popup, text=f"Answer: {self.target.upper()}", font=("Helvetica", 14),
                 bg=COLORS["bg"], fg="white").pack(pady=(0, 8))
        tk.Label(win_popup, text=f"Meaning: {definition}", font=("Helvetica", 12),
                 bg=COLORS["bg"], fg=COLORS["yellow"], wraplength=400, justify="left").pack(pady=(0, 16))
        tk.Button(win_popup, text="Next Level", font=("Helvetica", 12, "bold"),
                  bg=COLORS["green"], fg="white", relief="flat", padx=16, pady=8,
                  command=lambda: [win_popup.destroy(), self.new_game()]).pack(pady=6)
        tk.Button(win_popup, text="Main Menu", font=("Helvetica", 12),
                  bg=COLORS["gray"], fg="white", relief="flat", padx=16, pady=8,
                  command=lambda: [win_popup.destroy(), self.back_to_menu_callback()]).pack(pady=6)

    def update_stats(self, win):
        self.stats["games"] += 1
        if win:
            self.stats["wins"] += 1
            self.stats["streak"] += 1
            if self.stats["streak"] > self.stats["max_streak"]:
                self.stats["max_streak"] = self.stats["streak"]
        else:
            self.stats["streak"] = 0
        self.all_stats[self.player_name] = self.stats
        save_all_stats(self.all_stats)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wordle — Python Tkinter")
        self.configure(bg=COLORS["bg"])
        self.resizable(True, True)
        self.minsize(480, 700)  # Minimum size for usability

        self.player_name = self.ask_player_name()
        self.all_stats = load_all_stats()
        self.stats = get_player_stats(self.all_stats, self.player_name)
        self.daily_mode = False
        self.hard_mode = False
        self.menu = MainMenu(self, self.start_game, self.exit_app, self.show_stats, self.toggle_daily, self.daily_mode, self.toggle_hard, self.hard_mode, self.show_leaderboard, self.player_name)
        self.game = WordleApp(self, self.show_menu, self.stats, self.get_daily_mode, self.get_hard_mode, self.player_name, self.all_stats)
        self.menu.pack(fill="both", expand=True)
        self.game.pack_forget()

    def ask_player_name(self):
        name = simpledialog.askstring("Player Profile", "Enter your player name:", parent=self)
        if not name:
            name = "Player"
        return name.strip()

    def start_game(self):
        self.menu.pack_forget()
        self.game.pack(fill="both", expand=True)
        self.game.new_game()

    def show_menu(self):
        self.game.pack_forget()
        self.menu.pack(fill="both", expand=True)

    def exit_app(self):
        self.destroy()

    def show_stats(self):
        show_stats_popup(self, self.stats)

    def show_leaderboard(self):
        show_leaderboard_popup(self, self.all_stats)

    def toggle_daily(self, mode):
        self.daily_mode = mode

    def get_daily_mode(self):
        return self.daily_mode

    def toggle_hard(self, mode):
        self.hard_mode = mode

    def get_hard_mode(self):
        return self.hard_mode

if __name__ == "__main__":
    App().mainloop()
