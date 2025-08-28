import streamlit as st
import random
import os
import json
import hashlib
import datetime
from collections import Counter

ROWS = 6
COLS = 5

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

# --- Streamlit UI ---
st.set_page_config(page_title="Wordle in Streamlit", layout="centered")

st.title("Wordle — Streamlit Edition")

# Load words
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

# Session state for game
if "target" not in st.session_state:
    st.session_state.target = random.choice(words)
    st.session_state.guesses = []
    st.session_state.game_over = False
    st.session_state.stats = {"games": 0, "wins": 0, "streak": 0, "max_streak": 0}

def new_game():
    st.session_state.target = random.choice(words)
    st.session_state.guesses = []
    st.session_state.game_over = False

def daily_game():
    st.session_state.target = get_daily_word(words)
    st.session_state.guesses = []
    st.session_state.game_over = False

# Game mode selection
mode = st.radio("Game Mode", ["Classic", "Daily"], horizontal=True)
if mode == "Daily":
    daily_game()

# Show previous guesses
for guess, marks in st.session_state.guesses:
    cols = st.columns(COLS)
    for i, col in enumerate(cols):
        color = "#bdbdbd" if marks[i] == 0 else "#c9b458" if marks[i] == 1 else "#6aaa64"
        col.markdown(f"<div style='background:{color};color:white;border-radius:6px;text-align:center;font-size:28px;padding:8px'>{guess[i].upper()}</div>", unsafe_allow_html=True)

if not st.session_state.game_over:
    guess_input = st.text_input("Enter your guess:", max_chars=5).lower()
    if st.button("Submit Guess"):
        if len(guess_input) != 5 or not guess_input.isalpha():
            st.error("Please enter a valid 5-letter word.")
        elif guess_input not in words:
            st.error("Not in word list.")
        elif any(g[0] == guess_input for g in st.session_state.guesses):
            st.error("Already guessed.")
        else:
            marks = score_guess(guess_input, st.session_state.target)
            st.session_state.guesses.append((guess_input, marks))
            if guess_input == st.session_state.target:
                st.success(f"Great! You guessed {st.session_state.target.upper()} ✅")
                st.session_state.game_over = True
                st.session_state.stats["games"] += 1
                st.session_state.stats["wins"] += 1
                st.session_state.stats["streak"] += 1
                st.session_state.stats["max_streak"] = max(st.session_state.stats["max_streak"], st.session_state.stats["streak"])
                definition = get_definition(st.session_state.target)
                st.info(f"Meaning: {definition}")
            elif len(st.session_state.guesses) == ROWS:
                st.error(f"Out of tries. Answer: {st.session_state.target.upper()}")
                st.session_state.game_over = True
                st.session_state.stats["games"] += 1
                st.session_state.stats["streak"] = 0
                definition = get_definition(st.session_state.target)
                st.info(f"Meaning: {definition}")

if st.session_state.game_over:
    if st.button("New Game"):
        new_game()

# Stats
with st.expander("📊 Your Stats"):
    stats = st.session_state.stats
    st.write(f"Games Played: **{stats['games']}**")
    st.write(f"Wins: **{stats['wins']}**")
    st.write(f"Current Streak: **{stats['streak']}**")
    st.write(f"Max Streak: **{stats['max_streak']}**")