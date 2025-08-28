import streamlit as st
import random
import os
import json
import hashlib
import datetime
from collections import Counter

ROWS = 6
COLS = 5
STATS_FILE = "stats.json"

def load_words_from_file(filename="words_5.txt"):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return [w.strip().lower() for w in f if len(w.strip()) == 5 and w.strip().isalpha()]

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
    import requests
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

def load_all_stats(filename=STATS_FILE):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}

def save_all_stats(stats, filename=STATS_FILE):
    with open(filename, "w") as f:
        json.dump(stats, f)

def get_hint(possible_words, prev_guesses, marks_list):
    # Filter possible words based on previous guesses and marks
    filtered = possible_words[:]
    for guess, marks in zip(prev_guesses, marks_list):
        new_filtered = []
        for word in filtered:
            if score_guess(guess, word) == marks:
                new_filtered.append(word)
        filtered = new_filtered
    if filtered:
        return random.choice(filtered)
    return None

def color_tile(letter, mark):
    color = "#bdbdbd" if mark == 0 else "#c9b458" if mark == 1 else "#6aaa64"
    emoji = "⬜" if mark == 0 else "🟨" if mark == 1 else "🟩"
    return f"<span style='background:{color};color:white;border-radius:6px;text-align:center;font-size:28px;padding:8px;margin:2px;display:inline-block;width:40px'>{letter.upper()} {emoji}</span>"

def avatar(name):
    # Simple emoji avatar based on first letter
    avatars = {
        "a": "🦁", "b": "🐻", "c": "🐱", "d": "🐶", "e": "🦊", "f": "🐸", "g": "🐼", "h": "🐨",
        "i": "🦄", "j": "🐧", "k": "🐔", "l": "🦉", "m": "🐵", "n": "🐙", "o": "🐢", "p": "🦖",
        "q": "🦕", "r": "🦓", "s": "🐍", "t": "🦖", "u": "🦕", "v": "🦒", "w": "🦘", "x": "🦔",
        "y": "🦚", "z": "🦜"
    }
    return avatars.get(name[0].lower(), "🙂")

# --- Streamlit UI ---
st.set_page_config(page_title="Wordle in Streamlit", layout="centered")

st.markdown(
    "<h1 style='text-align:center;color:#1976d2;'>Wordle — Streamlit Edition</h1>",
    unsafe_allow_html=True
)

with st.expander("ℹ️ How to Play", expanded=False):
    st.markdown("""
    - Guess the **5-letter word** in 6 tries.
    - Each guess must be a valid word.
    - After each guess, the color of the tiles will show how close your guess was:
        - 🟩 Green: Correct letter, correct place
        - 🟨 Yellow: Correct letter, wrong place
        - ⬜ Gray: Letter not in the word
    - **Hard Mode:** If a letter is revealed as 🟩 or 🟨, you must use it in your next guess.
    - Try the **Daily Challenge** for a global word!
    """)

player = st.text_input("Enter your player name:", value="Player").strip()
if not player:
    st.stop()

st.markdown(f"<h3 style='text-align:center;'>{avatar(player)} {player}</h3>", unsafe_allow_html=True)

words = load_words_from_file("words_5.txt")
if not words:
    st.warning("words_5.txt not found. Using fallback words.")
    words = [
        "about","other","which","their","there","apple","grape","mango","peach","berry",
        "lemon","melon","chair","table","plant","glass","stone","flame","cloud","dream",
        "crash","trace","place","spare","share","stare","crate","slate","brave","blink",
        "pride","drive","bring","sling","sugar","cider","orbit","vivid","cabin","knock",
        "rinse","smile","snack","track","video","zesty","quick","jazzy","fuzzy","piano"
    ]

all_stats = load_all_stats()
stats = all_stats.get(player, {"games": 0, "wins": 0, "streak": 0, "max_streak": 0})

mode = st.radio("Game Mode", ["Classic", "Daily"], horizontal=True)
hard_mode = st.checkbox("Hard Mode (must use revealed letters in next guess)")

if "target" not in st.session_state or st.session_state.get("player") != player or st.session_state.get("mode") != mode:
    st.session_state.target = random.choice(words) if mode == "Classic" else get_daily_word(words)
    st.session_state.guesses = []
    st.session_state.marks = []
    st.session_state.game_over = False
    st.session_state.hard_letters = set()
    st.session_state.player = player
    st.session_state.mode = mode

def new_game():
    st.session_state.target = random.choice(words) if mode == "Classic" else get_daily_word(words)
    st.session_state.guesses = []
    st.session_state.marks = []
    st.session_state.game_over = False
    st.session_state.hard_letters = set()
    st.session_state.player = player
    st.session_state.mode = mode

# Show previous guesses with emoji and color
if st.session_state.guesses:
    st.markdown("<h4>Guesses:</h4>", unsafe_allow_html=True)
    for guess, marks in zip(st.session_state.guesses, st.session_state.marks):
        tiles = "".join([color_tile(guess[i], marks[i]) for i in range(COLS)])
        st.markdown(tiles, unsafe_allow_html=True)

# Hint button
if st.session_state.guesses and not st.session_state.game_over:
    if st.button("💡 Hint"):
        hint = get_hint(words, st.session_state.guesses, st.session_state.marks)
        if hint:
            st.info(f"Try: **{hint.upper()}**")
        else:
            st.info("No hints available!")

if not st.session_state.game_over:
    with st.form("guess_form", clear_on_submit=True):
        guess_input = st.text_input("Enter your guess:", max_chars=5, key="guess_input").lower()
        submitted = st.form_submit_button("Submit Guess")
        if submitted:
            if len(guess_input) != 5 or not guess_input.isalpha():
                st.error("Please enter a valid 5-letter word.")
            elif guess_input not in words:
                st.error("Not in word list.")
            elif any(g == guess_input for g in st.session_state.guesses):
                st.error("Already guessed.")
            elif hard_mode and st.session_state.hard_letters and any(l not in guess_input for l in st.session_state.hard_letters):
                missing = [l.upper() for l in st.session_state.hard_letters if l not in guess_input]
                st.error(f"Hard Mode: Must use {', '.join(missing)}!")
            else:
                marks = score_guess(guess_input, st.session_state.target)
                st.session_state.guesses.append(guess_input)
                st.session_state.marks.append(marks)
                # Update hard letters for next guess
                if hard_mode:
                    st.session_state.hard_letters = set()
                    for i in range(COLS):
                        if marks[i] in (1, 2):
                            st.session_state.hard_letters.add(guess_input[i])
                if guess_input == st.session_state.target:
                    st.success(f"🎉 Great! You guessed {st.session_state.target.upper()} ✅")
                    st.session_state.game_over = True
                    stats["games"] += 1
                    stats["wins"] += 1
                    stats["streak"] += 1
                    stats["max_streak"] = max(stats["max_streak"], stats["streak"])
                    all_stats[player] = stats
                    save_all_stats(all_stats)
                    definition = get_definition(st.session_state.target)
                    st.info(f"**Meaning:** {definition}")
                elif len(st.session_state.guesses) == ROWS:
                    st.error(f"😢 Out of tries. Answer: {st.session_state.target.upper()}")
                    st.session_state.game_over = True
                    stats["games"] += 1
                    stats["streak"] = 0
                    all_stats[player] = stats
                    save_all_stats(all_stats)
                    definition = get_definition(st.session_state.target)
                    st.info(f"**Meaning:** {definition}")

if st.session_state.game_over:
    st.markdown("---")
    st.markdown(f"**Game Over!** {'🎉' if st.session_state.guesses and st.session_state.guesses[-1] == st.session_state.target else '😢'}")
    st.markdown(f"**Word:** `{st.session_state.target.upper()}`")
    st.markdown(f"**Guesses:** {len(st.session_state.guesses)}")
    st.markdown(f"**Your guesses:** {', '.join([g.upper() for g in st.session_state.guesses])}")
    if st.button("🔄 New Game"):
        new_game()

# Stats
with st.expander("📊 Your Stats", expanded=False):
    st.markdown(f"**Games Played:** `{stats['games']}`")
    st.markdown(f"**Wins:** `{stats['wins']}`")
    st.markdown(f"**Current Streak:** `{stats['streak']}`")
    st.markdown(f"**Max Streak:** `{stats['max_streak']}`")

# Leaderboard
with st.expander("🏆 Leaderboard", expanded=False):
    sorted_stats = sorted(all_stats.items(), key=lambda x: x[1].get("max_streak", 0), reverse=True)
    st.markdown("<h4>Top Streaks</h4>", unsafe_allow_html=True)
    for i, (pname, pstats) in enumerate(sorted_stats[:10], 1):
        rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else ""
        st.markdown(
            f"{rank_emoji} <b>{avatar(pname)} {pname}</b> — Max Streak: <b>{pstats.get('max_streak', 0)}</b> | Games: {pstats.get('games', 0)} | Wins: {pstats.get('wins', 0)}",
            unsafe_allow_html=True
        )