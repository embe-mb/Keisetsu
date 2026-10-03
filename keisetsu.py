import tkinter as tk
from tkinter import filedialog, messagebox, font, colorchooser, ttk
import pandas as pd
import random
import math
import os
import sys
import json
import re
import subprocess
import colorsys
import time
import webbrowser

# PIL is required for high-quality thumbnail generation and glass-panel transparency compositing
try:
    from PIL import Image, ImageTk, ImageDraw
except ImportError:
    messagebox.showerror("Dependency Error", "Please install Pillow to run Keisetsu: pip install pillow")
    exit()

# ============================================================
# Persistent Settings Configuration
# ============================================================
SETTINGS_FILE = "keisetsu_settings.json"
BUILD_VERSION = "Build 1.11.1"
BUILD_DATE = "October 3, 2026"
# Keisetsu's folder, where settings, themes/, vocab_lists/ and the images
# live. In the Windows .exe (PyInstaller sets sys.frozen) __file__ points
# into a temporary unpack folder, so the folder holding the .exe is used.
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
# Passed to the .exe to open the CSV Manager instead of Keisetsu.
CSV_MANAGER_ARG = "--csv-manager"
HOME_URL = "embi.neocities.org"
HOME_LINK = "https://embi.neocities.org/"
# Optional window/taskbar icon: drop an "icon.png" next to keisetsu.py.
# If it is missing, logo.png is used instead.
ICON_FILES = ("icon.png", "logo.png")
# Seconds without a key press or click before the Study Mascot dozes off.
BUDDY_SLEEP_SECONDS = 30
# Combo Mode (a secret: unlocked by clicking the About window's logo
# COMBO_UNLOCK_CLICKS times). The "N HIT COMBO" counter appears from
# COMBO_SHOW_AT correct answers in a row; "C-C-C-COMBO BREAKER!!!" stays
# up for COMBO_BREAKER_MS after a miss.
COMBO_UNLOCK_CLICKS = 10
COMBO_SHOW_AT       = 3
COMBO_BREAKER_MS    = 3000
COMBO_RAINBOW_FROM  = 25    # starts fading into rainbow colors...
COMBO_RAINBOW_FULL  = 50    # ...fully rainbow (and glowing) from here
COMBO_SHAKE_FROM    = 75    # trembles, harder every 25 hits after this
COMBO_MILESTONES = {10: "NICE!", 25: "GREAT!", 50: "AWESOME!",
                    75: "INCREDIBLE!", 100: "UNSTOPPABLE!"}
# Line height (px) of 9 pt Arial at 100% display zoom. Subwindow sizes are
# designed for that zoom and scaled by how much bigger fonts really render.
BASE_UI_LINESPACE = 15
# Size of Tk's built-in "Import CSV" file picker at 100% zoom.
FILE_DIALOG_SIZE = (720, 480)
# Where the Study Mascot sits in the main panel: (vertical, horizontal).
# There's no "Bottom Center": the answer feedback fills that spot.
MASCOT_POSITIONS = {
    "Top Left":      ("top", "left"),
    "Top Center":    ("top", "center"),
    "Top Right":     ("top", "right"),
    "Bottom Left":   ("bottom", "left"),
    "Bottom Right":  ("bottom", "right"),
}
DEFAULT_MASCOT_POSITION = "Bottom Left"
VOCAB_MANAGER_SCRIPT = "vocab_manager.py"

# ============================================================
# Study Language & Font Defaults
# ============================================================
# Each language keeps its own font so switching between a Japanese and a
# Chinese deck doesn't mean retyping the font name every time. The
# defaults are the classic Mincho/Song serif faces Windows ships for each
# language (what Word, Notepad etc. fall back on for CJK text).
LANGUAGES = ("Japanese", "Chinese")
DEFAULT_FONTS = {
    "Japanese": "MS Mincho",
    "Chinese":  "SimSun",
}
# If the chosen font isn't installed (e.g. MS Mincho/SimSun on Linux or
# macOS), the first installed look-alike from these lists is used instead
# so the correct regional glyph forms are still shown.
FALLBACK_FONTS = {
    "Japanese": ["MS Mincho", "Yu Mincho", "Hiragino Mincho ProN", "Noto Serif CJK JP",
                 "IPAMincho", "TakaoMincho", "Meiryo", "Noto Sans CJK JP"],
    "Chinese":  ["SimSun", "NSimSun", "Songti SC", "STSong", "Noto Serif CJK SC",
                 "AR PL UMing CN", "Microsoft YaHei", "Noto Sans CJK SC"],
}
FONT_SAMPLE_TEXT = {
    "Japanese": "あいうえお 漢字",
    "Chinese":  "你好 汉字 漢字",
}

# ============================================================
# Romaji to Hiragana Conversion Engine
# ============================================================
ROMAJI_MAP = {
    'a': 'あ', 'i': 'い', 'u': 'う', 'e': 'え', 'o': 'お',
    'ka': 'か', 'ki': 'き', 'ku': 'く', 'ke': 'け', 'ko': 'こ',
    'sa': 'さ', 'shi': 'し', 'su': 'す', 'se': 'せ', 'so': 'そ',
    'ta': 'た', 'chi': 'ち', 'tsu': 'つ', 'te': 'て', 'to': 'と',
    'na': 'な', 'ni': 'に', 'nu': 'ぬ', 'ne': 'ね', 'no': 'の',
    'ha': 'は', 'hi': 'ひ', 'fu': 'ふ', 'he': 'へ', 'ho': 'ほ',
    'ma': 'ま', 'mi': 'み', 'mu': 'む', 'me': 'め', 'mo': 'も',
    'ya': 'や', 'yu': 'ゆ', 'yo': 'よ',
    'ra': 'ら', 'ri': 'り', 'ru': 'る', 're': 'れ', 'ro': 'ろ',
    'wa': 'わ', 'wo': 'を', 'nn': 'ん',
    'ga': 'が', 'gi': 'ぎ', 'gu': 'ぐ', 'ge': 'げ', 'go': 'ご',
    'za': 'ざ', 'ji': 'じ', 'zu': 'ず', 'ze': 'ぜ', 'zo': 'ぞ',
    'da': 'だ', 'di': 'ぢ', 'du': 'づ', 'de': 'で', 'do': 'ど',
    'ba': 'ば', 'bi': 'び', 'bu': 'ぶ', 'be': 'べ', 'bo': 'ぼ',
    'pa': 'ぱ', 'pi': 'ぴ', 'pu': 'ぷ', 'pe': 'ぺ', 'po': 'ぽ',
    'kya':'きゃ', 'kyu':'きゅ', 'kyo':'きょ',
    'sha':'しゃ', 'shu':'しゅ', 'sho':'しょ',
    'cha':'ちゃ', 'chu':'ちゅ', 'cho':'ちょ',
    'nya':'にゃ', 'nyu':'にゅ', 'nyo':'にょ',
    'hya':'ひゃ', 'hyu':'ひゅ', 'hyo':'ひょ',
    'mya':'みゃ', 'myu':'みゅ', 'myo':'みょ',
    'rya':'りゃ', 'ryu':'りゅ', 'ryo':'りょ',
    'gya':'ぎゃ', 'gyu':'ぎゅ', 'gyo':'ぎょ',
    'ja':'じゃ', 'ju':'じゅ', 'jo':'じょ',
    'bya':'びゃ', 'byu':'びゅ', 'byo':'びょ',
    'pya':'ぴゃ', 'pyu':'ぴゅ', 'pyo':'ぴょ',
    'vu': 'ゔ',
    # Small kana via the x/l prefix, e.g. "vuxo" -> ゔぉ, "fuxa" -> ふぁ
    'xa': 'ぁ', 'xi': 'ぃ', 'xu': 'ぅ', 'xe': 'ぇ', 'xo': 'ぉ',
    'la': 'ぁ', 'li': 'ぃ', 'lu': 'ぅ', 'le': 'ぇ', 'lo': 'ぉ',
    'xya':'ゃ', 'xyu':'ゅ', 'xyo':'ょ',
    'lya':'ゃ', 'lyu':'ゅ', 'lyo':'ょ',
    'xtsu':'っ', 'xtu':'っ', 'ltsu':'っ', 'ltu':'っ',
    'xwa':'ゎ', 'lwa':'ゎ', 'xka':'ゕ', 'lka':'ゕ', 'xke':'ゖ', 'lke':'ゖ',
    '-':'ー',
}

SORTED_ROMAJI = sorted(ROMAJI_MAP.items(), key=lambda x: len(x[0]), reverse=True)

def convert_to_hiragana(text):
    text = re.sub(r'([ksthmyrwgzdbp])\1', r'っ\1', text)
    for romaji, kana in SORTED_ROMAJI:
        text = text.replace(romaji, kana)
    return text

# ============================================================
# Numbered Pinyin to Tone Mark Conversion Engine
# ============================================================
# Typing a tone number straight after a syllable swaps it for the tone
# mark, e.g. "bu2shi4" -> "búshì", "lv4" -> "lǜ", "ma5" -> "ma" (5 = neutral).
# Only the longest valid pinyin syllable right before the digit is
# converted, so ordinary text like "lesson2" or "mp3" is left alone.
PINYIN_TONE_MARKS = {
    "a": "āáǎà", "e": "ēéěè", "i": "īíǐì", "o": "ōóǒò", "u": "ūúǔù", "ü": "ǖǘǚǜ",
    "A": "ĀÁǍÀ", "E": "ĒÉĚÈ", "I": "ĪÍǏÌ", "O": "ŌÓǑÒ", "U": "ŪÚǓÙ", "Ü": "ǕǗǙǛ",
}
_PINYIN_SYLLABLE = re.compile(
    r"(?:zh|ch|sh|[bpmfdtnlgkhjqxrzcsyw])?"
    r"(?:iang|iong|uang|ueng|ang|eng|ong|iao|ian|ing|uai|uan|üan|"
    r"ai|ei|ao|ou|an|en|er|ia|ie|iu|in|io|ua|uo|ui|un|ue|üe|ün|a|o|e|i|u|ü)r?",
    re.IGNORECASE,
)
_PINYIN_RUN = re.compile(r"([A-Za-züÜ:]+)([1-5])")


def _mark_pinyin_syllable(syl, tone):
    if tone == 5:
        return syl
    lower = syl.lower()
    if "a" in lower:
        pos = lower.index("a")
    elif "e" in lower:
        pos = lower.index("e")
    elif "ou" in lower:
        pos = lower.index("o")
    else:
        pos = max(lower.rfind(v) for v in "iouü")
    return syl[:pos] + PINYIN_TONE_MARKS[syl[pos]][tone - 1] + syl[pos + 1:]


def _convert_pinyin_run(match):
    run, tone = match.group(1), int(match.group(2))
    # "v" and "u:" are the usual keyboard stand-ins for ü.
    norm = run.replace("u:", "ü").replace("U:", "Ü").replace("v", "ü").replace("V", "Ü")
    for start in range(len(norm)):
        if _PINYIN_SYLLABLE.fullmatch(norm, start):
            return norm[:start] + _mark_pinyin_syllable(norm[start:], tone)
    return match.group(0)


def convert_to_pinyin(text):
    return _PINYIN_RUN.sub(_convert_pinyin_run, text)


def strip_pinyin_tones(text):
    """"búshì" -> "bushi" (ü is kept, since lü and lu are different words)."""
    for plain, marked in PINYIN_TONE_MARKS.items():
        for m in marked:
            text = text.replace(m, plain)
    return text

# ============================================================
# Animation Engine
# ============================================================
class AnimationEngine:
    EASING = {
        "linear":  lambda t: t,
        "ease_in": lambda t: t * t,
        "ease_out":lambda t: t * (2 - t),
        "ease_io": lambda t: t * t * (3 - 2 * t),
        "bounce":  lambda t: 1 - abs(math.cos(t * math.pi * 2.5)) * (1 - t) ** 2,
        "elastic": lambda t: (math.sin(13 * math.pi / 2 * t) * (2 ** (-10 * t)) + 1) if t > 0 else 0,
    }

    # Particle velocities are in pixels per STEP_MS, so motion looks the
    # same whatever the real frame rate is.
    STEP_MS = 50

    def __init__(self):
        self.tweens = []
        self.particles = []
        self.expired = []  # particles that died this tick (their canvas items need deleting)

    def tween(self, target, key, end, duration, easing="ease_io", on_done=None):
        self.tweens.append({
            "target": target, "key": key,
            "start": target[key], "end": end,
            "elapsed": 0, "duration": max(duration, 1),
            "easing": self.EASING.get(easing, self.EASING["linear"]),
            "on_done": on_done,
        })

    def tick(self, dt):
        alive = []
        for tw in self.tweens:
            tw["elapsed"] += dt
            t = min(tw["elapsed"] / tw["duration"], 1.0)
            tw["target"][tw["key"]] = tw["start"] + (tw["end"] - tw["start"]) * tw["easing"](t)
            if t < 1.0:
                alive.append(tw)
            elif tw["on_done"]:
                tw["on_done"]()
        self.tweens = alive

        k = dt / self.STEP_MS
        alive = []
        for p in self.particles:
            p["x"] += p["vx"] * k
            p["y"] += p["vy"] * k
            p["vy"] += p["gravity"] * k
            p["life"] -= dt
            (alive if p["life"] > 0 else self.expired).append(p)
        self.particles = alive

    def cancel(self, target):
        """Drops any running tweens on `target` without firing their
        on_done, so a new motion can take over cleanly."""
        self.tweens = [tw for tw in self.tweens if tw["target"] is not target]

    def burst(self, x, y, chars=None, n=30, spread=4.5, lifetime=1600,
              gravity=0.15, lift=1.5, tint=None, scale=1.0):
        if chars is None:
            chars = ["*", "#"]
        
        for _ in range(n):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, spread)
            self.emit(x, y, random.choice(chars),
                      math.cos(angle) * speed, math.sin(angle) * speed - lift,
                      random.randint(lifetime // 2, lifetime), lifetime,
                      gravity=gravity, tint=tint, scale=scale)

    def emit(self, x, y, char, vx, vy, life, max_life=None,
             gravity=0.15, tint=None, fixed_size=False, scale=1.0):
        """One particle. `tint` is a "#rrggbb" color that fades into the
        background as it dies (default: the usual blue-grey); `fixed_size`
        keeps text such as "Ouch!" readable instead of shrinking; `scale`
        multiplies its font size."""
        self.particles.append({
            "x": x, "y": y, "vx": vx, "vy": vy, "char": char,
            "life": life, "max_life": max_life or life,
            "gravity": gravity, "tint": tint, "fixed": fixed_size, "scale": scale,
            "item": None, "size": None,
        })

# ============================================================
# Study Mascot Frame Data (Japanese folklore, then Chinese mythology)
# ============================================================
ANIMALS = {
    "Shiba Inu": {
        "origin": "Japanese",
        "fps": 3,
        "states": {
            "idle": [
                "   ∧___∧   \n  (´·ω·`)  \n  ( ⊃ ⊂ )ɷ \n   ∪   ∪   ",
                "   ∧___∧   \n  (´·ω·`)  \n  ( ⊃ ⊂ )ɞ \n   ∪   ∪   ",
                "   ∧___∧   \n  (´-ω-`)  \n  ( ⊃ ⊂ )ɷ \n   ∪   ∪   ",
                "   ∧___∧   \n  (´·ω·`)  \n  ( ⊃ ⊂ )ɞ \n   ∪   ∪   ",
            ],
            "excited": [
                "   ∧___∧   \n \\(*≧ω≦*)/ \n  (     )ɷ \n   ∪   ∪   ",
                "   ∧___∧   \n  (*^ω^*)  \n  ( ⊃ ⊂ )ɞ \n   ∪   ∪   ",
                "   ∧___∧   \n \\(*≧ω≦*)/ \n  (     )ɷ \n   ∪   ∪   ",
                "   ∧___∧   \n  (*^ω^*)  \n  ( ⊃ ⊂ )ɞ \n   ∪   ∪   ",
            ],
            "sleeping": [
                "   ∧___∧ z \n  (´ᴗωᴗ`)  \n  ( ⊃ ⊂ )ɷ \n   ∪   ∪   ",
                "   ∧___∧ zZ\n  (´ᴗωᴗ`)  \n  ( ⊃ ⊂ )ɷ \n   ∪   ∪   ",
                "   ∧___∧  Z\n  (´ᴗωᴗ`)  \n  ( ⊃ ⊂ )ɷ \n   ∪   ∪   ",
                "   ∧___∧   \n  (´ᴗωᴗ`)  \n  ( ⊃ ⊂ )ɷ \n   ∪   ∪   ",
            ],
            "startled": [
                "  !∧___∧!  \n \\( ◎ω◎ )/ \n  (     )ɷ \n   ∪   ∪   ",
                "   ∧___∧ ! \n  (´°ω°`)  \n  ( ⊃ ⊂ )ɷ \n   ∪   ∪   ",
                "   ∧___∧   \n  (´·ω·`)  \n  ( ⊃ ⊂ )ɷ \n   ∪   ∪   ",
            ],
            "embarrassed": [
                "   ∧___∧ ! \n  (´>ω<`)  \n  ( ⊃ ⊂ )ɷ \n   ∪   ∪   ",
                "   ∧___∧⊂; \n  (´>ω<`)  \n  ( ⊃   )ɷ \n   ∪   ∪   ",
                "   ∧___∧⊂ ;\n  (´ˇωˇ`)  \n  ( ⊃   )ɷ \n   ∪   ∪   ",
                "   ∧___∧   \n  (´ˇωˇ`); \n  ( ⊃ ⊂ )ɷ \n   ∪   ∪   ",
            ],
            "angry": [
                "   ∧___∧ ╬ \n  (´ÒωÓ`)  \n  ( ⊃ ⊂ )ɷ \n   ∪   ∪   ",
                " ╬ ∧___∧   \n \\(`ÒДÓ´)/ \n  (     )ɷ \n  ∪     ∪  ",
                "   ∧___∧ ╬ \n  (´ÒωÓ`)  \n  ( ⊃ ⊂ )ɷ \n   ∪   ∪   ",
                " ╬ ∧___∧   \n \\(`ÒДÓ´)/ \n  (     )ɷ \n  ∪     ∪  ",
            ],
            "fuming": [
                "   ∧___∧ ╬ \n  (´ÒωÓ`)  \n  (  ╳  )ɷ \n   ∪   ∪   ",
                "   ∧___∧   \n  (´ÒωÓ`)  \n  (  ╳  )ɞ \n   ∪   ∪   ",
                "   ∧___∧ ╬ \n  (´ÒωÓ`)з \n  (  ╳  )ɷ \n   ∪   ∪   ",
                "   ∧___∧   \n  (´ÒωÓ`)з≡\n  (  ╳  )ɞ \n   ∪   ∪   ",
            ],
            "relieved": [
                "   ∧___∧   \n  (´ᴗωᴗ`)  \n  ( ⊃ ⊂ )ɷ \n   ∪   ∪   ",
                "   ∧___∧   \n  (´ᴗoᴗ`)з \n  ( ⊃ ⊂ )ɷ \n   ∪   ∪   ",
                "   ∧___∧   \n  (´-ω-`)з~\n  ( ⊃ ⊂ )ɞ \n   ∪   ∪   ",
                "   ∧___∧   \n  (´ᵔωᵔ`)  \n  ( ⊃ ⊂ )ɷ \n   ∪   ∪   ",
            ],
        },
        "idle_trigger": 150,
    },
    "Maneki-Neko": {
        "origin": "Japanese",
        "fps": 4,
        "states": {
            "idle": [
                "   ∧___∧ ∩ \n  (=ᵔωᵔ=)/ \n  ( ─◉─ )  \n  (_[¥]_)  ",
                "   ∧___∧   \n  (=ᵔωᵔ=)∩ \n  ( ─◉─ )  \n  (_[¥]_)  ",
                "   ∧___∧   \n  (=ᵔωᵔ=)⊃ \n  ( ─◉─ )  \n  (_[¥]_)  ",
                "   ∧___∧   \n  (=ᵔωᵔ=)∩ \n  ( ─◉─ )  \n  (_[¥]_)  ",
            ],
            "dancing": [
                " ♪ ∧___∧ ∩ \n  (=^ω^=)/ \n  ( ─◉─ )  \n  (_[¥]_) ♫",
                "   ∧___∧ ♪ \n  (=^ω^=)⊃ \n  ( ─◉─ )  \n ♫(_[¥]_)  ",
            ],
            "sleeping": [
                "   ∧___∧ z \n  (=ᴗωᴗ=)_ \n  ( ─◉─ )  \n  (_[¥]_)  ",
                "   ∧___∧ zZ\n  (=ᴗωᴗ=)_ \n  ( ─◉─ )  \n  (_[¥]_)  ",
                "   ∧___∧  Z\n  (=ᴗωᴗ=)_ \n  ( ─◉─ )  \n  (_[¥]_)  ",
                "   ∧___∧   \n  (=ᴗωᴗ=)_ \n  ( ─◉─ )  \n  (_[¥]_)  ",
            ],
            "startled": [
                "  !∧___∧!  \n \\(=◎ω◎=)/ \n  ( ─◉─ )  \n  (_[¥]_)  ",
                "   ∧___∧ ! \n  (=°ω°=)∩ \n  ( ─◉─ )  \n  (_[¥]_)  ",
                "   ∧___∧ ∩ \n  (=ᵔωᵔ=)/ \n  ( ─◉─ )  \n  (_[¥]_)  ",
            ],
            "embarrassed": [
                "   ∧___∧ ! \n  (=>ω<=)  \n  ( ─◉─ )  \n  (_[¥]_)  ",
                "   ∧___∧⊂; \n  (=>ω<=)  \n  ( ─◉─ )  \n  (_[¥]_)  ",
                "   ∧___∧⊂ ;\n  (=ˇωˇ=)  \n  ( ─◉─ )  \n  (_[¥]_)  ",
                "   ∧___∧   \n  (=ˇωˇ=)∩;\n  ( ─◉─ )  \n  (_[¥]_)  ",
            ],
            "angry": [
                "   ∧___∧ ╬ \n  (=ÒωÓ=)  \n  ( ─◉─ )  \n  (_[¥]_)  ",
                " ╬ ∧___∧ ∩ \n  (=ÒДÓ=)/ \n  ( ─◉─ )  \n  (_[¥]_)  ",
                "   ∧___∧ ╬ \n  (=ÒωÓ=)⊃ \n  ( ─◉─ )  \n  (_[¥]_)  ",
                " ╬ ∧___∧ ∩ \n  (=ÒДÓ=)/ \n  ( ─◉─ )  \n  (_[¥]_)  ",
            ],
            "fuming": [
                "   ∧___∧ ╬ \n  (=ÒωÓ=)  \n  (  ╳  )  \n  (_[¥]_)  ",
                "   ∧___∧   \n  (=ÒωÓ=)  \n  (  ╳  )  \n  (_[¥]_)  ",
                "   ∧___∧ ╬ \n  (=ÒωÓ=)з \n  (  ╳  )  \n  (_[¥]_)  ",
                "   ∧___∧   \n  (=ÒωÓ=)з≡\n  (  ╳  )  \n  (_[¥]_)  ",
            ],
            "relieved": [
                "   ∧___∧   \n  (=ᴗωᴗ=)_ \n  ( ─◉─ )  \n  (_[¥]_)  ",
                "   ∧___∧   \n  (=ᴗoᴗ=)з \n  ( ─◉─ )  \n  (_[¥]_)  ",
                "   ∧___∧   \n  (=-ω-=)з~\n  ( ─◉─ )  \n  (_[¥]_)  ",
                "   ∧___∧ ∩ \n  (=ᵔωᵔ=)/ \n  ( ─◉─ )  \n  (_[¥]_)  ",
            ],
        },
        "idle_trigger": 100,
    },
    "Daruma Doll": {
        "origin": "Japanese",
        "fps": 2,
        "states": {
            "idle": [
                "    ___    \n  ╱ ◉ ○ ╲  \n │ ╰≈‿≈╯ │ \n  ╲_____╱  ",
                "    ___    \n  ╱ ◉ ○ ╲  \n │ ╰≈‿≈╯ │ \n  ╲_____╱  ",
                "    ___    \n  ╱ ─ ─ ╲  \n │ ╰≈‿≈╯ │ \n  ╲_____╱  ",
                "    ___    \n  ╱ ◉ ○ ╲  \n │ ╰≈‿≈╯ │ \n  ╲_____╱  ",
            ],
            "wobble": [
                "     ___   \n   ╱ ◉ ○ ╲ \n  │ ╰≈‿≈╯ │\n  ╲_____╱  ",
                "    ___    \n  ╱ ◉ ○ ╲  \n │ ╰≈‿≈╯ │ \n  ╲_____╱  ",
                "   ___     \n ╱ ◉ ○ ╲   \n│ ╰≈‿≈╯ │  \n  ╲_____╱  ",
                "    ___    \n  ╱ ◉ ○ ╲  \n │ ╰≈‿≈╯ │ \n  ╲_____╱  ",
            ],
            "sleeping": [
                "    ___  z \n  ╱ ᴗ ᴗ ╲  \n │ ╰≈‿≈╯ │ \n  ╲_____╱  ",
                "    ___  zZ\n  ╱ ᴗ ᴗ ╲  \n │ ╰≈‿≈╯ │ \n  ╲_____╱  ",
                "    ___   Z\n  ╱ ᴗ ᴗ ╲  \n │ ╰≈‿≈╯ │ \n  ╲_____╱  ",
                "    ___    \n  ╱ ᴗ ᴗ ╲  \n │ ╰≈‿≈╯ │ \n  ╲_____╱  ",
            ],
            "startled": [
                "  ! ___ !  \n  ╱ ◎ ◎ ╲  \n │ ╰≈o≈╯ │ \n  ╲_____╱  ",
                "     ___ ! \n   ╱ ◉ ○ ╲ \n  │ ╰≈o≈╯ │\n  ╲_____╱  ",
                "    ___    \n  ╱ ◉ ○ ╲  \n │ ╰≈‿≈╯ │ \n  ╲_____╱  ",
            ],
            "embarrassed": [
                "    ___  ! \n  ╱ > < ╲  \n │ ╰≈o≈╯ │ \n  ╲_____╱  ",
                "     ___ ; \n   ╱ > < ╲ \n  │ ╰≈o≈╯ │\n  ╲_____╱  ",
                "    ___  ; \n  ╱ ˇ ˇ ╲  \n │ ╰≈‿≈╯ │ \n  ╲_____╱  ",
                "   ___     \n ╱ ˇ ˇ ╲;  \n│ ╰≈‿≈╯ │  \n  ╲_____╱  ",
            ],
            "angry": [
                "    ___ ╬  \n  ╱ Ò Ó ╲  \n │ ╰≈Д≈╯ │ \n  ╲_____╱  ",
                "  ╬  ___   \n   ╱ Ò Ó ╲ \n  │ ╰≈Д≈╯ │\n  ╲_____╱  ",
                "    ___ ╬  \n  ╱ Ò Ó ╲  \n │ ╰≈Д≈╯ │ \n  ╲_____╱  ",
                "   ___  ╬  \n ╱ Ò Ó ╲   \n│ ╰≈Д≈╯ │  \n  ╲_____╱  ",
            ],
            "fuming": [
                "    ___ ╬  \n  ╱ Ò Ó ╲  \n │ ╰≈^≈╯ │ \n  ╲_____╱  ",
                "    ___    \n  ╱ Ò Ó ╲  \n │ ╰≈^≈╯ │ \n  ╲_____╱  ",
                "    ___ ╬  \n  ╱ Ò Ó ╲з \n │ ╰≈^≈╯ │ \n  ╲_____╱  ",
                "    ___    \n  ╱ Ò Ó ╲з≡\n │ ╰≈^≈╯ │ \n  ╲_____╱  ",
            ],
            "relieved": [
                "    ___    \n  ╱ ᴗ ᴗ ╲  \n │ ╰≈‿≈╯ │ \n  ╲_____╱  ",
                "    ___    \n  ╱ ᴗ ᴗ ╲з \n │ ╰≈o≈╯ │ \n  ╲_____╱  ",
                "    ___    \n  ╱ - - ╲з~\n │ ╰≈‿≈╯ │ \n  ╲_____╱  ",
                "    ___    \n  ╱ ◉ ○ ╲  \n │ ╰≈‿≈╯ │ \n  ╲_____╱  ",
            ],
        },
        "idle_trigger": 200,
    },
    "Spirit Kitsune": {
        "origin": "Japanese",
        "fps": 3,
        "states": {
            "idle": [
                "  /\\___/\\  \n  (ˋ ‿ ˊ)  \n  ( ⊃ ⊂ )≋ \n   ∪   ∪ ≋≋",
                "  /\\___/\\  \n  (ˋ ‿ ˊ)  \n ∘( ⊃ ⊂ )∽ \n   ∪   ∪ ≋≋",
                "  /\\___/\\  \n  (ˉ ‿ ˉ)  \n  ( ⊃ ⊂ )≋ \n   ∪   ∪ ≋≋",
                "  /\\___/\\  \n  (ˋ ‿ ˊ)  \n  ( ⊃ ⊂ )∽ \n   ∪   ∪ ≋≋",
            ],
            "magic": [
                "∘ /\\___/\\  \n  (ˋ ▽ ˊ) °\n° ( ⊃ ⊂ )≋ \n   ∪   ∪ ≋≋",
                "° /\\___/\\ ∘\n  (ˋ ▽ ˊ)  \n  ( ⊃ ⊂ )≋∘\n  ∘∪   ∪ ≋≋",
                "  /\\___/\\ °\n∘ (ˋ ▽ ˊ)  \n  ( ⊃ ⊂ )≋ \n  °∪   ∪∘≋≋",
            ],
            "sleeping": [
                "  /\\___/\\  \n  (ᴗ ‿ ᴗ) z\n  ( ⊃ ⊂ )≋ \n   ∪   ∪ ≋≋",
                "  /\\___/\\ Z\n  (ᴗ ‿ ᴗ) z\n  ( ⊃ ⊂ )≋ \n   ∪   ∪ ≋≋",
                "  /\\___/\\ Z\n  (ᴗ ‿ ᴗ)  \n  ( ⊃ ⊂ )≋ \n   ∪   ∪ ≋≋",
                "  /\\___/\\  \n  (ᴗ ‿ ᴗ)  \n  ( ⊃ ⊂ )≋ \n   ∪   ∪ ≋≋",
            ],
            "startled": [
                "! /\\___/\\ !\n  (◎ o ◎)  \n  ( ⊃ ⊂ )≋≋\n   ∪   ∪≋≋≋",
                "  /\\___/\\ !\n  (° ‿ °)  \n  ( ⊃ ⊂ )≋ \n   ∪   ∪ ≋≋",
                "  /\\___/\\  \n  (ˋ ‿ ˊ)  \n  ( ⊃ ⊂ )≋ \n   ∪   ∪ ≋≋",
            ],
            "embarrassed": [
                "  /\\___/\\ !\n  (> _ <)  \n  ( ⊃ ⊂ )≋ \n   ∪   ∪ ≋≋",
                "  /\\___/\\ ;\n  (> _ <)  \n  ( ⊃ ⊂ )∽ \n   ∪   ∪ ≋≋",
                "  /\\___/\\ ;\n  (ˇ ‿ ˇ)≋≋\n  ( ⊃ ⊂ )≋ \n   ∪   ∪   ",
                "  /\\___/\\  \n  (ˇ ‿ ˇ); \n  ( ⊃ ⊂ )∽ \n   ∪   ∪ ≋≋",
            ],
            "angry": [
                "  /\\___/\\╬ \n  (Ò Д Ó)  \n °( ⊃ ⊂ )≋°\n   ∪   ∪ ≋≋",
                "╬ /\\___/\\ ∘\n \\(Ò Д Ó)/ \n∘ (     )≋≋\n  ∪     ∪≋≋",
                "  /\\___/\\╬ \n  (Ò Д Ó)  \n °( ⊃ ⊂ )≋°\n   ∪   ∪ ≋≋",
                "╬ /\\___/\\ ∘\n \\(Ò Д Ó)/ \n∘ (     )≋≋\n  ∪     ∪≋≋",
            ],
            "fuming": [
                "  /\\___/\\╬ \n  (Ò _ Ó)  \n  (  ╳  )≋ \n   ∪   ∪ ≋≋",
                "  /\\___/\\  \n  (Ò _ Ó)  \n  (  ╳  )∽ \n   ∪   ∪ ≋≋",
                "  /\\___/\\╬ \n  (Ò _ Ó)з \n  (  ╳  )≋ \n   ∪   ∪ ≋≋",
                "  /\\___/\\  \n  (Ò _ Ó)з≡\n  (  ╳  )∽ \n   ∪   ∪ ≋≋",
            ],
            "relieved": [
                "  /\\___/\\  \n  (ᴗ ‿ ᴗ)  \n  ( ⊃ ⊂ )≋ \n   ∪   ∪ ≋≋",
                "  /\\___/\\  \n  (ᴗ o ᴗ)з \n  ( ⊃ ⊂ )≋ \n   ∪   ∪ ≋≋",
                "  /\\___/\\  \n  (- ‿ -)з~\n  ( ⊃ ⊂ )∽ \n   ∪   ∪ ≋≋",
                "  /\\___/\\  \n  (ˋ ‿ ˊ)  \n  ( ⊃ ⊂ )≋ \n   ∪   ∪ ≋≋",
            ],
        },
        "idle_trigger": 180,
    },
    "Tanuki": {
        "origin": "Japanese",
        "fps": 3,
        "states": {
            "idle": [
                "   ∩ ☘ ∩   \n  (◐ ω ◑)  \n  ( (◯) )ʃ \n   ∪   ∪   ",
                "   ∩ ☘ ∩   \n  (◐ ω ◑)  \n  ( (◯) )ʅ \n   ∪   ∪   ",
                "   ∩ ☘ ∩   \n  (◒ ω ◒)  \n  ( (◯) )ʃ \n   ∪   ∪   ",
                "   ∩ ☘ ∩   \n  (◐ ω ◑)  \n  ( (◯) )ʅ \n   ∪   ∪   ",
            ],
            "drumming": [
                " ♪ ∩ ☘ ∩   \n  (◐ ▽ ◑)  \n  ( ⊃◯⊂ )ʃ \n   ∪   ∪   ",
                "   ∩ ☘ ∩ ♫ \n  (◐ ▽ ◑)  \n ⊂( (◯) )⊃ \n   ∪   ∪   ",
                " ♫ ∩ ☘ ∩   \n  (◐ ▽ ◑)  \n  ( ⊃◯⊂ )ʅ \n   ∪   ∪   ",
                "   ∩ ☘ ∩ ♪ \n  (◐ ▽ ◑)  \n ⊂( (◯) )⊃ \n   ∪   ∪   ",
            ],
            "sleeping": [
                "   ∩ ☘ ∩ z \n  (◒ ω ◒)  \n  ( (◯) )ʃ \n   ∪   ∪   ",
                "   ∩ ☘ ∩ zZ\n  (◒ ω ◒)  \n  ( (◯) )ʃ \n   ∪   ∪   ",
                "   ∩ ☘ ∩  Z\n  (◒ ω ◒)  \n  ( (◯) )ʅ \n   ∪   ∪   ",
                "   ∩ ☘ ∩   \n  (◒ ω ◒)  \n  ( (◯) )ʅ \n   ∪   ∪   ",
            ],
            "startled": [
                "  !∩ ☘ ∩!  \n  (◉ o ◉)  \n \\( (◯) )/ \n   ∪   ∪   ",
                "   ∩ ☘ ∩ ! \n  (◉ _ ◉)  \n  ( (◯) )ʃ \n   ∪   ∪   ",
                "   ∩ ☘ ∩   \n  (◐ ω ◑)  \n  ( (◯) )ʃ \n   ∪   ∪   ",
            ],
            "embarrassed": [
                "   ∩ ☘ ∩ ! \n  (> ω <)  \n  ( (◯) )ʃ \n   ∪   ∪   ",
                "   ∩ ☘ ∩⊂; \n  (> ω <)  \n  ( (◯) )ʃ \n   ∪   ∪   ",
                "   ∩ ☘ ∩⊂ ;\n  (ˇ ω ˇ)  \n  ( (◯) )ʅ \n   ∪   ∪   ",
                "   ∩ ☘ ∩   \n  (ˇ ω ˇ); \n  ( ⊃◯⊂ )ʃ \n   ∪   ∪   ",
            ],
            "angry": [
                "   ∩ ☘ ∩ ╬ \n  (Ò ω Ó)  \n  ( ⊃◯⊂ )ʃ \n   ∪   ∪   ",
                " ╬ ∩ ☘ ∩   \n  (Ò Д Ó)  \n ⊂( (◯) )⊃ \n  ∪     ∪  ",
                "   ∩ ☘ ∩ ╬ \n  (Ò ω Ó)  \n  ( ⊃◯⊂ )ʅ \n   ∪   ∪   ",
                " ╬ ∩ ☘ ∩   \n  (Ò Д Ó)  \n ⊂( (◯) )⊃ \n  ∪     ∪  ",
            ],
            "fuming": [
                "   ∩ ☘ ∩ ╬ \n  (Ò ω Ó)  \n  (  ╳  )ʃ \n   ∪   ∪   ",
                "   ∩ ☘ ∩   \n  (Ò ω Ó)  \n  (  ╳  )ʅ \n   ∪   ∪   ",
                "   ∩ ☘ ∩ ╬ \n  (Ò ω Ó)з \n  (  ╳  )ʃ \n   ∪   ∪   ",
                "   ∩ ☘ ∩   \n  (Ò ω Ó)з≡\n  (  ╳  )ʅ \n   ∪   ∪   ",
            ],
            "relieved": [
                "   ∩ ☘ ∩   \n  (◒ ω ◒)  \n  ( ⊃◯⊂ )ʃ \n   ∪   ∪   ",
                "   ∩ ☘ ∩   \n  (◒ o ◒)з \n  ( ⊃◯⊂ )ʃ \n   ∪   ∪   ",
                "   ∩ ☘ ∩   \n  (- ω -)з~\n  ( (◯) )ʅ \n   ∪   ∪   ",
                "   ∩ ☘ ∩   \n  (◐ ω ◑)  \n  ( (◯) )ʃ \n   ∪   ∪   ",
            ],
        },
        "idle_trigger": 160,
    },
    "Sun Wukong": {
        "origin": "Chinese",
        "fps": 4,
        "states": {
            "idle": [
                "   ╭═◉═╮ ┃ \n  @(ᵔ∀ᵔ)@┃ \n  ʃ( ⊃ ⊂)┃ \n    ∪  ∪ ┃ ",
                "   ╭═◉═╮ ┃ \n  @(ᵔ∀ᵔ)@┃ \n  ʅ( ⊃ ⊂)┃ \n    ∪  ∪ ┃ ",
                "   ╭═◉═╮ ┃ \n  @(-∀-)@┃ \n  ʃ( ⊃ ⊂)┃ \n    ∪  ∪ ┃ ",
                "   ╭═◉═╮ ┃ \n  @(ˋ∀ˊ)@┃ \n  ʅ( ⊃ ⊂)┃ \n    ∪  ∪ ┃ ",
            ],
            "somersault": [
                "   ╭═◉═╮ ┃ \n  @(ˋ▽ˊ)@┃ \n  ʃ( ⊃ ⊂)┃ \n ≈☁☁☁☁☁≈   ",
                " ━━╋═◉═╋━━ \n \\@(ˋ▽ˊ)@/ \n  ʃ(    )  \n  ≈☁☁☁☁☁≈  ",
                "   ╭═◉═╮ ┃ \n  @(ˋ▽ˊ)@┃ \n  ʅ( ⊃ ⊂)┃ \n   ≈☁☁☁☁☁≈ ",
                " ━━╋═◉═╋━━ \n \\@(ˋ▽ˊ)@/ \n  ʅ(    )  \n  ≈☁☁☁☁☁≈  ",
            ],
            "sleeping": [
                "   ╭═◉═╮ z╱\n  @(ᴗ‿ᴗ)@╱ \n  ʃ( ⊃ ⊂)  \n    ∪  ∪   ",
                "   ╭═◉═╮zZ╱\n  @(ᴗ‿ᴗ)@╱ \n  ʃ( ⊃ ⊂)  \n    ∪  ∪   ",
                "   ╭═◉═╮ Z╱\n  @(ᴗ‿ᴗ)@╱ \n  ʅ( ⊃ ⊂)  \n    ∪  ∪   ",
                "   ╭═◉═╮  ╱\n  @(ᴗ‿ᴗ)@╱ \n  ʅ( ⊃ ⊂)  \n    ∪  ∪   ",
            ],
            "startled": [
                "  !╭═◉═╮!┃ \n \\@(◎o◎)@┃ \n  ʃ(    )┃ \n    ∪  ∪ ┃ ",
                "   ╭═◉═╮ ┃!\n  @(°∀°)@┃ \n  ʃ( ⊃ ⊂)┃ \n    ∪  ∪ ┃ ",
                "   ╭═◉═╮ ┃ \n  @(ᵔ∀ᵔ)@┃ \n  ʃ( ⊃ ⊂)┃ \n    ∪  ∪ ┃ ",
            ],
            "embarrassed": [
                "   ╭═◉═╮ ┃!\n  @(>_<)@┃ \n  ʃ( ⊃ ⊂)┃ \n    ∪  ∪ ┃ ",
                "   ╭═◉═╮⊃┃;\n  @(>_<)@┃ \n  ʃ( ⊃  )┃ \n    ∪  ∪ ┃ ",
                "   ╭═◉═╮⊃┃;\n  @(ˇ∀ˇ)@┃ \n  ʅ( ⊃  )┃ \n    ∪  ∪ ┃ ",
                "   ╭═◉═╮ ┃ \n  @(ˇ∀ˇ)@┃;\n  ʃ( ⊃ ⊂)┃ \n    ∪  ∪ ┃ ",
            ],
            "angry": [
                "   ╭═◉═╮ ┃╬\n  @(ÒДÓ)@┃ \n  ʃ( ⊃ ⊂)┃ \n    ∪  ∪ ┃ ",
                " ╬ ╭═◉═╮ ┃ \n \\@(ÒДÓ)@┃ \n  ʃ(  ⊂)━┻━\n   ∪    ∪  ",
                "   ╭═◉═╮ ┃╬\n  @(ÒДÓ)@┃ \n  ʃ( ⊃ ⊂)┃ \n    ∪  ∪ ┃ ",
                " ╬ ╭═◉═╮ ┃ \n \\@(ÒДÓ)@┃ \n  ʃ(  ⊂)━┻━\n   ∪    ∪  ",
            ],
            "fuming": [
                "   ╭═◉═╮ ┃╬\n  @(Ò_Ó)@┃ \n  ʃ(  ╳ )┃ \n    ∪  ∪ ┃ ",
                "   ╭═◉═╮ ┃ \n  @(Ò_Ó)@┃ \n  ʃ(  ╳ )┃ \n    ∪  ∪ ┃ ",
                "   ╭═◉═╮ ┃╬\n  @(Ò_Ó)@з \n  ʅ(  ╳ )┃ \n    ∪  ∪ ┃ ",
                "   ╭═◉═╮ ┃ \n  @(Ò_Ó)@з≡\n  ʅ(  ╳ )┃ \n    ∪  ∪ ┃ ",
            ],
            "relieved": [
                "   ╭═◉═╮ ┃ \n  @(ᴗ∀ᴗ)@┃ \n  ʃ( ⊃ ⊂)┃ \n    ∪  ∪ ┃ ",
                "   ╭═◉═╮ ┃ \n  @(ᴗoᴗ)@з \n  ʃ( ⊃ ⊂)┃ \n    ∪  ∪ ┃ ",
                "   ╭═◉═╮ ┃ \n  @(-‿-)@з~\n  ʅ( ⊃ ⊂)┃ \n    ∪  ∪ ┃ ",
                "   ╭═◉═╮ ┃ \n  @(ᵔ∀ᵔ)@┃ \n  ʅ( ⊃ ⊂)┃ \n    ∪  ∪ ┃ ",
            ],
        },
        "idle_trigger": 140,
    },
    "Zhu Bajie": {
        "origin": "Chinese",
        "fps": 3,
        "states": {
            "idle": [
                "  ∩ ___ ∩ Ш\n  (´(oo)`)│\n  ( ⊃◯⊂ ) │\n   ∪   ∪  │",
                "  ∩ ___ ∩ Ш\n  (´(oo)`)│\n  ( ⊃◯⊂ ) │\n   ∪   ∪  │",
                "  ∩ ___ ∩ Ш\n  (-(oo)-)│\n  ( ⊃◯⊂ ) │\n   ∪   ∪  │",
                "  ∩ ___ ∩ Ш\n  (´(OO)`)│\n  ( ⊃◯⊂ ) │\n   ∪   ∪  │",
            ],
            "feasting": [
                "  ∩ ___ ∩ ♪\n  (ˆ(oo)ˆ) \n  ( ⊃◓⊂ )  \n   ∪   ∪   ",
                "  ∩ ___ ∩  \n  (ˆ(oo)ˆ)◓\n  (  ◯ ⊃)  \n   ∪   ∪  ♫",
                "  ∩ ___ ∩ ♫\n  (ˆ(OO)ˆ)°\n  ( ⊃◯⊂ )  \n   ∪   ∪   ",
                "  ∩ ___ ∩  \n  (ˆ(oo)ˆ) \n  ( ⊃◯⊂ ) ♪\n   ∪   ∪   ",
            ],
            "sleeping": [
                "  ∩ ___ ∩ z\n  (ᴗ(oo)ᴗ) \n  ( ⊃◯⊂ )╲ \n   ∪   ∪  Ш",
                "  ∩ ___ ∩zZ\n  (ᴗ(oo)ᴗ) \n  ( ⊃◯⊂ )╲ \n   ∪   ∪  Ш",
                "  ∩ ___ ∩ Z\n  (ᴗ(OO)ᴗ) \n  ( ⊃◯⊂ )╲ \n   ∪   ∪  Ш",
                "  ∩ ___ ∩  \n  (ᴗ(oo)ᴗ) \n  ( ⊃◯⊂ )╲ \n   ∪   ∪  Ш",
            ],
            "startled": [
                " !∩ ___ ∩!Ш\n  (◎(OO)◎)│\n \\(  ◯  )/│\n   ∪   ∪  │",
                "  ∩ ___ ∩!Ш\n  (°(oo)°)│\n  ( ⊃◯⊂ ) │\n   ∪   ∪  │",
                "  ∩ ___ ∩ Ш\n  (´(oo)`)│\n  ( ⊃◯⊂ ) │\n   ∪   ∪  │",
            ],
            "embarrassed": [
                "  ∩ ___ ∩!Ш\n  (>(oo)<)│\n  ( ⊃◯⊂ ) │\n   ∪   ∪  │",
                "  ∩ ___ ∩;Ш\n  (>(oo)<)│\n  ( ⊃◯⊂ ) │\n   ∪   ∪  │",
                "  ∩ ___ ∩;Ш\n  (ˇ(oo)ˇ)│\n  ( ⊃◯⊂ ) │\n   ∪   ∪  │",
                "  ∩ ___ ∩ Ш\n  (ˇ(oo)ˇ)│\n  ( ⊃◯⊂ );│\n   ∪   ∪  │",
            ],
            "angry": [
                "  ∩ ___ ∩╬Ш\n  (Ò(OO)Ó)│\n  ( ⊃◯⊂ ) │\n   ∪   ∪  │",
                " ╬∩ ___ ∩ Ш\n  (Ò(OO)Ó)┃\n  ( ⊃◯ ⊂)━┛\n  ∪     ∪  ",
                "  ∩ ___ ∩╬Ш\n  (Ò(OO)Ó)│\n  ( ⊃◯⊂ ) │\n   ∪   ∪  │",
                " ╬∩ ___ ∩ Ш\n  (Ò(OO)Ó)┃\n  ( ⊃◯ ⊂)━┛\n  ∪     ∪  ",
            ],
            "fuming": [
                "  ∩ ___ ∩╬Ш\n  (Ò(oo)Ó)│\n  (  ╳  ) │\n   ∪   ∪  │",
                "  ∩ ___ ∩ Ш\n  (Ò(oo)Ó)│\n  (  ╳  ) │\n   ∪   ∪  │",
                "  ∩ ___ ∩╬Ш\n  (Ò(OO)Ó)з\n  (  ╳  ) │\n   ∪   ∪  │",
                "  ∩ ___ ∩ Ш\n  (Ò(OO)Ó)≡\n  (  ╳  ) │\n   ∪   ∪  │",
            ],
            "relieved": [
                "  ∩ ___ ∩ Ш\n  (ᴗ(oo)ᴗ)│\n  ( ⊃◯⊂ ) │\n   ∪   ∪  │",
                "  ∩ ___ ∩ Ш\n  (ᴗ(OO)ᴗ)з\n  ( ⊃◯⊂ ) │\n   ∪   ∪  │",
                "  ∩ ___ ∩ Ш\n  (-(oo)-)~\n  ( ⊃◯⊂ ) │\n   ∪   ∪  │",
                "  ∩ ___ ∩ Ш\n  (ˆ(oo)ˆ)│\n  ( ⊃◯⊂ ) │\n   ∪   ∪  │",
            ],
        },
        "idle_trigger": 170,
    },
    "Jade Rabbit": {
        "origin": "Chinese",
        "fps": 3,
        "states": {
            "idle": [
                "   (\\ /)  ☾\n   (•x•)   \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
                "   (\\ /)  ☾\n   (•x•)   \n  ( ⊃ ⊂ )° \n   ∪   ∪   ",
                "   (\\ /)  ☾\n   (-x-)   \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
                "   (| /)  ☾\n   (•x•)   \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
            ],
            "pounding": [
                "   (\\ /) ┃☾\n   (ˆxˆ)┃  \n  ( ⊃ ⊃)┃∘ \n   ∪ ╰──╯  ",
                "   (\\ /)  ☾\n   (>x<)┃  \n  ( ⊃ ⊃)┃∘ \n   ∪ ╰┸─╯  ",
                "   (\\ /) ┃☾\n   (ˆxˆ)┃ ✧\n  ( ⊃ ⊃)┃∘ \n   ∪ ╰──╯  ",
                "   (\\ /)  ☾\n   (>x<)┃✧ \n  ( ⊃ ⊃)┃∘ \n   ∪ ╰┸─╯  ",
            ],
            "sleeping": [
                "   (\\ /)  ☾\n   (ᴗxᴗ) z \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
                "   (\\ /) Z☾\n   (ᴗxᴗ) z \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
                "   (\\ /) Z☾\n   (ᴗxᴗ)   \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
                "   (\\ /)  ☾\n   (ᴗxᴗ)   \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
            ],
            "startled": [
                "  !(| |)! ☾\n   (◎x◎)   \n \\(     )/ \n   ∪   ∪   ",
                "   (| |) !☾\n   (°x°)   \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
                "   (\\ /)  ☾\n   (•x•)   \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
            ],
            "embarrassed": [
                "   (\\ /) !☾\n   (>x<)   \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
                "   (\\ \\) ;☾\n   (>x<)   \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
                "   (\\ \\) ;☾\n  ⊂(ˇxˇ)   \n  (   ⊂ )∘ \n   ∪   ∪   ",
                "   (\\ /)  ☾\n   (ˇxˇ);  \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
            ],
            "angry": [
                "   (| |)╬ ☾\n   (ÒxÓ)   \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
                " ╬ (| |)  ☾\n \\ (ÒДÓ) / \n  (     )∘ \n  ∪     ∪  ",
                "   (| |)╬ ☾\n   (ÒxÓ)   \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
                " ╬ (| |)  ☾\n \\ (ÒДÓ) / \n  (     )∘ \n  ∪     ∪  ",
            ],
            "fuming": [
                "   (| |)╬ ☾\n   (ÒxÓ)   \n  (  ╳  )∘ \n   ∪   ∪   ",
                "   (| |)  ☾\n   (ÒxÓ)   \n  (  ╳  )∘ \n   ∪   ∪   ",
                "   (| |)╬ ☾\n   (ÒxÓ)з  \n  (  ╳  )∘ \n   ∪   ∪   ",
                "   (| |)  ☾\n   (ÒxÓ)з≡ \n  (  ╳  )∘ \n   ∪   ∪   ",
            ],
            "relieved": [
                "   (\\ /)  ☾\n   (ᴗxᴗ)   \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
                "   (\\ \\)  ☾\n   (ᴗoᴗ)з  \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
                "   (\\ \\)  ☾\n   (-x-)з~ \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
                "   (\\ /)  ☾\n   (ˆxˆ)   \n  ( ⊃ ⊂ )∘ \n   ∪   ∪   ",
            ],
        },
        "idle_trigger": 150,
    },
    "Nezha": {
        "origin": "Chinese",
        "fps": 4,
        "states": {
            "idle": [
                "  ◎___◎  ♦ \n  (ˋ‿ˊ)  │ \n ∽( ⊃ ⊂)━┿ \n  ⊛   ⊛  │ ",
                "  ◎___◎  ♦ \n  (ˋ‿ˊ)  │ \n ≈( ⊃ ⊂)━┿ \n  ✺   ✺  │ ",
                "  ◎___◎  ♦ \n  (-‿-)  │ \n ∽( ⊃ ⊂)━┿ \n  ⊛   ⊛  │ ",
                "  ◎___◎  ♦ \n  (ˋ‿ˊ)  │ \n ≈( ⊃ ⊂)━┿ \n  ✺   ✺  │ ",
            ],
            "wheels": [
                "  ◎___◎ ✧♦ \n  (ˋ▽ˊ)  │ \n∽≈( ⊃ ⊂)━┿ \n ϟ⊛ ϟ ⊛ϟ │ ",
                "  ◎___◎  ♦✧\n  (ˋ▽ˊ)  │ \n≈∽( ⊃ ⊂)━┿ \n ϟ✺ ϟ ✺ϟ │ ",
                " ✧◎___◎  ♦ \n  (ˋ▽ˊ)  │ \n∽≈( ⊃ ⊂)━┿ \n ϟ❂ ϟ ❂ϟ │ ",
                "  ◎___◎ ✧♦ \n  (ˋ▽ˊ)  │ \n≈∽( ⊃ ⊂)━┿ \n ϟ✺ ϟ ✺ϟ │ ",
            ],
            "sleeping": [
                "  ◎___◎ z ♦\n  (ᴗ‿ᴗ)  │ \n ∽( ⊃ ⊂) │ \n  ◯   ◯  │ ",
                "  ◎___◎ zZ♦\n  (ᴗ‿ᴗ)  │ \n ∽( ⊃ ⊂) │ \n  ◯   ◯  │ ",
                "  ◎___◎  Z♦\n  (ᴗ‿ᴗ)  │ \n ∽( ⊃ ⊂) │ \n  ◯   ◯  │ ",
                "  ◎___◎   ♦\n  (ᴗ‿ᴗ)  │ \n ∽( ⊃ ⊂) │ \n  ◯   ◯  │ ",
            ],
            "startled": [
                " !◎___◎! ♦ \n \\(◎o◎)/ │ \n ∽(    ) ┿ \n  ⊛   ⊛  │ ",
                "  ◎___◎ !♦ \n  (°‿°)  │ \n ∽( ⊃ ⊂)━┿ \n  ✺   ✺  │ ",
                "  ◎___◎  ♦ \n  (ˋ‿ˊ)  │ \n ∽( ⊃ ⊂)━┿ \n  ⊛   ⊛  │ ",
            ],
            "embarrassed": [
                "  ◎___◎ !♦ \n  (>_<)  │ \n ∽( ⊃ ⊂)━┿ \n  ⊛   ⊛  │ ",
                "  ◎___◎⊂;♦ \n  (>_<)  │ \n ∽( ⊃  ) ┿ \n  ◯   ◯  │ ",
                "  ◎___◎⊂;♦ \n  (ˇ‿ˇ)  │ \n ∽( ⊃  ) ┿ \n  ◯   ◯  │ ",
                "  ◎___◎  ♦ \n  (ˇ‿ˇ); │ \n ∽( ⊃ ⊂)━┿ \n  ⊛   ⊛  │ ",
            ],
            "angry": [
                "  ◎___◎╬ ♦ \n  (ÒДÓ)  │ \n ≈( ⊃ ⊂)━┿ \n ϟ⊛ ϟ ⊛ϟ │ ",
                "╬ ◎___◎ ✧♦ \n  (ÒДÓ) ╱  \n≈∽( ⊃ ⊂)╱  \n ϟ✺ ϟ ✺ϟ   ",
                "  ◎___◎╬ ♦ \n  (ÒДÓ)  │ \n ≈( ⊃ ⊂)━┿ \n ϟ❂ ϟ ❂ϟ │ ",
                "╬ ◎___◎ ✧♦ \n  (ÒДÓ) ╱  \n≈∽( ⊃ ⊂)╱  \n ϟ✺ ϟ ✺ϟ   ",
            ],
            "fuming": [
                "  ◎___◎╬ ♦ \n  (Ò_Ó)  │ \n ∽(  ╳ ) │ \n  ⊛ ϟ ⊛  │ ",
                "  ◎___◎  ♦ \n  (Ò_Ó)  │ \n ≈(  ╳ ) │ \n  ✺   ✺  │ ",
                "  ◎___◎╬ ♦ \n  (Ò_Ó)з │ \n ∽(  ╳ ) │ \n  ⊛ ϟ ⊛  │ ",
                "  ◎___◎  ♦ \n  (Ò_Ó)з≡│ \n ≈(  ╳ ) │ \n  ✺   ✺  │ ",
            ],
            "relieved": [
                "  ◎___◎  ♦ \n  (ᴗ‿ᴗ)  │ \n ∽( ⊃ ⊂)━┿ \n  ⊛   ⊛  │ ",
                "  ◎___◎  ♦ \n  (ᴗoᴗ)з │ \n ∽( ⊃ ⊂)━┿ \n  ◯   ◯  │ ",
                "  ◎___◎  ♦ \n  (-‿-)з~│ \n ∽( ⊃ ⊂)━┿ \n  ◯   ◯  │ ",
                "  ◎___◎  ♦ \n  (ˋ‿ˊ)  │ \n ∽( ⊃ ⊂)━┿ \n  ⊛   ⊛  │ ",
            ],
        },
        "idle_trigger": 130,
    },
    "Chinese Dragon": {
        "origin": "Chinese",
        "fps": 3,
        "states": {
            "idle": [
                "  Ψ ___ Ψ  \n ∽(ˋ ◇ ˊ)∽ \n  ( ⊃ ⊂ )◉ \n ≈≋∪≋≋≋∪≋∽ ",
                "  Ψ ___ Ψ  \n ~(ˋ ◇ ˊ)~ \n  ( ⊃ ⊂ )◉ \n ∽≋∪≋≋≋∪≋≈ ",
                "  Ψ ___ Ψ  \n ∽(- ◇ -)∽ \n  ( ⊃ ⊂ )◉ \n ≈≋∪≋≋≋∪≋∽ ",
                "  Ψ ___ Ψ  \n ~(ˋ ◇ ˊ)~ \n  ( ⊃ ⊂ )◉ \n ∽≋∪≋≋≋∪≋≈ ",
            ],
            "pearl": [
                "  Ψ ___ Ψ ✧\n ∽(ˋ ▽ ˊ)∽◉\n  ( ⊃ ⊂ )  \n ≈≋∪≋≋≋∪≋∽ ",
                " ✧Ψ ___ Ψ ◉\n ~(ˋ ▽ ˊ)~ \n  (   ⊂ )⊃ \n ∽≋∪≋≋≋∪≋≈✧",
                "◉ Ψ ___ Ψ  \n⊂∽(ˋ ▽ ˊ)∽ \n  ( ⊃   ) ✧\n ≈≋∪≋≋≋∪≋∽ ",
                "  Ψ ___ Ψ  \n ~(ˋ ▽ ˊ)~ \n ✧( ⊃ ⊂ )◉ \n ∽≋∪≋≋≋∪≋≈ ",
            ],
            "sleeping": [
                "  Ψ ___ Ψ z\n ∽(ᴗ ◇ ᴗ)∽ \n  ( ⊃ ⊂ )◉ \n ≈≋∪≋≋≋∪≋≈ ",
                "  Ψ ___ ΨzZ\n ∽(ᴗ ◇ ᴗ)∽ \n  ( ⊃ ⊂ )◉ \n ≈≋∪≋≋≋∪≋≈ ",
                "  Ψ ___ Ψ Z\n ~(ᴗ ◇ ᴗ)~ \n  ( ⊃ ⊂ )◉ \n ≈≋∪≋≋≋∪≋≈ ",
                "  Ψ ___ Ψ  \n ~(ᴗ ◇ ᴗ)~ \n  ( ⊃ ⊂ )◉ \n ≈≋∪≋≋≋∪≋≈ ",
            ],
            "startled": [
                " !Ψ ___ Ψ! \n∽\\(◎ o ◎)/∽\n  (     )◉ \n ≈≋∪≋≋≋∪≋∽ ",
                "  Ψ ___ Ψ !\n ∽(° ◇ °)∽ \n  ( ⊃ ⊂ )◉ \n ∽≋∪≋≋≋∪≋≈ ",
                "  Ψ ___ Ψ  \n ~(ˋ ◇ ˊ)~ \n  ( ⊃ ⊂ )◉ \n ≈≋∪≋≋≋∪≋∽ ",
            ],
            "embarrassed": [
                "  Ψ ___ Ψ !\n ∽(> ◇ <)∽ \n  ( ⊃ ⊂ )◉ \n ≈≋∪≋≋≋∪≋∽ ",
                "  Ψ ___ Ψ ;\n ~(> ◇ <)~ \n  ( ⊃ ⊂ )◉ \n ∽≋∪≋≋≋∪≋≈ ",
                "  Ψ ___ Ψ;⊂\n ~(ˇ ◇ ˇ)~ \n  ( ⊃   )◉ \n ≈≋∪≋≋≋∪≋∽ ",
                "  Ψ ___ Ψ  \n ∽(ˇ ◇ ˇ)∽;\n  ( ⊃ ⊂ )◉ \n ∽≋∪≋≋≋∪≋≈ ",
            ],
            "angry": [
                "  Ψ ___ Ψ╬ \n ∽(Ò Д Ó)∽ϟ\n  ( ⊃ ⊂ )◉ \n ≈≋∪≋≋≋∪≋∽ ",
                " ╬Ψ ___ Ψ  \nϟ∽(Ò Д Ó)∽≡\n  ( ⊃ ⊂ )◉ \n ∽≋∪≋≋≋∪≋≈ ",
                "  Ψ ___ Ψ╬ \n ∽(Ò Д Ó)∽ϟ\n  ( ⊃ ⊂ )◉ \n ≈≋∪≋≋≋∪≋∽ ",
                " ╬Ψ ___ Ψ  \nϟ∽(Ò Д Ó)∽≡\n  ( ⊃ ⊂ )◉ \n ∽≋∪≋≋≋∪≋≈ ",
            ],
            "fuming": [
                "  Ψ ___ Ψ╬ \n ∽(Ò _ Ó)∽ \n  (  ╳  )◉ \n ≈≋∪≋≋≋∪≋∽ ",
                "  Ψ ___ Ψ  \n ~(Ò _ Ó)~ \n  (  ╳  )◉ \n ∽≋∪≋≋≋∪≋≈ ",
                "  Ψ ___ Ψ╬ \n ∽(Ò _ Ó)з \n  (  ╳  )◉ \n ≈≋∪≋≋≋∪≋∽ ",
                "  Ψ ___ Ψ  \n ~(Ò _ Ó)з≡\n  (  ╳  )◉ \n ∽≋∪≋≋≋∪≋≈ ",
            ],
            "relieved": [
                "  Ψ ___ Ψ  \n ∽(ᴗ ◇ ᴗ)∽ \n  ( ⊃ ⊂ )◉ \n ≈≋∪≋≋≋∪≋∽ ",
                "  Ψ ___ Ψ  \n ∽(ᴗ o ᴗ)з \n  ( ⊃ ⊂ )◉ \n ∽≋∪≋≋≋∪≋≈ ",
                "  Ψ ___ Ψ  \n ~(- ◇ -)з~\n  ( ⊃ ⊂ )◉ \n ≈≋∪≋≋≋∪≋∽ ",
                "  Ψ ___ Ψ  \n ~(ˋ ◇ ˊ)~ \n  ( ⊃ ⊂ )◉ \n ∽≋∪≋≋≋∪≋≈ ",
            ],
        },
        "idle_trigger": 180,
    },
}

# Mascot states that are driven by user (in)activity rather than the
# random idle cycle or answer reactions - never picked as a "fun" alt state.
ACTIVITY_STATES = ("idle", "sleeping", "startled")

# Mascot states driven by how the user is answering. "embarrassed" plays on
# a wrong answer, "angry" when one card is missed ANGRY_STREAK times in a
# row, "fuming" loops while any card has been missed GRUDGE_MISSES or more
# times and isn't mastered yet, and "relieved" (a sigh) plays once the last
# of those cards is mastered. Every mascot has all four.
REACTION_STATES = ("embarrassed", "angry", "fuming", "relieved")
ANGRY_STREAK  = 3
GRUDGE_MISSES = 5

# States that loop until something moves the mascot on; any other state
# plays through once and then returns to the mascot's resting state.
LOOPING_STATES = ("idle", "sleeping", "fuming")
# Frame-rate multipliers for states that should play slower than the
# mascot's usual fps - a sigh of relief shouldn't be rushed.
STATE_SPEED = {"relieved": 0.5}


def fun_states(animal):
    """An animal's "fun" alternate states (e.g. Shiba's "excited")."""
    return [s for s in animal["states"]
            if s not in ACTIVITY_STATES and s not in REACTION_STATES]

# ============================================================
# Main App
# ============================================================
class KeisetsuApp:
    # The animation loop runs at ~60 fps while anything is moving
    # (particles, tweens, the Perfect Run celebration) and drops to 20 fps
    # when only the mascot's frame cycle is running, to save CPU.
    TICK_MS = 50
    FAST_TICK_MS = 16

    # Falls back to DejaVu Sans Mono on Linux (see the mascot glyph rules).
    BUDDY_FONT_FAMILY = "Consolas"

    # Floor for the auto-fitting question font, so an extremely long entry
    # shrinks only until it's still comfortably readable rather than
    # collapsing to nothing.
    MIN_Q_FONT_SIZE = 14

    BUTTON_IMAGES = {
        "import":      "btn_import.png",
        "csv_manager": "btn_csv_manager.png",
        "font":        "btn_font.png",
        "buddy":       "btn_buddy.png",
        "theme_toggle":"btn_theme_toggle.png",
        "themes":      "btn_themes.png",
        "bg_color":    "btn_bg_color.png",
        "fg_color":    "btn_fg_color.png",
        "auto_kana":   "btn_autokana.png",
        "help":        "btn_help.png",
        "about":       "btn_about.png",
        "submit":      "btn_submit.png",
    }
    
    UI_IMAGES = {
        "sidebar":     "bg_sidebar.png",
        "topbar":      "bg_topbar.png",
        "main":        "bg_main.png"
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Keisetsu - Diligent Studying")
        self.root.geometry("1460x810")
        self.root.minsize(1000, 680)

        self.set_window_icon()
        self.font_scale = self.compute_font_scale()
        # Tk's own file picker has a fixed 400x120 px file list, which is
        # tiny once fonts are scaled up, so it's enlarged each time it opens.
        self.root.bind_class("TkFDialog", "<Map>", self._enlarge_file_dialog, add="+")

        self.df = None
        self.current_csv_paths = []
        self.study_queue = []
        self.current_card_index = None
        self.last_practiced_index = None
        self.card_stats = {}
        self.perfect_run = True 
        self.current_question_text = ""

        # font_name always mirrors the font picked for the active study
        # language; language_fonts remembers each language's choice.
        self.study_language = "Japanese"
        self.language_fonts = dict(DEFAULT_FONTS)
        self.font_name = tk.StringVar(value=DEFAULT_FONTS["Japanese"])
        self.font_size = tk.IntVar(value=48)
        self._font_family_cache = {}
        self.auto_kana_enabled = True
        self.auto_pinyin_enabled = True
        self._is_converting = False 
        self.custom_bg_color = None
        self.custom_fg_color = None
        self.active_custom_theme = None 
        self.content_opacity = 1.0

        self.themes = {
            "Light": {
                "bg": "#FFFFFF", "fg": "#000000", "sidebar_bg": "#F5F6FA",
                "progress_bg": "#E0E0E0", "progress_fg": "#333333", "canvas_bg": "white",
                "success": "#00AA00", "error": "#CC0000", "comment": "#2266AA"
            },
            "Dark": {
                "bg": "#2B2B2B", "fg": "#EAEAEA", "sidebar_bg": "#1E1E1E",
                "progress_bg": "#3C3F41", "progress_fg": "#BBBBBB", "canvas_bg": "#555555",
                "success": "#4CAF50", "error": "#FF5252", "comment": "#64B5F6"
            },
        }
        self.current_theme = "Light"
        self.current_buddy = "Shiba Inu"
        self.mascot_position = DEFAULT_MASCOT_POSITION
        # Combo Mode is never saved: it lasts until the deck changes or
        # Keisetsu restarts.
        self.combo_mode = False

        self.load_settings()

        # Keyboard Bindings
        self.root.bind("<grave>", self.hotkey_toggle_auto_kana)
        # Any key press or click inside the main window counts as activity:
        # it keeps the Study Mascot awake (and startles it if it dozed off).
        self.root.bind("<KeyPress>", self.on_user_activity, add="+")
        self.root.bind("<ButtonPress>", self.on_user_activity, add="+")

        self.engine = AnimationEngine()
        self._buddy_state = "idle"
        self._buddy_frame_idx = 0
        self._buddy_ftimer = 0
        self._buddy_idle_ctr = 0
        self._last_tick = time.perf_counter()
        self._buddy_color = None
        self._buddy_transition = False
        self._buddy_asleep = False
        # Cards missed GRUDGE_MISSES+ times and not yet mastered. While any
        # are left, the mascot's resting state is "fuming" instead of "idle".
        self._grudge_cards = set()
        self._fume_timer = 0.0
        # Combo Mode runtime state (see the Combo Mode section).
        self.combo = 0
        self.combo_max = 0
        self._combo_hue = 0.0
        self._combo_jump = {"v": 0.0}
        self._combo_shown_n = None
        self._breaker_until = 0.0
        self._breaker_start = 0.0
        self._splash_start = None
        self._next_card_job = None
        self._combo_deck = None
        self._last_activity = time.monotonic()
        self._scale   = {"v": 1.0}
        self._alpha   = {"v": 1.0}
        self._offsetY = {"v": 0.0}
        self._offsetX = {"v": 0.0}

        # Baseline resolution: Keisetsu's own default window size. Scaling
        # is measured against THIS (not the 1920x1080 theme art) so the app
        # looks exactly as before at its normal default size, and only
        # grows/shrinks when the window is meaningfully bigger, smaller, or
        # a different shape (portrait monitors, 1366x768 laptops, etc).
        self.BASELINE_W, self.BASELINE_H = 1460, 810
        self.ui_scale = 1.0
        self.mascot_base_x = 0
        self.mascot_base_y = 0

        self.loaded_images = {}
        self.loaded_raw_images = {}
        self.loaded_ui_images = {}
        self.thumbnail_cache = {} 
        self.sidebar_buttons = []
        self.preload_assets()

        # ── Perfect Run Celebration State ──────────────────
        # Fires only when a whole session is cleared with zero wrong
        # answers (see next_card's "Done" branch / start_perfect_run_celebration).
        self._celebration_active = False
        self._celebration_after_id = None
        self._rainbow_phase = 0.0
        self._last_bar_frac = 0.0  # mastered fraction (0..1), redrawn at the canvas's live width
        self._dance_t = 0.0
        self._dance_widgets = []
        self._celebration_stars = []
        self._celebration_fireworks = []
        self._firework_timer = 0.0
        self._rainbow_key = None
        self._rainbow_img = None
        self._rainbow_img_id = None
        self._tick_dt = float(self.TICK_MS)
        self._rest_coords = {}

        self.setup_layout_panels()
        self.apply_theme()
        self.apply_font()

        self.engine.tween(self._alpha, "v", 0.0, 1,
                          on_done=lambda: (
                              self._buddy_set_frame(0),
                              self.engine.tween(self._alpha, "v", 1.0, 400, "ease_out"),
                          ))
        self._anim_loop()

    # ── Window / Taskbar Icon ─────────────────────────────
    def set_window_icon(self):
        """Uses icon.png (or logo.png as a fallback) from Keisetsu's folder as
        the window icon. iconphoto(True, ...) also makes it the default for
        every dialog, and handing over several sizes lets the taskbar/panel
        (e.g. Linux Mint's Cinnamon panel) pick a crisp one."""
        for name in ICON_FILES:
            path = os.path.join(APP_DIR, name)
            if not os.path.exists(path):
                continue
            try:
                src = Image.open(path).convert("RGBA")
                icons = []
                for size in (16, 32, 48, 64, 128, 256):
                    img = src.copy()
                    img.thumbnail((size, size), Image.Resampling.LANCZOS)
                    icons.append(ImageTk.PhotoImage(img))
                self._window_icons = icons  # keep references alive
                self.root.iconphoto(True, *icons)
                return
            except Exception:
                continue

    # ── Subwindow Sizing ──────────────────────────────────
    def compute_font_scale(self):
        """Measures the rendered UI font rather than trusting the reported
        DPI, which on Linux often disagrees with what fontconfig really draws
        (e.g. Mint at 125% renders at 192 DPI while Tk reports 120)."""
        linespace = font.Font(root=self.root, family="Arial", size=9).metrics("linespace")
        return max(1.0, min(4.0, linespace / BASE_UI_LINESPACE))

    def px(self, n):
        """A pixel size from the 100%-zoom design, scaled for this display."""
        return int(round(n * self.font_scale))

    def fit_window(self, top, width, height):
        """Sizes a subwindow to its 100%-zoom design size scaled for this
        display, but never smaller than its contents need (so buttons are
        never cut off) or bigger than 90% of the screen, then centers it
        over the main window. The content size also becomes the minimum.
        A design size of 0 means "just fit the contents"."""
        top.update_idletasks()
        max_w = int(top.winfo_screenwidth() * 0.9)
        max_h = int(top.winfo_screenheight() * 0.9)
        req_w, req_h = top.winfo_reqwidth(), top.winfo_reqheight()
        w = min(max(self.px(width), req_w), max_w)
        h = min(max(self.px(height), req_h), max_h)
        top.minsize(min(req_w, max_w), min(req_h, max_h))
        self._center_over_root(top, w, h)

    def _center_over_root(self, top, w, h):
        """`top` is a Toplevel or, for Tk's built-in dialogs (which Python
        didn't create), its Tcl path name."""
        path = str(top)
        call = self.root.tk.call
        sw, sh = call("winfo", "screenwidth", path), call("winfo", "screenheight", path)
        x = self.root.winfo_rootx() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - h) // 2
        x = max(0, min(x, sw - w))
        y = max(0, min(y, sh - h))
        call("wm", "geometry", path, f"{w}x{h}+{x}+{y}")

    def _enlarge_file_dialog(self, event):
        # event.widget is a plain path string here; <Map> also fires for
        # the dialog's child widgets, so only act on the dialog itself.
        path = str(event.widget)
        call = self.root.tk.call
        if call("winfo", "toplevel", path) != path:
            return
        cur_w, cur_h = call("winfo", "width", path), call("winfo", "height", path)
        w = max(self.px(FILE_DIALOG_SIZE[0]), cur_w)
        h = max(self.px(FILE_DIALOG_SIZE[1]), cur_h)
        if (w, h) != (cur_w, cur_h):
            self._center_over_root(path, w, h)

    # ── Hotkey Logic ──────────────────────────────────────
    def hotkey_toggle_auto_kana(self, event):
        self.toggle_auto_kana()
        return "break"

    # ── Asset Resolution Engine ───────────────────────────
    def get_asset_path(self, filename):
        if self.active_custom_theme:
            theme_path = os.path.join("themes", self.active_custom_theme, filename)
            if os.path.exists(theme_path):
                return theme_path
        if os.path.exists(filename):
            return filename
        return None

    def preload_assets(self):
        # Every themeable PNG is loaded through PIL and kept in its native
        # resolution (self.loaded_raw_images / "<key>_raw") so it can be
        # rescaled on demand to whatever size its container ends up being -
        # this is what lets buttons and background art adapt to any window
        # resolution or aspect ratio instead of staying pinned to one size.
        self.loaded_images = {}
        self.loaded_raw_images = {}
        for key, filename in self.BUTTON_IMAGES.items():
            path = self.get_asset_path(filename)
            if path:
                try:
                    pil_img = Image.open(path).convert("RGBA")
                    self.loaded_raw_images[key] = pil_img
                    self.loaded_images[key] = ImageTk.PhotoImage(pil_img)
                except Exception:
                    self.loaded_images[key] = None
                    self.loaded_raw_images[key] = None
            else:
                self.loaded_images[key] = None
                self.loaded_raw_images[key] = None

        self.loaded_ui_images = {}
        for key, filename in self.UI_IMAGES.items():
            path = self.get_asset_path(filename)
            if path:
                try:
                    pil_img = Image.open(path).convert("RGBA")
                    self.loaded_ui_images[key] = ImageTk.PhotoImage(pil_img)
                    self.loaded_ui_images[key + "_raw"] = pil_img
                except Exception:
                    self.loaded_ui_images[key] = None
                    self.loaded_ui_images[key + "_raw"] = None
            else:
                self.loaded_ui_images[key] = None
                self.loaded_ui_images[key + "_raw"] = None

    # ── Settings Save System ──────────────────────────────
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_theme = data.get("theme", self.current_theme)
                    self.current_buddy = data.get("buddy", self.current_buddy)
                    pos = data.get("mascot_position", self.mascot_position)
                    self.mascot_position = pos if pos in MASCOT_POSITIONS else DEFAULT_MASCOT_POSITION
                    lang = data.get("language", self.study_language)
                    self.study_language = lang if lang in LANGUAGES else "Japanese"
                    saved_fonts = data.get("font_names")
                    if isinstance(saved_fonts, dict):
                        for l in LANGUAGES:
                            if saved_fonts.get(l):
                                self.language_fonts[l] = saved_fonts[l]
                    elif data.get("font_name"):
                        # Settings from before Chinese support only had one
                        # font, which was always the Japanese one.
                        self.language_fonts["Japanese"] = data["font_name"]
                    self.font_name.set(self.language_fonts[self.study_language])
                    self.font_size.set(data.get("font_size", self.font_size.get()))
                    self.auto_kana_enabled = data.get("auto_kana", self.auto_kana_enabled)
                    self.auto_pinyin_enabled = data.get("auto_pinyin", self.auto_pinyin_enabled)
                    self.custom_bg_color = data.get("custom_bg", self.custom_bg_color)
                    self.custom_fg_color = data.get("custom_fg", self.custom_fg_color)
                    self.active_custom_theme = data.get("active_custom_theme", self.active_custom_theme)
                    self.content_opacity = data.get("content_opacity", 1.0)
            except Exception as e:
                print(f"Error reading configuration file: {e}")

    def save_settings(self):
        data = {
            "theme": self.current_theme,
            "buddy": self.current_buddy,
            "mascot_position": self.mascot_position,
            "language": self.study_language,
            "font_names": self.language_fonts,
            "font_size": self.font_size.get(),
            "auto_kana": self.auto_kana_enabled,
            "auto_pinyin": self.auto_pinyin_enabled,
            "custom_bg": self.custom_bg_color,
            "custom_fg": self.custom_fg_color,
            "active_custom_theme": self.active_custom_theme,
            "content_opacity": self.content_opacity
        }
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving Keisetsu settings: {e}")

    # ── Dynamic Input Handler ─────────────────────────────
    def auto_input_active(self):
        # The one sidebar toggle drives whichever converter fits the study
        # language: Romaji -> kana for Japanese, numbered -> toned pinyin
        # for Chinese. Each language remembers its own on/off state.
        if self.study_language == "Chinese":
            return self.auto_pinyin_enabled
        return self.auto_kana_enabled

    def toggle_auto_kana(self):
        if self.study_language == "Chinese":
            self.auto_pinyin_enabled = not self.auto_pinyin_enabled
        else:
            self.auto_kana_enabled = not self.auto_kana_enabled
        self.save_settings()
        self.update_autokana_button_text()

    def update_autokana_button_text(self):
        state = "ON" if self.auto_input_active() else "OFF"
        if self.study_language == "Chinese":
            self.btn_autokana.fallback_text = f"ā Auto-Pinyin: {state}"
        else:
            self.btn_autokana.fallback_text = f"あ Auto-Kana: {state}"
        
        glow_color = "#39FF14" if self.auto_input_active() else "#FF073A"
        self.autokana_glow_frame.config(bg=glow_color)

        if not self.loaded_images.get("auto_kana"):
            self.btn_autokana.config(text=self.btn_autokana.fallback_text)

    def on_answer_type(self, var_name, index, mode):
        if not self.auto_input_active() or self._is_converting:
            return

        raw = self.answer_var.get()
        if self.study_language == "Chinese":
            converted = convert_to_pinyin(raw)
        else:
            converted = convert_to_hiragana(raw)

        if converted != raw:
            cursor = self.answer_entry.index(tk.INSERT)
            diff = len(converted) - len(raw)
            
            self._is_converting = True
            self.answer_var.set(converted)
            self._is_converting = False
            
            self.answer_entry.icursor(cursor + diff)

    # ── Unified Canvas Framework & Layout ─────────────────
    def create_sleek_button(self, parent, img_key, fallback_text, command, scalable=False):
        btn = tk.Label(parent, bd=0, highlightthickness=0, cursor="hand2")
        btn.fallback_text = fallback_text 
        btn.img_key = img_key
        btn.bind("<Button-1>", lambda e: command())
        
        img = self.loaded_images.get(img_key)
        if img:
            btn.config(image=img)
            btn.image = img 
        else:
            btn.config(text=fallback_text, font=("Arial", 11, "bold"), padx=10, pady=8)
            btn.image = None

        # Scalable buttons live in the sidebar and get their PNG re-rendered
        # at the right size whenever the sidebar's width changes (see
        # rescale_sidebar_buttons), instead of staying a fixed pixel size.
        if scalable:
            self.sidebar_buttons.append(btn)
            
        return btn

    def setup_layout_panels(self):
        self.sidebar = tk.Frame(self.root, width=220, bd=0, highlightthickness=0)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.workspace = tk.Frame(self.root, bd=0, highlightthickness=0)
        self.workspace.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.sidebar_bg_lbl = tk.Label(self.sidebar, bd=0, highlightthickness=0)
        self.sidebar_bg_lbl.place(x=0, y=0, relwidth=1, relheight=1)
        self.sidebar.bind("<Configure>", self.on_sidebar_resize)
        
        # No fixed height: the label and bar inside decide it. A configured
        # height (it used to be 45) is re-requested every time the frame is
        # reconfigured (e.g. its bg on a theme toggle), so the bar would snap
        # to 45 px and back to its real ~58 px, re-laying out the whole
        # canvas twice and making everything bob.
        self.progress_frame = tk.Frame(self.workspace, bd=0, highlightthickness=0)
        self.progress_frame.pack(fill=tk.X, side=tk.TOP)
        self.topbar_bg_lbl = tk.Label(self.progress_frame, bd=0, highlightthickness=0)
        self.topbar_bg_lbl.place(x=0, y=0, relwidth=1, relheight=1)
        self.progress_frame.bind("<Configure>", self.on_topbar_resize)
        
        # Main Canvas replaces the standard frame logic to guarantee 100% genuine transparency.
        self.main_canvas = tk.Canvas(self.workspace, bd=0, highlightthickness=0)
        self.main_canvas.pack(fill=tk.BOTH, expand=True)
        self.main_canvas.bind("<Configure>", self.on_main_resize)

        # ── Settings Sidebar Panels ──
        self.btn_import = self.create_sleek_button(self.sidebar, "import", "📥 Import CSV", self.import_csv, scalable=True)
        self.btn_import.pack(fill=tk.X, padx=20, pady=(20, 6), side=tk.TOP)

        # Create CSV / CSV Editor have been superseded by the standalone
        # vocab_manager.py companion tool - this single button launches it.
        self.btn_csv_manager = self.create_sleek_button(self.sidebar, "csv_manager", "🗂️ CSV Manager", self.open_csv_manager, scalable=True)
        self.btn_csv_manager.pack(fill=tk.X, padx=20, pady=6, side=tk.TOP)

        div1 = tk.Frame(self.sidebar, height=2, bg="#555555")
        div1.pack(fill=tk.X, padx=20, pady=10, side=tk.TOP)

        self.btn_themes = self.create_sleek_button(self.sidebar, "themes", "🎨 Themes", self.open_theme_selector, scalable=True)
        self.btn_themes.pack(fill=tk.X, padx=20, pady=6, side=tk.TOP)

        self.btn_buddy = self.create_sleek_button(self.sidebar, "buddy", "🏮 Change Study Mascot", self.change_buddy, scalable=True)
        self.btn_buddy.pack(fill=tk.X, padx=20, pady=6, side=tk.TOP)

        self.btn_bg_col = self.create_sleek_button(self.sidebar, "bg_color", "🖌️ Custom BG Color", self.choose_bg_color, scalable=True)
        self.btn_bg_col.pack(fill=tk.X, padx=20, pady=6, side=tk.TOP)

        self.btn_fg_col = self.create_sleek_button(self.sidebar, "fg_color", "✏️ Custom Font Color", self.choose_fg_color, scalable=True)
        self.btn_fg_col.pack(fill=tk.X, padx=20, pady=6, side=tk.TOP)

        self.btn_font = self.create_sleek_button(self.sidebar, "font", "🔤 Customize Font", self.change_font, scalable=True)
        self.btn_font.pack(fill=tk.X, padx=20, pady=6, side=tk.TOP)

        div2 = tk.Frame(self.sidebar, height=2, bg="#555555")
        div2.pack(fill=tk.X, padx=20, pady=10, side=tk.TOP)

        self.btn_theme_tog = self.create_sleek_button(self.sidebar, "theme_toggle", "🌗 Toggle Bright/Dark", self.toggle_theme, scalable=True)
        self.btn_theme_tog.pack(fill=tk.X, padx=20, pady=6, side=tk.TOP)

        self.autokana_glow_frame = tk.Frame(self.sidebar, bd=2, relief=tk.SOLID)
        self.autokana_glow_frame.pack(fill=tk.X, padx=18, pady=4, side=tk.TOP)
        self.btn_autokana = self.create_sleek_button(self.autokana_glow_frame, "auto_kana", "あ Auto-Kana: ON", self.toggle_auto_kana, scalable=True)
        self.btn_autokana.pack(fill=tk.X, padx=2, pady=2)
        self.update_autokana_button_text()
        
        self.btn_about = self.create_sleek_button(self.sidebar, "about", "ℹ️ About Keisetsu", self.open_about_page, scalable=True)
        self.btn_about.pack(fill=tk.X, padx=20, pady=15, side=tk.BOTTOM)

        self.btn_help = self.create_sleek_button(self.sidebar, "help", "❓ Help Guide", self.open_help_page, scalable=True)
        self.btn_help.pack(fill=tk.X, padx=20, pady=0, side=tk.BOTTOM)

        # ── Workspace Dashboard System ──
        self.progress_label = tk.Label(self.progress_frame, text="Progress: 0/0 mastered (0%)", font=("Arial", 11, "bold"))
        self.progress_label.pack(side=tk.LEFT, padx=15, pady=10)

        # Stretches across the rest of the top bar and redraws on every
        # resize, so it tracks the window size / fullscreen / display scale.
        self.progress_canvas = tk.Canvas(self.progress_frame, height=14, width=1, highlightthickness=0)
        self.progress_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15, pady=10)
        self.progress_canvas.bind("<Configure>", lambda e: self.redraw_progress_bar())

        # Main Canvas Content Elements
        self.bg_img_id = self.main_canvas.create_image(0, 0, anchor=tk.NW)

        self.q_text_id = self.main_canvas.create_text(0, 0, text="Please import a CSV to start.", justify="center", width=800)

        self.answer_var = tk.StringVar()
        self.answer_var.trace_add("write", self.on_answer_type)

        # Unified Entry Box
        self.answer_entry = tk.Entry(self.main_canvas, textvariable=self.answer_var, width=25, justify="center")
        self.answer_entry.bind("<Return>", self.check_answer)
        # Bound here too (not just on root) because Tk checks a focused
        # widget's own bindings before its class's default "type this key"
        # behavior - this is what stops the ` from actually being typed
        # into the box while still toggling Auto-Kana.
        self.answer_entry.bind("<grave>", self.hotkey_toggle_auto_kana)
        self.entry_win_id = self.main_canvas.create_window(0, 0, window=self.answer_entry)

        # Anchored East so it dynamically pushes left of the Entry
        self.prompt_text_id = self.main_canvas.create_text(0, 0, text="Type Reading:", anchor=tk.E)
        
        self.submit_btn = self.create_sleek_button(self.main_canvas, "submit", "Submit", self.check_answer)
        self.submit_win_id = self.main_canvas.create_window(0, 0, window=self.submit_btn)

        # anchor="n" (top-center) means these are pinned by their TOP edge.
        # Multi-line results (e.g. "Wrong! (0%)\nAnswers: ...\n\nTip: ...")
        # then grow downward from a fixed point instead of expanding
        # upward from a center point into the entry box above them.
        self.feedback_text_id = self.main_canvas.create_text(0, 0, text="", justify="center", width=800, anchor=tk.N)
        self.comment_text_id = self.main_canvas.create_text(0, 0, text="", justify="center", width=800, anchor=tk.N)
        self.stats_text_id = self.main_canvas.create_text(0, 0, text="Cards remaining: 0", justify="center")

        # Combo Mode: the "N HIT COMBO" counter, its glow (copies of the
        # text drawn around it, since Tk text can't blur), the COMBO BREAKER
        # banner, and the big splash shown when the mode switches on.
        families = set(font.families(self.root))
        self._combo_family = next((f for f in ("Impact", "Arial Black", "DejaVu Sans", "Arial")
                                   if f in families), "Arial")
        self.combo_halo_ids = [self.main_canvas.create_text(0, 0, text="", state=tk.HIDDEN)
                               for _ in range(8)]
        self.combo_text_id = self.main_canvas.create_text(0, 0, text="", state=tk.HIDDEN)
        self.breaker_text_id = self.main_canvas.create_text(
            0, 0, text="C-C-C-COMBO BREAKER!!!", state=tk.HIDDEN, justify="center")
        self.splash_text_id = self.main_canvas.create_text(0, 0, text="", state=tk.HIDDEN, justify="center")
        # The combo text is drawn in a synthesized bold italic, whose slanted
        # glyphs stick out past the box Tk measures for the text. The canvas
        # only repaints that box when the text moves or hides, so on Windows
        # the overhang (e.g. the tips of "!!!") was left on screen for good.
        # This invisible rectangle is stretched over the combo text plus a
        # margin before every change (_repaint_combo_area); moving it makes
        # the canvas repaint that whole area, which clears the leftovers.
        self._combo_repaint_id = self.main_canvas.create_rectangle(0, 0, 0, 0, outline="", fill="")
        self.combo_base = (0, 0)

        # The Study Mascot's anchor and position come from
        # self.mascot_position and are set in on_main_resize.
        # A plain font tuple, not a named tkinter.font.Font: resizing a
        # named font makes Tk re-lay out every widget in the app, which
        # briefly resized the top bar and made the whole panel bob each
        # time the mascot's size changed (e.g. while switching mascots).
        self._buddy_font_size = 15
        first_frames = ANIMALS[self.current_buddy]["states"]["idle"]
        self.buddy_text_id = self.main_canvas.create_text(
            0, 0, text=first_frames[0], font=(self.BUDDY_FONT_FAMILY, 15),
            justify=tk.CENTER, anchor=tk.N
        )

    def on_main_resize(self, event=None):
        if event:
            self.main_width = event.width
            self.main_height = event.height
        else:
            self.main_width = self.main_canvas.winfo_width()
            self.main_height = self.main_canvas.winfo_height()

        w, h = self.main_width, self.main_height
        if w <= 1 or h <= 1: return

        # -- Resolution-aware global scale factor --
        # Compared against the sidebar/topbar too, so this tracks the
        # window's *actual* resolution rather than just the canvas, which
        # keeps fonts/buttons sized sensibly on anything from a 1366x768
        # laptop to a tall portrait monitor.
        sidebar_w_now = self.sidebar.winfo_width() or 220
        topbar_h_now  = self.progress_frame.winfo_height() or 45
        self.ui_scale = self.compute_ui_scale(w + sidebar_w_now, h + topbar_h_now)

        target_sidebar_w = max(170, min(300, int(220 * self.ui_scale)),
                               self._sidebar_text_width())
        target_sidebar_w = min(target_sidebar_w, int((w + sidebar_w_now) * 0.4))
        if abs(target_sidebar_w - sidebar_w_now) > 3:
            self.sidebar.config(width=target_sidebar_w)

        self.apply_scaled_fonts()

        # Dynamic Background Scaling & Glass Panel Composition
        bg_hex = self.get_current_color("bg")
        if self.loaded_ui_images.get("main_raw"):
            cropped = self._cover_fit(self.loaded_ui_images["main_raw"], w, h)

            panel_w, panel_h = int(w * 0.75), int(h * 0.8)
            px, py = (w - panel_w) // 2, (h - panel_h) // 2
            
            r, g, b = tuple(int(bg_hex[i:i+2], 16) for i in (1, 3, 5))
            alpha = int(255 * self.content_opacity)
            
            tint = Image.new("RGBA", (panel_w, panel_h), (r, g, b, alpha))
            panel_crop = cropped.crop((px, py, px + panel_w, py + panel_h))
            blended_panel = Image.alpha_composite(panel_crop, tint)
            
            cropped.paste(blended_panel, (px, py))
            
            self.bg_photo = ImageTk.PhotoImage(cropped)
            self.main_canvas.itemconfig(self.bg_img_id, image=self.bg_photo)
        else:
            self.main_canvas.itemconfig(self.bg_img_id, image="")
            self.main_canvas.config(bg=bg_hex)

        # -- Dynamic Coordinate Repositioning Math --
        # Vertical positions are proportional fractions of the panel's
        # actual height (rather than fixed pixel offsets from center) so
        # the whole layout - mascot, question, entry row, feedback - holds
        # together whether the window is short-and-wide or tall-and-narrow.
        cx = w // 2
        # The wrap width scales along WITH the font instead of being pinned
        # at a flat 900px. Previously a large or high-DPI window grew the
        # question font but left this cap alone, so the bigger the text got
        # the proportionally LESS room it had to wrap in - which is exactly
        # how a short sentence ended up broken into four oversized lines.
        wrap_w = max(280, min(int(900 * self.ui_scale), int(w * 0.72)))

        # The mascot sits in one of the window's corners or at the top
        # center (see MASCOT_POSITIONS). Corners hug the window edge to
        # leave the most room for the text.
        vert, horiz = MASCOT_POSITIONS[self.mascot_position]
        mascot_pad = max(12, int(16 * self.ui_scale))
        top_y      = max(24, int(h * 0.1) + mascot_pad)
        stats_y    = h - max(24, int(30 * self.ui_scale))
        inset_x    = mascot_pad if horiz != "center" else 0

        self.mascot_base_x = {"left": inset_x, "center": cx, "right": w - inset_x}[horiz]
        if vert == "top":
            self.mascot_base_y = mascot_pad if horiz != "center" else top_y
        else:
            self.mascot_base_y = h - mascot_pad
        anchor = ("n" if vert == "top" else "s") + {"left": "w", "center": "", "right": "e"}[horiz]
        self.main_canvas.itemconfig(self.buddy_text_id, anchor=anchor)
        # Size and place the mascot BEFORE measuring it. Its font is
        # normally updated by the animation loop, which runs after this -
        # measuring first would lay the text out around a stale mascot size.
        self._sync_buddy_font()
        self._position_buddy()
        mascot_bbox = self.main_canvas.bbox(self.buddy_text_id)
        if not mascot_bbox:
            mascot_bbox = (self.mascot_base_x, self.mascot_base_y,
                           self.mascot_base_x + int(160 * self.ui_scale),
                           self.mascot_base_y + int(110 * self.ui_scale))
        m_left, m_top, m_right, m_bottom = mascot_bbox

        # Dynamically query the physical size of the entry box based on the current font size
        entry_w = self.answer_entry.winfo_reqwidth()
        if entry_w < 10: entry_w = 350  # Fallback if system hasn't rendered it yet
        entry_h = self.answer_entry.winfo_reqheight()
        if entry_h < 10: entry_h = 44

        # A mascot on the left or right sits beside the text when the
        # panel is wide enough: the question and feedback wrap narrower to
        # stay out of its column. Otherwise it gets its own row, above
        # (top) or below (bottom) everything else.
        side_by_side = False
        if horiz != "center":
            narrowed = w - 2 * (inset_x + (m_right - m_left) + 16)
            if narrowed >= 360:
                side_by_side = True
                wrap_w = min(wrap_w, narrowed)

        question_y = max(top_y + 100, int(h * 0.34))
        if vert == "top" and not side_by_side:
            question_y = max(question_y, m_bottom + 60)
        entry_y = max(question_y + 70, int(h * 0.53))

        if vert == "bottom":
            # The entry row isn't narrowed, so check whether it would run
            # into a bottom mascot beside it.
            prompt_bbox = self.main_canvas.bbox(self.prompt_text_id)
            prompt_w    = (prompt_bbox[2] - prompt_bbox[0]) if prompt_bbox else 160
            submit_w    = self.submit_btn.winfo_reqwidth() or 120
            row_left    = cx - entry_w // 2 - 15 - prompt_w
            row_right   = cx + entry_w // 2 + 20 + submit_w
            row_clear   = m_right < row_left or m_left > row_right
            if not side_by_side or (not row_clear and entry_y + entry_h // 2 + 12 > m_top):
                # Lift the question and entry row so the feedback below
                # them has room before it reaches the mascot.
                question_y = max(top_y + 60, int(h * 0.26))
                entry_y    = max(question_y + 70, int(h * 0.44))
        # A bottom mascot in its own row keeps the comment/tip line above it.
        self._comment_floor = m_top - 20 if (vert == "bottom" and not side_by_side) else None

        self.main_canvas.coords(self.q_text_id, cx, question_y)

        # Work out the vertical slot the question is actually allowed to
        # fill - clear of a mascot above it and the entry row below it -
        # then shrink the font until the text genuinely fits inside it.
        band_top = m_bottom + 12 if (vert == "top" and not side_by_side) else top_y
        band_bottom   = entry_y - entry_h // 2 - 16
        # Anchored at its center, so the usable height is twice whichever
        # side has less clearance.
        half_band = max(30, min(question_y - band_top, band_bottom - question_y))
        self._q_wrap_w = wrap_w
        self._q_max_h  = int(half_band * 2)
        self.refit_question_text()

        # Center the entry exactly in the middle of the layout
        self.main_canvas.itemconfig(self.entry_win_id, anchor=tk.CENTER)
        self.main_canvas.coords(self.entry_win_id, cx, entry_y)
        
        # Anchor the Prompt text East (Right-aligned) and map it 15px to the left of the entry box
        self.main_canvas.itemconfig(self.prompt_text_id, anchor=tk.E)
        self.main_canvas.coords(self.prompt_text_id, cx - (entry_w // 2) - 15, entry_y)
        
        # Anchor the Submit Button West (Left-aligned) and map it just right of the entry box
        submit_gap = max(12, int(20 * self.ui_scale))
        self.main_canvas.itemconfig(self.submit_win_id, anchor=tk.W)
        self.main_canvas.coords(self.submit_win_id, cx + (entry_w // 2) + submit_gap, entry_y)
        self._rescale_submit_button()

        # Feedback is anchored at a fixed point a comfortable gap BELOW the
        # entry row's bottom edge; comment/tip is then placed below
        # feedback's actual rendered height (see reflow_feedback_area).
        # This is what stops a long multi-line "Wrong!" message from ever
        # sliding back up underneath the entry box.
        feedback_gap = max(26, int(entry_h * 0.6) + 16)
        self.feedback_base_y = entry_y + entry_h // 2 + feedback_gap
        self.main_canvas.itemconfig(self.feedback_text_id, width=wrap_w)
        self.main_canvas.itemconfig(self.comment_text_id, width=wrap_w)
        self.main_canvas.coords(self.feedback_text_id, cx, self.feedback_base_y)

        # stats_y was worked out alongside the mascot placement above.
        self.main_canvas.coords(self.stats_text_id, cx, stats_y)

        # Combo Mode's counter sits under the entry row, where the (hidden)
        # feedback text would be; the splash sits mid-panel.
        self.combo_base = (cx, self.feedback_base_y + max(30, int(40 * self.ui_scale)))
        self.main_canvas.coords(self.splash_text_id, cx, int(h * 0.42))
        self._apply_combo_visibility()

        self.reflow_feedback_area()
        self._position_buddy()
        self._snapshot_rest_coords()

    def _snapshot_rest_coords(self):
        """Snapshot of "at rest" coordinates for every dancing canvas item -
        the celebration dance oscillates around these rather than tracking
        a moving target, and stopping the celebration just means jumping
        back to whatever is here."""
        self._rest_coords = {
            "q":        self.main_canvas.coords(self.q_text_id),
            "prompt":   self.main_canvas.coords(self.prompt_text_id),
            "entry":    self.main_canvas.coords(self.entry_win_id),
            "submit":   self.main_canvas.coords(self.submit_win_id),
            "feedback": self.main_canvas.coords(self.feedback_text_id),
            "comment":  self.main_canvas.coords(self.comment_text_id),
            "stats":    self.main_canvas.coords(self.stats_text_id),
        }

    # ── Resolution / DPI Scaling Engine ────────────────────
    def compute_ui_scale(self, total_w, total_h):
        """Scale factor comparing the window's real footprint against
        Keisetsu's own default size (self.BASELINE_W/H). Using the smaller
        of the two axis ratios ("contain" rather than "cover") means the
        UI shrinks to fit a narrow portrait monitor's width instead of
        overflowing it, and grows only as far as the tighter dimension
        allows on a larger screen."""
        if total_w <= 0 or total_h <= 0:
            return 1.0
        scale = min(total_w / self.BASELINE_W, total_h / self.BASELINE_H)
        return max(0.55, min(1.5, scale))

    def _cover_fit(self, pil_img, target_w, target_h):
        """Resize + center-crop a PIL image so it exactly fills a
        target_w x target_h box, preserving aspect ratio (a 'cover' fit,
        the same technique CSS background-size:cover uses). This is what
        lets a single themeing PNG fill its panel cleanly at *any* window
        resolution or aspect ratio instead of leaving gaps or distorting."""
        if target_w <= 0 or target_h <= 0:
            return pil_img
        iw, ih = pil_img.size
        scale = max(target_w / iw, target_h / ih)
        new_w, new_h = max(1, int(iw * scale)), max(1, int(ih * scale))
        resized = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        return resized.crop((left, top, left + target_w, top + target_h))

    def refit_question_text(self):
        """Re-runs the question auto-fit using the geometry worked out by
        the most recent layout pass. Called whenever the question text
        changes, because a long vocab entry needs more shrinking than a
        short one does."""
        wrap_w = getattr(self, "_q_wrap_w", 0)
        if wrap_w:
            self._fit_question_text(wrap_w, getattr(self, "_q_max_h", 200))

    def _fit_question_text(self, wrap_w, max_h):
        """Shrinks the main question font until the text it currently holds
        actually FITS the space available to it.

        Tk font sizes given as positive numbers are in *points*, and Tk
        converts those to pixels using the display's DPI scaling. On a
        desktop running fractional scaling (e.g. Linux Mint at 125%) that
        conversion already enlarges the text - so multiplying by our own
        ui_scale on top of it double-counted the scaling, and the question
        ballooned well past its slot into several oversized lines that ran
        straight through the mascot and the entry box.

        Measuring the *rendered* result and stepping the size down until it
        fits sidesteps the whole problem: it doesn't matter whether the
        platform scales by points, by DPI, or not at all, because the
        check is against real on-screen geometry. Everything else in the
        UI is image-based and already scaled in pixels by us, which is why
        only this one element misbehaved."""
        f_name  = self.active_font_family()
        desired = int(getattr(self, "_q_desired_size", self.font_size.get()))
        size    = max(self.MIN_Q_FONT_SIZE, desired)

        for _ in range(40):
            self.main_canvas.itemconfig(self.q_text_id, font=(f_name, size), width=wrap_w)
            bbox = self.main_canvas.bbox(self.q_text_id)
            if not bbox:
                break
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            fits = text_h <= max_h and text_w <= wrap_w + 4
            if fits or size <= self.MIN_Q_FONT_SIZE:
                break
            size = max(self.MIN_Q_FONT_SIZE, int(size * 0.92))

        self._q_actual_size = size

    def apply_scaled_fonts(self):
        scale  = self.ui_scale
        f_name = self.active_font_family()
        # Starting point for the auto-fit; _fit_question_text may step this
        # down if the text doesn't fit the slot at this size.
        q_size = max(16, int(self.font_size.get() * scale))
        self._q_desired_size = q_size
        self.main_canvas.itemconfig(self.q_text_id, font=(f_name, q_size))
        self.main_canvas.itemconfig(self.prompt_text_id, font=(f_name, max(9, int(16 * scale))))
        self.main_canvas.itemconfig(self.feedback_text_id, font=(f_name, max(10, int(20 * scale))))
        self.main_canvas.itemconfig(self.comment_text_id, font=(f_name, max(9, int(16 * scale))))
        self.main_canvas.itemconfig(self.stats_text_id, font=(f_name, max(8, int(14 * scale))))
        self.answer_entry.config(font=(f_name, max(10, int(20 * scale))))

    def _rescale_submit_button(self):
        raw = self.loaded_raw_images.get("submit")
        if not raw:
            return
        iw, ih = raw.size
        if iw <= 0 or ih <= 0:
            return
        new_w = max(50, int(iw * self.ui_scale))
        new_h = max(18, int(ih * self.ui_scale))
        size_key = (new_w, new_h, self.submit_btn.cget("bg"))
        if getattr(self, "_submit_img_size", None) == size_key:
            return
        try:
            resized = raw.resize((new_w, new_h), Image.Resampling.LANCZOS)
            self.submit_photo = self._opaque_photo(resized, self.submit_btn)
            self.submit_btn.config(image=self.submit_photo)
            self.submit_btn.image = self.submit_photo
            self._submit_img_size = size_key
        except Exception:
            pass

    def reflow_feedback_area(self):
        """Places the comment/tip line just below wherever the feedback
        text's OWN rendered bounding box actually ends - so a short
        one-line result and a long four-line result both get a tip placed
        directly underneath them, with nothing overlapping."""
        base_y = getattr(self, "feedback_base_y", None)
        if base_y is None:
            return
        self.main_canvas.update_idletasks()
        bbox = self.main_canvas.bbox(self.feedback_text_id)
        bottom = bbox[3] if bbox else base_y
        comment_y = max(base_y + 20, bottom + 18)

        stats_coords = self.main_canvas.coords(self.stats_text_id)
        if stats_coords:
            comment_y = min(comment_y, stats_coords[1] - 30)
        floor = getattr(self, "_comment_floor", None)
        if floor is not None:
            comment_y = min(comment_y, floor)

        fb_coords = self.main_canvas.coords(self.feedback_text_id)
        cx = fb_coords[0] if fb_coords else self.main_width // 2
        self.main_canvas.coords(self.comment_text_id, cx, comment_y)

    def on_sidebar_resize(self, event):
        if event.width <= 1 or event.height <= 1:
            return
        self.refresh_sidebar_bg()
        self.rescale_sidebar_buttons(event.width)

    def on_topbar_resize(self, event):
        if event.width <= 1 or event.height <= 1:
            return
        self.refresh_topbar_bg()

    def _opaque_photo(self, pil_img, widget):
        """PhotoImage of pil_img flattened onto the widget's background
        colour. Tk labels are never see-through, so this looks identical,
        but Tk on X11 redraws any image with partial transparency by
        blending it pixel by pixel in software - which made every repaint
        of the themed sidebar (e.g. during the Perfect Run dance) slow."""
        if pil_img.mode == "RGBA":
            r, g, b = (v // 257 for v in widget.winfo_rgb(widget.cget("bg")))
            flat = Image.new("RGB", pil_img.size, (r, g, b))
            flat.paste(pil_img, mask=pil_img.getchannel("A"))
            pil_img = flat
        return ImageTk.PhotoImage(pil_img)

    def refresh_sidebar_bg(self):
        w, h = self.sidebar.winfo_width(), self.sidebar.winfo_height()
        raw = self.loaded_ui_images.get("sidebar_raw")
        if raw and w > 1 and h > 1:
            fitted = self._cover_fit(raw, w, h)
            self.sidebar_bg_photo = self._opaque_photo(fitted, self.sidebar_bg_lbl)
            self.sidebar_bg_lbl.config(image=self.sidebar_bg_photo)
        else:
            self.sidebar_bg_lbl.config(image="")

    def refresh_topbar_bg(self):
        w, h = self.progress_frame.winfo_width(), self.progress_frame.winfo_height()
        raw = self.loaded_ui_images.get("topbar_raw")
        if raw and w > 1 and h > 1:
            fitted = self._cover_fit(raw, w, h)
            self.topbar_bg_photo = self._opaque_photo(fitted, self.topbar_bg_lbl)
            self.topbar_bg_lbl.config(image=self.topbar_bg_photo)
        else:
            self.topbar_bg_lbl.config(image="")

    def _sidebar_text_width(self):
        """Sidebar width needed so no text (non-PNG) button's label is cut
        off. Their font is a fixed point size, which renders much wider
        under desktop display scaling than the 300 px cap above assumes.
        The 48 px covers the buttons' 20 px side margins plus the Auto-Kana
        glow border."""
        widths = [btn.winfo_reqwidth() for btn in self.sidebar_buttons
                  if not self.loaded_raw_images.get(getattr(btn, "img_key", None))]
        return max(widths, default=0) + 48

    def rescale_sidebar_buttons(self, sidebar_width):
        """Re-renders every sidebar button PNG at a width that fits the
        sidebar's current size (preserving aspect ratio), instead of
        leaving them at one fixed pixel size regardless of resolution."""
        target_w = max(60, sidebar_width - 40)
        for btn in self.sidebar_buttons:
            raw = self.loaded_raw_images.get(getattr(btn, "img_key", None))
            if not raw:
                continue
            iw, ih = raw.size
            if iw <= 0:
                continue
            scale = target_w / iw
            new_w, new_h = max(1, int(iw * scale)), max(1, int(ih * scale))
            # The PNG is flattened onto the button's bg colour, so a theme
            # colour change needs a re-render too, not just a resize.
            size_key = (new_w, new_h, btn.cget("bg"))
            if getattr(btn, "_scaled_size", None) == size_key:
                continue
            try:
                resized = raw.resize((new_w, new_h), Image.Resampling.LANCZOS)
                photo = self._opaque_photo(resized, btn)
                btn.scaled_image = photo  # keep a reference so Tk doesn't garbage-collect it
                btn.config(image=photo)
                btn.image = photo
                btn._scaled_size = size_key
            except Exception:
                pass

    def _sync_buddy_font(self):
        """Keeps the mascot's font in step with the resolution scale.
        Shared by the layout pass and the animation loop so both always
        agree on its size (and therefore its measured height)."""
        new_size = max(8, int(15 * getattr(self, "ui_scale", 1.0) * self._scale["v"]))
        if new_size != self._buddy_font_size:
            self._buddy_font_size = new_size
            self.main_canvas.itemconfig(self.buddy_text_id, font=(self.BUDDY_FONT_FAMILY, new_size))

    def _position_buddy(self):
        x = self.mascot_base_x + self._offsetX["v"]
        y = self.mascot_base_y - self._offsetY["v"]
        if self._celebration_active:
            x += 14 * math.sin(self._dance_t * 1.3 + 3.4)
            y += 14 * math.sin(self._dance_t * 0.9)
        try:
            self.main_canvas.coords(self.buddy_text_id, x, y)
        except Exception:
            pass

    # ── Mascot Visual Logic Engine System ─────────────────
    def _buddy_bbox(self):
        """The mascot's current on-canvas box, used to aim particle bursts
        at it wherever it is placed."""
        bbox = self.main_canvas.bbox(self.buddy_text_id)
        if not bbox:
            x, y = self.mascot_base_x, self.mascot_base_y
            return (x, y, x, y)
        return bbox

    def _buddy_def(self):
        return ANIMALS[self.current_buddy]

    def _buddy_frames(self, state=None):
        return self._buddy_def()["states"][state or self._buddy_state]

    def _buddy_set_frame(self, idx):
        self._buddy_frame_idx = idx % len(self._buddy_frames())
        self.main_canvas.itemconfig(self.buddy_text_id, text=self._buddy_frames()[self._buddy_frame_idx])

    def set_buddy(self, buddy_name):
        if buddy_name == self.current_buddy or self._buddy_transition:
            return
        self._buddy_transition = True

        def _do_switch():
            self.current_buddy     = buddy_name
            self._buddy_state      = self._buddy_rest_state()
            self._buddy_frame_idx  = 0
            self._buddy_idle_ctr   = 0
            self._buddy_asleep     = False
            self._last_activity    = time.monotonic()
            self._buddy_set_frame(0)
            self.save_settings()
            self.engine.tween(self._scale, "v", 1.0, 180, "ease_out")
            self.engine.tween(self._alpha, "v", 1.0, 180, "ease_out",
                              on_done=lambda: setattr(self, "_buddy_transition", False))

        self.engine.tween(self._alpha, "v", 0.0, 120, "ease_in", on_done=_do_switch)
        self.engine.tween(self._scale, "v", 0.75, 120, "ease_in")

    def _buddy_rest_state(self):
        return "fuming" if self._grudge_cards else "idle"

    def _buddy_play(self, state):
        self._buddy_state     = state
        self._buddy_ftimer    = 0
        self._buddy_idle_ctr  = 0
        self._buddy_set_frame(0)

    def _buddy_head(self):
        """Canvas point just above the top-right of the mascot's head."""
        x0, y0, x1, y1 = self._buddy_bbox()
        return x0 + (x1 - x0) * 0.7, y0 + 6

    def _buddy_move(self, target, steps):
        """Runs (value, ms, easing) tweens on `target` one after another,
        replacing whatever motion it was already doing."""
        self.engine.cancel(target)

        def run(i):
            if i < len(steps):
                end, ms, easing = steps[i]
                self.engine.tween(target, "v", end, ms, easing, on_done=lambda: run(i + 1))
        run(0)

    def _buddy_say(self, text, color):
        """A short word ("Ouch!", "Phew~") that floats up from the mascot."""
        x, y = self._buddy_head()
        # A mascot at the top of the window has no room above its head,
        # so the word starts beside it instead of off-screen.
        self.engine.emit(x, max(y - 6, 30), text, random.uniform(0.3, 0.8),
                         -1.6 if y > 60 else 0.6, 1300,
                         gravity=0.02, tint=color, fixed_size=True)

    def buddy_react_correct(self, question_text="", card=None, mastered=False):
        x0, y0, x1, y1 = self._buddy_bbox()
        active_kana = list(question_text.replace(" ", ""))
        particle_chars = ["*", "#", "+"] + active_kana

        if mastered and card in self._grudge_cards:
            self._grudge_cards.discard(card)
            if not self._grudge_cards:
                self.engine.burst((x0 + x1) / 2, (y0 + y1) / 2,
                                  chars=particle_chars, n=25, spread=4.5, lifetime=1400)
                self._buddy_sigh_of_relief()
                return

        # A little upward hop that settles with a bounce - positive
        # offsetY is defined as "shifted up" (see _position_buddy).
        self._buddy_move(self._offsetY, [(22.0, 120, "ease_out"), (0.0, 260, "bounce")])
        self.engine.burst((x0 + x1) / 2, (y0 + y1) / 2,
                          chars=particle_chars, n=45, spread=5.5, lifetime=1600)

        # Still holding a grudge over another card: pleased, but not
        # enough to stop glaring.
        if self._grudge_cards:
            return
        alt = fun_states(self._buddy_def())
        if alt:
            self._buddy_play(alt[0])

    def buddy_react_incorrect(self, card=None, stats=None):
        stats = stats or {}
        if stats.get("wrong_count", 0) >= GRUDGE_MISSES:
            self._grudge_cards.add(card)
        if self._grudge_cards or stats.get("wrong_streak", 0) >= ANGRY_STREAK:
            self._buddy_get_angry()
        else:
            self._buddy_get_embarrassed()

    def _buddy_get_embarrassed(self):
        """An "ouch" wince: the mascot ducks, wobbles sheepishly and pops
        back up, sweating a little."""
        self._buddy_play("embarrassed")
        self._buddy_move(self._offsetY, [(-9.0, 80, "ease_out"), (-9.0, 160, "linear"),
                                         (0.0, 380, "ease_io")])
        self._buddy_move(self._offsetX, [(-6.0, 80, "ease_out"), (5.0, 120, "ease_io"),
                                         (-3.0, 120, "ease_io"), (0.0, 140, "ease_io")])
        x, y = self._buddy_head()
        for _ in range(4):
            self.engine.emit(x + random.uniform(-4, 8), y + 8, random.choice([";", "'", "°"]),
                             random.uniform(0.4, 1.6), random.uniform(-2.2, -1.0),
                             random.randint(600, 900), gravity=0.22, tint="#5fa8e8")
        self._buddy_say(random.choice(["Ouch!", "Oof!", "Yikes!"]), self.themes[self.current_theme]["error"])

    def _buddy_get_angry(self):
        """A stomp and a furious shake. If a grudge is being held the mascot
        then settles into its "fuming" loop instead of "idle"."""
        self._buddy_play("angry")
        self._buddy_move(self._offsetY, [(16.0, 100, "ease_out"), (-4.0, 90, "ease_in"),
                                         (0.0, 220, "bounce")])
        self._buddy_move(self._offsetX, [(0.0, 190, "linear"), (-16, 50, "ease_io"),
                                         (15, 50, "ease_io"), (-12, 50, "ease_io"),
                                         (10, 50, "ease_io"), (-6, 50, "ease_io"),
                                         (0, 60, "ease_io")])
        x, y = self._buddy_head()
        self.engine.burst(x, y, chars=["╬", "#", "!"], n=12, spread=3.0, lifetime=1000,
                          tint="#e53935")
        self._buddy_say(random.choice(["Grr!", "Hmph!", "Again?!"]), "#e53935")

    def _buddy_sigh_of_relief(self):
        """Back to normal: a slow breath in, a long sigh out."""
        self._buddy_play("relieved")
        self._buddy_move(self._offsetX, [(0.0, 150, "ease_io")])
        self._buddy_move(self._offsetY, [(8.0, 450, "ease_io"), (-4.0, 900, "ease_io"),
                                         (0.0, 350, "ease_io")])

        def exhale():
            x, y = self._buddy_head()
            for i in range(5):
                self.engine.emit(x + i * 4, y + 18, random.choice(["~", "°", "∘"]),
                                 random.uniform(1.0, 2.0), random.uniform(-0.9, -0.3),
                                 random.randint(1000, 1500), gravity=-0.01, tint="#8fb8d8")
            self._buddy_say("Phew~", self.themes[self.current_theme]["success"])
        self.root.after(450, exhale)

    def _buddy_fume_puff(self):
        """While fuming, an anger mark or a puff of steam every so often."""
        x, y = self._buddy_head()
        char = random.choice(["╬", "~", "з"])
        self.engine.emit(x + random.uniform(-6, 6), y, char,
                         random.uniform(-0.4, 0.6), random.uniform(-1.4, -0.8),
                         random.randint(700, 1000),
                         gravity=-0.01, tint="#e53935" if char == "╬" else "#9aa4ae")

    def on_user_activity(self, event=None):
        self._last_activity = time.monotonic()
        if self._buddy_asleep:
            self._buddy_wake_startled()

    def _buddy_fall_asleep(self):
        self._buddy_asleep    = True
        self._buddy_state     = "sleeping"
        self._buddy_idle_ctr  = 0
        self._buddy_set_frame(0)
        # Slowly sink a little, like nodding off.
        self.engine.tween(self._offsetY, "v", -6.0, 900, "ease_io")

    def _buddy_wake_startled(self):
        self._buddy_asleep    = False
        self._buddy_state     = "startled"
        self._buddy_ftimer    = 0
        self._buddy_idle_ctr  = 0
        self._buddy_set_frame(0)
        # A sharp jump straight up, then a bouncy landing back at rest.
        self.engine.tween(self._offsetY, "v", 30.0, 90, "ease_out",
                          on_done=lambda: self.engine.tween(
                              self._offsetY, "v", 0.0, 380, "bounce"))
        x0, y0, x1, y1 = self._buddy_bbox()
        self.engine.burst((x0 + x1) / 2, y0 + 10,
                          chars=["!", "!", "?", "z"], n=18, spread=4.0, lifetime=900)

    def _anim_loop(self):
        # Step by the real time since the last tick (capped, so a stall
        # doesn't make everything jump), rather than assuming the after()
        # delay was exact - Tk timers routinely run late under load.
        now = time.perf_counter()
        dt = min(100.0, (now - self._last_tick) * 1000.0)
        self._last_tick = now
        self._tick_dt = dt
        self.engine.tick(dt)

        fps      = self._buddy_def()["fps"] * STATE_SPEED.get(self._buddy_state, 1.0)
        frame_ms = 1000 / fps
        rest = self._buddy_rest_state()
        self._buddy_ftimer += dt
        if self._buddy_ftimer >= frame_ms:
            self._buddy_ftimer    = 0
            nxt = self._buddy_frame_idx + 1
            # One-shot states show their last frame for a full beat, then
            # hand back to the resting state ("idle", or "fuming").
            if nxt >= len(self._buddy_frames()) and self._buddy_state not in LOOPING_STATES:
                self._buddy_state = rest
                nxt = 0
            self._buddy_frame_idx = nxt % len(self._buddy_frames())
            if not self._buddy_transition:
                self.main_canvas.itemconfig(self.buddy_text_id, text=self._buddy_frames()[self._buddy_frame_idx])

        self._buddy_idle_ctr += dt / self.TICK_MS  # counts 50 ms steps
        trigger = self._buddy_def()["idle_trigger"]
        alt     = fun_states(self._buddy_def())
        if self._buddy_state in ("idle", "fuming") and self._buddy_state != rest:
            self._buddy_play(rest)  # e.g. a new deck was loaded mid-grudge
        elif (self._buddy_state == "idle" and not self._buddy_transition
                and not self._celebration_active
                and time.monotonic() - self._last_activity >= BUDDY_SLEEP_SECONDS):
            self._buddy_fall_asleep()  # never mid-reaction, nor while fuming
        elif self._buddy_state == "sleeping":
            pass  # loops until on_user_activity wakes it
        elif self._buddy_state == "idle" and alt and self._buddy_idle_ctr >= trigger:
            self._buddy_play(alt[0])
        elif self._buddy_state == "fuming" and not self._buddy_transition:
            self._fume_timer += dt
            if self._fume_timer >= 1800:
                self._fume_timer = random.uniform(0, 600)
                self._buddy_fume_puff()

        if not any(t["target"] is self._scale for t in self.engine.tweens):
            if abs(self._scale["v"] - 1.0) > 0.01:
                self.engine.tween(self._scale, "v", 1.0, 200, "ease_out")

        a  = max(0.0, min(1.0, self._alpha["v"]))
        bg = self.get_current_color("bg")
        fg = self.get_current_color("fg")
        try:
            r1, g1, b1 = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
            r2, g2, b2 = int(fg[1:3], 16), int(fg[3:5], 16), int(fg[5:7], 16)
            blended = "#{:02x}{:02x}{:02x}".format(
                int(r1 + (r2 - r1) * a),
                int(g1 + (g2 - g1) * a),
                int(b1 + (b2 - b1) * a),
            )
            if blended != self._buddy_color:
                self._buddy_color = blended
                self.main_canvas.itemconfig(self.buddy_text_id, fill=blended)
        except Exception:
            pass

        # self._scale here is only ever driven by set_buddy()'s switch
        # animation (shrink-out / grow-back-in) - incorrect answers no
        # longer touch it, so this can't cause a per-answer size pulse.
        self._sync_buddy_font()
        self._position_buddy()

        self._update_combo_display(dt)
        self._draw_particles()

        if self._celebration_active:
            k = dt / self.TICK_MS
            self._dance_t += 0.18 * k
            self._rainbow_phase = (self._rainbow_phase + 0.012 * k) % 1.0
            self._draw_rainbow_progress_bar(self._last_bar_frac)
            self._update_celebration_dance()
            self._update_sidebar_dance()
            self._update_celebration_sprites()

        busy = (self._celebration_active or self.engine.particles
                or self.engine.tweens or self._combo_animating())
        interval = self.FAST_TICK_MS if busy else self.TICK_MS
        spent = (time.perf_counter() - now) * 1000.0
        self.root.after(max(1, int(interval - spent)), self._anim_loop)

    def _draw_particles(self):
        """Each particle keeps one canvas item for its whole life, which is
        moved and recolored every tick rather than deleted and recreated."""
        for p in self.engine.expired:
            if p["item"] is not None:
                self.main_canvas.delete(p["item"])
        self.engine.expired = []

        base = 15 * max(0.8, self.ui_scale)
        bg   = self.get_current_color("bg")
        for p in self.engine.particles:
            lf    = max(0.0, p["life"] / p["max_life"])
            if p["tint"]:
                color = self._blend_hex(bg, p["tint"], min(1.0, lf * 1.6))
            else:
                gray  = int(200 * lf)
                color = "#{:02x}{:02x}{:02x}".format(
                    gray, min(255, int(gray + 55)), min(255, int(gray + 100)))
            size  = int(base * p["scale"]) if p["fixed"] else max(10, int(base * p["scale"] * lf))
            x, y  = int(p["x"]), int(p["y"])
            if p["item"] is None:
                p["item"] = self.main_canvas.create_text(
                    x, y, text=p["char"], fill=color, tags="particle",
                    font=("Courier New", size))
                p["size"] = size
                continue
            self.main_canvas.coords(p["item"], x, y)
            if size != p["size"]:
                p["size"] = size
                self.main_canvas.itemconfig(p["item"], fill=color, font=("Courier New", size))
            else:
                self.main_canvas.itemconfig(p["item"], fill=color)

    @staticmethod
    def _blend_hex(c1, c2, a):
        """c1 -> c2 by a (0..1); falls back to c2 for non-#rrggbb colors."""
        try:
            r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
            r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
        except (ValueError, TypeError):
            return c2
        return "#{:02x}{:02x}{:02x}".format(int(r1 + (r2 - r1) * a),
                                            int(g1 + (g2 - g1) * a),
                                            int(b1 + (b2 - b1) * a))

    def _update_celebration_dance(self):
        """Bobs each main-canvas element around its own rest position with
        a distinct phase, so the whole panel ripples rather than moving
        as one rigid block."""
        rc = self._rest_coords
        if not rc:
            return
        t = self._dance_t
        specs = [
            ("q",        self.q_text_id,      0.0),
            ("prompt",   self.prompt_text_id, 0.6),
            ("entry",    self.entry_win_id,   0.9),
            ("submit",   self.submit_win_id,  1.2),
            ("feedback", self.feedback_text_id, 1.6),
            ("comment",  self.comment_text_id,  2.0),
            ("stats",    self.stats_text_id,    2.6),
        ]
        for key, item_id, phase in specs:
            base = rc.get(key)
            if not base or len(base) < 2:
                continue
            bx, by = base[0], base[1]
            dx = 6 * math.sin(t * 0.6 + phase)
            dy = 10 * math.sin(t + phase)
            try:
                self.main_canvas.coords(item_id, bx + dx, by + dy)
            except Exception:
                pass

    def _start_sidebar_dance(self):
        """Temporarily swaps every packed sidebar/topbar widget over to
        place() (frozen at its current on-screen position) so it can be
        animated independently without disturbing Pack's layout math, then
        hands each one a staggered phase so the whole strip ripples like a
        wave instead of moving in lockstep."""
        self._dance_widgets = []
        candidates = []
        for frame in (self.sidebar, self.progress_frame):
            for w in frame.winfo_children():
                try:
                    info = w.pack_info()
                except Exception:
                    continue  # not pack-managed (e.g. the *_bg_lbl backgrounds) - leave alone
                candidates.append((w, info))

        # Capture every widget's CURRENT position in one pass, before ANY
        # of them are detached from pack. Forgetting one widget shifts its
        # still-packed siblings to fill the gap - reading positions one at
        # a time while also detaching them would capture each subsequent
        # widget's already-collapsed position instead of its true resting
        # spot, which is what made the whole sidebar visibly hop upward
        # once at the start and then look "stuck".
        self.sidebar.update_idletasks()
        self.progress_frame.update_idletasks()
        snapshots = [
            (w, info, w.winfo_x(), w.winfo_y(), w.winfo_width(), w.winfo_height())
            for w, info in candidates
        ]

        for idx, (w, info, x, y, width, height) in enumerate(snapshots):
            w.pack_forget()
            w.place(x=x, y=y, width=width, height=height)
            self._dance_widgets.append({
                "widget": w, "base_x": x, "base_y": y,
                "pack_info": info, "phase": idx * 0.5,
            })

    def _update_sidebar_dance(self):
        # Sidebar buttons are wide-and-short bars stacked in a column, so a
        # side-to-side sway along their long axis reads far better than a
        # vertical bob (which barely registers against their height and
        # risks adjacent bars visually colliding). A small secondary
        # vertical wobble at a different frequency keeps the motion from
        # feeling like a flat 1-D slide.
        t = self._dance_t
        moved = False
        for d in self._dance_widgets:
            phase = d["phase"]
            dx = 11 * math.sin(t * 1.1 + phase)
            dy = 3 * math.sin(t * 2.3 + phase)
            pos = (int(d["base_x"] + dx), int(d["base_y"] + dy))
            if pos == d.get("pos"):
                continue  # re-placing a widget at the same spot still costs a relayout
            d["pos"] = pos
            moved = True
            try:
                d["widget"].place_configure(x=pos[0], y=pos[1])
            except Exception:
                pass

        # On Windows, the strip of the themed background label that a moving
        # button uncovers isn't reliably repainted, so the buttons' edges
        # smear across it like the Solitaire win screen. Ask the background
        # labels to redraw themselves after every move.
        if moved and sys.platform == "win32":
            for lbl in (self.sidebar_bg_lbl, self.topbar_bg_lbl):
                try:
                    lbl.event_generate("<Expose>", x=0, y=0, count=0,
                                       width=lbl.winfo_width(), height=lbl.winfo_height())
                except Exception:
                    pass

    def _stop_sidebar_dance(self):
        for d in self._dance_widgets:
            w = d["widget"]
            try:
                w.place_forget()
                info = {k: v for k, v in d["pack_info"].items() if k != "in"}
                w.pack(**info)
            except Exception:
                pass
        self._dance_widgets = []

    def _random_bright_color(self):
        hue = random.random()
        r, g, b = colorsys.hsv_to_rgb(hue, 0.75, 1.0)
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

    def _make_star(self, w, h):
        """One twinkling star: fixed at a random spot, pulsing size gives
        the twinkle, and it quietly respawns somewhere new every few
        seconds so the field keeps feeling alive rather than static."""
        return {
            "x": random.uniform(w * 0.06, w * 0.94),
            "y": random.uniform(h * 0.05, h * 0.88),
            "phase": random.uniform(0, 2 * math.pi),
            "speed": random.uniform(0.004, 0.009),  # radians per ms
            "base_size": random.randint(10, 18),
            "color": self._random_bright_color(),
            "life": random.uniform(2500, 5500),
            "age": 0.0,
        }

    def _spawn_firework(self, w, h):
        """A firework begins as a rising spark and explodes into a radial
        burst of embers once it reaches its (randomly chosen) apex."""
        return {
            "phase": "rising",
            "x": random.uniform(w * 0.15, w * 0.85),
            "y": h - 30,
            "start_y": h - 30,
            "apex_y": random.uniform(h * 0.15, h * 0.55),
            "t": 0.0,
            "rise_dur": random.uniform(420, 650),
            "color": self._random_bright_color(),
            "embers": [],
            "item": None,
        }

    def _explode_firework(self, fw):
        fw["phase"] = "exploded"
        if fw["item"] is not None:
            self.main_canvas.delete(fw["item"])
            fw["item"] = None
        for _ in range(random.randint(22, 34)):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 4.5)
            fw["embers"].append({
                "x": fw["x"], "y": fw["y"],
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.uniform(650, 1100),
                "age": 0.0,
                "item": None, "size": None,
            })

    def _spawn_celebration_sprites(self):
        """Sets up the celebration's background sparkle: a field of
        twinkling stars plus a fireworks launcher that keeps firing off
        random bursts at random positions for the rest of the celebration."""
        w = max(300, self.main_width or 1200)
        h = max(300, self.main_height or 700)
        self._celebration_stars = [self._make_star(w, h) for _ in range(22)]
        self._celebration_fireworks = []
        self._firework_timer = random.uniform(200, 450)  # first burst arrives quickly

    def _sprite_item(self, x, y, text, color, font):
        """New celebration sprite, stacked just above the background image."""
        item_id = self.main_canvas.create_text(
            x, y, text=text, fill=color, font=font, tags="celebration_sprite")
        self.main_canvas.tag_raise(item_id, self.bg_img_id)
        return item_id

    def _update_celebration_sprites(self):
        # Every star, spark and ember keeps one canvas item that is moved
        # and resized in place. Deleting and recreating ~150 text items
        # each frame was what made the celebration stutter.
        dt = self._tick_dt
        k = dt / self.TICK_MS
        w = max(300, self.main_width or 1200)
        h = max(300, self.main_height or 700)
        f_name = self.active_font_family()
        canvas = self.main_canvas

        # --- twinkling star field ---
        for i, s in enumerate(self._celebration_stars):
            s["age"] += dt
            if s["age"] >= s["life"]:
                old_item = s.get("item")
                s = self._make_star(w, h)
                s["item"] = old_item
                self._celebration_stars[i] = s
                if old_item is not None:
                    canvas.coords(old_item, s["x"], s["y"])
                    canvas.itemconfig(old_item, fill=s["color"])
            twinkle = math.sin(s["age"] * s["speed"] + s["phase"])
            size = max(6, int(s["base_size"] + 5 * twinkle))
            if s.get("item") is None:
                s["item"] = self._sprite_item(s["x"], s["y"], "✦", s["color"], (f_name, size))
                s["size"] = size
            elif size != s.get("size"):
                s["size"] = size
                canvas.itemconfig(s["item"], font=(f_name, size))

        # --- fireworks launcher: fires a new burst at a random spot every
        # ~0.5-1s, capped so a runaway timer can't pile up unboundedly ---
        self._firework_timer -= dt
        if self._firework_timer <= 0 and len(self._celebration_fireworks) < 4:
            self._celebration_fireworks.append(self._spawn_firework(w, h))
            self._firework_timer = random.uniform(500, 1000)

        alive_fireworks = []
        spark_font = (f_name, max(12, int(18 * self.ui_scale)))
        for fw in self._celebration_fireworks:
            if fw["phase"] == "rising":
                fw["t"] += dt
                progress = min(1.0, fw["t"] / fw["rise_dur"])
                fw["y"] = fw["start_y"] + (fw["apex_y"] - fw["start_y"]) * progress
                if fw["item"] is None:
                    fw["item"] = self._sprite_item(fw["x"], fw["y"], "✹", fw["color"], spark_font)
                else:
                    canvas.coords(fw["item"], fw["x"], fw["y"])
                if progress >= 1.0:
                    self._explode_firework(fw)
                alive_fireworks.append(fw)
            else:
                alive_embers = []
                for e in fw["embers"]:
                    e["age"] += dt
                    if e["age"] >= e["life"]:
                        if e["item"] is not None:
                            canvas.delete(e["item"])
                        continue
                    e["x"] += e["vx"] * k
                    e["y"] += e["vy"] * k
                    e["vy"] += 0.08 * k
                    life_frac = 1.0 - (e["age"] / e["life"])
                    size = max(6, int(6 + 12 * life_frac))
                    if e["item"] is None:
                        e["item"] = self._sprite_item(e["x"], e["y"], "✦", fw["color"], (f_name, size))
                        e["size"] = size
                    else:
                        canvas.coords(e["item"], e["x"], e["y"])
                        if size != e["size"]:
                            e["size"] = size
                            canvas.itemconfig(e["item"], font=(f_name, size))
                    alive_embers.append(e)
                fw["embers"] = alive_embers
                if fw["embers"]:
                    alive_fireworks.append(fw)
        self._celebration_fireworks = alive_fireworks

    def start_perfect_run_celebration(self):
        if self._celebration_active:
            self.stop_perfect_run_celebration()

        # Re-take the rest positions now: the feedback/tip text has changed
        # since the last layout pass, and the dance would otherwise snap the
        # tip back to where it sat before, underneath the "Answers:" text.
        self._snapshot_rest_coords()
        self._celebration_active = True
        self._dance_t = 0.0
        self._rainbow_phase = 0.0
        self._spawn_celebration_sprites()
        self._start_sidebar_dance()
        self.update_progress_display()

        if self._celebration_after_id:
            try:
                self.root.after_cancel(self._celebration_after_id)
            except Exception:
                pass
        self._celebration_after_id = self.root.after(14000, self.stop_perfect_run_celebration)

    def stop_perfect_run_celebration(self):
        if not self._celebration_active:
            return
        self._celebration_active = False

        if self._celebration_after_id:
            try:
                self.root.after_cancel(self._celebration_after_id)
            except Exception:
                pass
            self._celebration_after_id = None

        self.main_canvas.delete("celebration_sprite")
        self._celebration_stars = []
        self._celebration_fireworks = []
        self._stop_sidebar_dance()
        self.on_main_resize()  # snaps every canvas item back to its exact rest position
        self.update_progress_display()  # back to a plain solid-color bar

    # ── Modal Control Panel Configurations ────────────────
    def apply_custom_theme_selection(self, theme_folder_name, window_ref):
        self.active_custom_theme = theme_folder_name
        self.save_settings()
        self.preload_assets()

        def update_btn(btn, img_key):
            img = self.loaded_images.get(img_key)
            if img:
                btn.config(image=img, text="", padx=0, pady=0)
                btn.image = img
            else:
                btn.config(image="", text=btn.fallback_text, font=("Arial", 11, "bold"), padx=10, pady=8)
                btn.image = None
            # The underlying art changed, so drop any cached "already at
            # this size" markers - otherwise a same-size-but-different-art
            # theme swap would keep showing the previous theme's PNG.
            btn._scaled_size = None

        for btn in self.sidebar_buttons:
            update_btn(btn, btn.img_key)
        update_btn(self.submit_btn, "submit")
        self._submit_img_size = None

        self.apply_theme()
        self.rescale_sidebar_buttons(self.sidebar.winfo_width())
        self.on_main_resize()  # Force canvas + submit button to re-composite
        self.refresh_sidebar_bg()
        self.refresh_topbar_bg()
        window_ref.destroy()

    def open_theme_selector(self):
        top = tk.Toplevel(self.root)
        top.title("Theme Selector")
        top.config(bg=self.themes[self.current_theme]["sidebar_bg"])
        thumb_w, thumb_h = self.px(240), self.px(135)
        
        header = tk.Label(top, text="Select a Theme Profile", font=("Arial", 16, "bold"),
                          bg=self.themes[self.current_theme]["sidebar_bg"], 
                          fg=self.themes[self.current_theme]["fg"])
        header.pack(pady=15)

        grid_frame = tk.Frame(top, bg=self.themes[self.current_theme]["sidebar_bg"])
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        theme_folders = [None] 
        if os.path.exists("themes"):
            for d in os.listdir("themes"):
                if os.path.isdir(os.path.join("themes", d)):
                    theme_folders.append(d)

        row, col = 0, 0
        for theme_name in theme_folders:
            display_name = theme_name if theme_name else "Default Interface"
            
            thumb_path = None
            if theme_name:
                target = os.path.join("themes", theme_name, "bg_main.png")
                if os.path.exists(target): thumb_path = target
            else:
                if os.path.exists("bg_main.png"): thumb_path = "bg_main.png"

            thumb_img = None
            if thumb_path:
                try:
                    img = Image.open(thumb_path)
                    img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                    thumb_img = ImageTk.PhotoImage(img)
                    self.thumbnail_cache[display_name] = thumb_img 
                except Exception as e:
                    pass
            
            item_frame = tk.Frame(grid_frame, bg=self.themes[self.current_theme]["sidebar_bg"], bd=2, relief=tk.GROOVE)
            item_frame.grid(row=row, column=col, padx=10, pady=10)
            
            action_cmd = lambda t=theme_name: self.apply_custom_theme_selection(t, top)
            
            if thumb_img:
                btn = tk.Button(item_frame, image=thumb_img, command=action_cmd, cursor="hand2", bd=0)
                btn.pack(padx=5, pady=5)
            else:
                ph = tk.Canvas(item_frame, width=thumb_w, height=thumb_h, bg=self.themes[self.current_theme]["bg"], highlightthickness=1)
                ph.pack(padx=5, pady=5)
                ph.bind("<Button-1>", lambda e, t=theme_name: self.apply_custom_theme_selection(t, top))
                
            tk.Label(item_frame, text=display_name, font=("Arial", 10, "bold"),
                     bg=self.themes[self.current_theme]["sidebar_bg"], 
                     fg=self.themes[self.current_theme]["fg"]).pack(pady=5)
                     
            col += 1
            if col > 2:
                col = 0
                row += 1

        self.fit_window(top, 820, 0)

    def open_help_page(self):
        top = tk.Toplevel(self.root)
        top.title("Keisetsu Help Guide")
        top.config(bg=self.themes[self.current_theme]["bg"])

        text_box = tk.Text(top, wrap=tk.WORD, width=50, height=12, font=("Arial", 10), bg=self.themes[self.current_theme]["bg"], fg=self.themes[self.current_theme]["fg"], bd=0, padx=20, pady=20)
        text_box.pack(fill=tk.BOTH, expand=True)

        help_content = (
            "📖 WELCOME TO KEISETSU 📖\n\n"
            "▶ HOW TO STUDY:\n"
            "Click 'Import CSV' to load a deck from your 'vocab_lists' folder. Type the reading (e.g. Romaji or Kana) into the input box and hit Enter. "
            "Your Study Mascot will jump for joy if you get it right! Complete a session perfectly for a special trophy. "
            "Use 'Change Study Mascot' to pick a companion from Japanese folklore (Shiba Inu, Maneki-Neko, Daruma Doll, "
            "Spirit Kitsune, Tanuki) or Chinese mythology (Sun Wukong the Monkey King, Zhu Bajie, the Jade Rabbit, "
            "Nezha, or a Chinese Dragon). The same window sets where the mascot sits: "
            "any corner of the window (Bottom Left by default) or top center.\n\n"
            "▶ STUDYING MULTIPLE DECKS AT ONCE:\n"
            "In the Import CSV file picker, you can select more than one CSV at a time (ctrl/shift-click, or Ctrl+A). "
            "All of the selected decks are pooled together into a single shuffled session - handy for studying an "
            "entire textbook's chapter-by-chapter vocabulary lists all in one go.\n\n"
            "▶ MISSED CARDS:\n"
            "A card you get wrong is shuffled back into the cards still to come, so it pops up again at a random "
            "point in the session (never as the very next card) rather than waiting until the end. The more times "
            "you've missed a card, the more correct answers it takes to master it.\n\n"
            "▶ AUTO-KANA TOGGLE:\n"
            "Press the ` (grave/tilde) key on your keyboard to instantly turn the Romaji-to-Hiragana converter on or off. "
            "While the study language is Chinese, the same button (and hotkey) becomes Auto-Pinyin instead.\n\n"
            "▶ AUTO-PINYIN (CHINESE MODE):\n"
            "Type pinyin with a tone number after each syllable and it turns into tone marks as you type: "
            "'bu2shi4' becomes 'búshì', 'ni3hao3' becomes 'nǐhǎo'. Use 'v' (or 'u:') for ü, e.g. 'lv4' becomes 'lǜ', "
            "and 5 for the neutral tone, e.g. 'ma5' becomes 'ma'. If a deck's answers are written without tone marks, "
            "tones are not required to get the card right.\n\n"
            "▶ CHINESE DECKS & FONTS:\n"
            "Open 'Customize Font' to switch the study language between Japanese and Chinese. Each language remembers "
            "its own font (defaults: MS Mincho for Japanese, SimSun for Chinese) so characters are drawn in the correct "
            "regional style. If a font isn't installed on your computer, the closest installed match is used instead.\n\n"
            "▶ CSV MANAGER:\n"
            "Click 'CSV Manager' to open Keisetsu's companion deck-building tool (vocab_manager.py) in its own window. "
            "It saves decks straight into the same 'vocab_lists' folder Keisetsu imports from, so a deck you create or edit "
            "there is ready to study here immediately with 'Import CSV' - no need to move files around. "
            "To remove a row, click it to highlight it, then click 'Delete' at the top of the window "
            "(or press the Delete key) and confirm. The CSV Manager opens in Dark mode whenever Keisetsu is "
            "set to Dark mode.\n\n"
            "▶ THEMES & CUSTOMIZATION:\n"
            "You can customize Keisetsu endlessly by creating a folder inside the 'themes/' directory.\n"
            "Place the following PNG files into your folder and then activate it through the 'Themes' button:\n"
            "  - bg_main.png - Main Canvas\n"
            "  - bg_sidebar.png - Sidebar Background\n"
            "  - bg_topbar.png - Top Progress Bar\n"
            "  - Custom Buttons (e.g. btn_import.png)\n"
            "For the crispest results, aim for roughly the same proportions as the defaults "
            "(bg_main.png wide and tall, bg_sidebar.png narrow and tall, bg_topbar.png wide and short, "
            "buttons roughly 160x45) - but every one of these images is automatically rescaled to fit "
            "your actual window size and aspect ratio, so they'll still look right on a 1366x768 laptop, "
            "an ultrawide, or a vertical/portrait monitor.\n\n"
            "▶ GLASS PANEL OPACITY:\n"
            "In 'Custom BG Color', adjust the Container Opacity slider to seamlessly blend your flashcard container against your Custom 'bg_main.png' wallpaper."
        )
        text_box.insert(tk.END, help_content)
        text_box.config(state=tk.DISABLED)
        self.fit_window(top, 680, 560)

    def open_about_page(self):
        top = tk.Toplevel(self.root)
        top.title("About Keisetsu")
        top.resizable(False, False)
        top.config(bg=self.themes[self.current_theme]["sidebar_bg"])

        logo_path = "logo.png"
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                img.thumbnail((self.px(320), self.px(160)), Image.Resampling.LANCZOS)
                logo_img = ImageTk.PhotoImage(img)
                self.thumbnail_cache["about_logo"] = logo_img
                logo_lbl = tk.Label(top, image=logo_img, bg=self.themes[self.current_theme]["sidebar_bg"])
                logo_lbl.pack(pady=20)
            except Exception:
                logo_lbl = None
        else:
            logo_lbl = None

        title_lbl = tk.Label(top, text=f"Keisetsu - {BUILD_VERSION}", font=("Arial", 14, "bold"),
                 bg=self.themes[self.current_theme]["sidebar_bg"], fg=self.themes[self.current_theme]["fg"])
        title_lbl.pack(pady=5)
                 
        tk.Label(top, text=f"Build Date: {BUILD_DATE}", font=("Arial", 10),
                 bg=self.themes[self.current_theme]["sidebar_bg"], fg=self.themes[self.current_theme]["fg"]).pack(pady=2)

        home_link = tk.Label(top, text=f"Home: {HOME_URL}", font=("Arial", 10, "italic", "underline"),
                             cursor="hand2",
                             bg=self.themes[self.current_theme]["sidebar_bg"], fg=self.themes[self.current_theme]["comment"])
        home_link.pack(pady=10)
        home_link.bind("<Button-1>", lambda e: webbrowser.open(HOME_LINK))

        license_text = (
            "KEISETSU AI-GENERATION DISCLAIMER & OPEN SOFTWARE LICENSE\n\n"
            "The Keisetsu software and its accompanying source code are provided \"as is\", "
            "without warranty of any kind, express or implied. The source code architecture "
            "and logic of this software were generated entirely by an Artificial Intelligence.\n\n"
            "Permission is hereby granted, free of charge, to any person obtaining a copy "
            "of this software and associated documentation files, to deal in the software "
            "without restriction, including without limitation the rights to use, copy, "
            "modify, merge, publish, distribute, sublicense, and/or sell copies of the software, "
            "and to permit persons to whom the software is furnished to do so.\n\n"
            "Diligent studying leads to masterful results."
        )
        
        text_box = tk.Text(top, wrap=tk.WORD, height=12, width=50, font=("Arial", 9),
                           bg=self.themes[self.current_theme]["bg"], 
                           fg=self.themes[self.current_theme]["fg"],
                           relief=tk.SUNKEN, bd=2)
        text_box.insert(tk.END, license_text)
        text_box.config(state=tk.DISABLED) 
        text_box.pack(pady=20, padx=25)
        self.fit_window(top, 500, 0)

        # Secret: click the logo (or the title, if there's no logo.png)
        # COMBO_UNLOCK_CLICKS times before closing the window.
        clicks = [0]

        def on_logo_click(event):
            clicks[0] += 1
            if clicks[0] == COMBO_UNLOCK_CLICKS:
                self._show_secret_unlocked(top, text_box)
                self.unlock_combo_mode()
        (logo_lbl or title_lbl).bind("<Button-1>", on_logo_click)

    # ── Combo Mode (secret) ────────────────────────────────
    def _show_secret_unlocked(self, top, text_box):
        """Swaps the About window's disclaimer for a flashing, color-cycling
        SECRET MODE UNLOCKED message."""
        text_box.config(state=tk.NORMAL)
        text_box.delete("1.0", tk.END)
        text_box.tag_configure("center", justify="center")
        text_box.tag_configure("big", font=("Arial", 18, "bold"))
        text_box.tag_configure("sub", font=("Arial", 10, "bold"))
        text_box.tag_configure("small", font=("Arial", 9, "italic"))
        text_box.insert(tk.END, "\n\n", "center")
        text_box.insert(tk.END, "★ SECRET MODE UNLOCKED ★\n\n", ("center", "big"))
        text_box.insert(tk.END, "COMBO MODE\n", ("center", "sub"))
        text_box.insert(tk.END, "No hints. No waiting. Just combos.\n\n", ("center", "small"))
        text_box.insert(tk.END, "(Lasts until you switch decks or restart Keisetsu.)", ("center", "small"))
        text_box.config(state=tk.DISABLED)

        def cycle(hue=0.0):
            if not top.winfo_exists():
                return
            r, g, b = colorsys.hsv_to_rgb(hue % 1.0, 0.8, 1.0)
            text_box.tag_configure("big", foreground="#{:02x}{:02x}{:02x}".format(
                int(r * 255), int(g * 255), int(b * 255)))
            top.after(60, cycle, hue + 0.02)
        cycle()

    def unlock_combo_mode(self):
        self.set_combo_mode(True)

    def set_combo_mode(self, on):
        self.combo_mode = bool(on)
        # Combo Mode doesn't outlive the deck it was switched on for.
        self._combo_deck = self.df if self.combo_mode else None
        self._reset_combo()
        self._apply_combo_visibility()
        if self.combo_mode:
            self._splash_start = time.monotonic()
            # No waiting in Combo Mode: skip the rest of any result pause.
            if self._next_card_job is not None:
                self._schedule_next_card(0)
        else:
            self._splash_start = None
            self.main_canvas.itemconfig(self.splash_text_id, state=tk.HIDDEN)
        if getattr(self, "main_width", 0) > 1:
            self.on_main_resize()

    def _apply_combo_visibility(self):
        """Combo Mode strips the panel down to the question, the entry row,
        the mascot and the progress bar."""
        state = tk.HIDDEN if self.combo_mode else tk.NORMAL
        for item in (self.prompt_text_id, self.feedback_text_id,
                     self.comment_text_id, self.stats_text_id):
            self.main_canvas.itemconfig(item, state=state)

    def _repaint_combo_area(self):
        """Makes the canvas repaint the area around every visible piece of
        combo text, italic overhang included. Call it before moving, resizing
        or hiding them."""
        canvas = self.main_canvas
        area = None
        for item in (self.combo_text_id, self.breaker_text_id,
                     self.splash_text_id, *self.combo_halo_ids):
            if canvas.itemcget(item, "state") == tk.HIDDEN:
                continue
            box = canvas.bbox(item)
            if not box:
                continue
            m = 0.5 * (box[3] - box[1])
            box = (box[0] - m, box[1] - m, box[2] + m, box[3] + m)
            area = box if area is None else (min(area[0], box[0]), min(area[1], box[1]),
                                             max(area[2], box[2]), max(area[3], box[3]))
        if area:
            canvas.coords(self._combo_repaint_id, *area)

    def _reset_combo(self):
        self._repaint_combo_area()
        self.combo = 0
        self.combo_max = 0
        self._combo_shown_n = None
        self._breaker_until = 0.0
        self.main_canvas.itemconfig(self.combo_text_id, state=tk.HIDDEN)
        self.main_canvas.itemconfig(self.breaker_text_id, state=tk.HIDDEN)
        for hid in self.combo_halo_ids:
            self.main_canvas.itemconfig(hid, state=tk.HIDDEN)

    def _combo_hit(self):
        """A correct answer in Combo Mode: the question blows apart and the
        counter ticks up with a little jump."""
        self._explode_question()
        self.combo += 1
        self.combo_max = max(self.combo_max, self.combo)
        if self.combo < COMBO_SHOW_AT:
            return
        self._breaker_until = 0.0  # a new combo replaces the banner
        self._repaint_combo_area()
        self.main_canvas.itemconfig(self.breaker_text_id, state=tk.HIDDEN)
        self.main_canvas.itemconfig(self.combo_text_id, state=tk.NORMAL)
        self.engine.cancel(self._combo_jump)
        self.engine.tween(self._combo_jump, "v", max(12, 16 * self.ui_scale), 70, "ease_out",
                          on_done=lambda: self.engine.tween(self._combo_jump, "v", 0.0, 240, "bounce"))
        word = COMBO_MILESTONES.get(self.combo)
        if word is None and self.combo > 100 and self.combo % 50 == 0:
            word = "GODLIKE!"
        if word:
            x, y = self.combo_base
            self.engine.emit(x, y - 10, word, random.uniform(-0.5, 0.5), -2.4, 1400,
                             gravity=0.03, tint=self._random_bright_color(),
                             fixed_size=True, scale=1.5)
            self.engine.burst(x, y, chars=["★", "✦", "*"], n=24, spread=6.0, lifetime=1100,
                              tint="#FFD54F", scale=1.3)

    def _combo_break(self, correct_answer):
        """A miss in Combo Mode: a counter that was showing explodes into
        "C-C-C-COMBO BREAKER!!!", and the right answer flashes up briefly,
        since the usual feedback text is hidden."""
        if self.combo >= COMBO_SHOW_AT:
            bbox = self.main_canvas.bbox(self.combo_text_id)
            x, y = self.combo_base
            if bbox:
                x, y = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
            text = self.main_canvas.itemcget(self.combo_text_id, "text").replace(" ", "")
            self.engine.burst(x, y, chars=list(text) + ["✦", "*"], n=40, spread=9.0,
                              lifetime=1200, gravity=0.3, lift=3.0,
                              tint=self._combo_color(time.monotonic()), scale=1.8)
            self._breaker_start = time.monotonic()
            self._breaker_until = self._breaker_start + COMBO_BREAKER_MS / 1000
            self.main_canvas.itemconfig(self.breaker_text_id, state=tk.NORMAL)
        self._repaint_combo_area()
        self.combo = 0
        self._combo_shown_n = None
        self.main_canvas.itemconfig(self.combo_text_id, state=tk.HIDDEN)
        for hid in self.combo_halo_ids:
            self.main_canvas.itemconfig(hid, state=tk.HIDDEN)

        # The answer you should have given, drifting up like a damage
        # number from just under the COMBO BREAKER banner.
        x, y = self.combo_base
        self.engine.emit(x, y + max(45, int(60 * self.ui_scale)), correct_answer,
                         0, -0.3, 1800, gravity=0.0,
                         tint=self.themes[self.current_theme]["error"],
                         fixed_size=True, scale=1.3)

    def _explode_question(self):
        bbox = self.main_canvas.bbox(self.q_text_id)
        if not bbox:
            return
        x, y = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
        chars = [c for c in self.current_question_text if not c.isspace()] or ["*"]
        n = min(48, 14 + 3 * len(chars))
        for _ in range(n):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2.5, 8.0)
            self.engine.emit(x + random.uniform(-0.3, 0.3) * (bbox[2] - bbox[0]),
                             y + random.uniform(-0.3, 0.3) * (bbox[3] - bbox[1]),
                             random.choice(chars + ["✦"]),
                             math.cos(angle) * speed, math.sin(angle) * speed - 2.0,
                             random.randint(700, 1200), gravity=0.28,
                             tint=self._random_bright_color(), scale=2.2)

    def _show_combo_results(self):
        self.main_canvas.itemconfig(self.q_text_id, text="\n".join(
            [self.main_canvas.itemcget(self.q_text_id, "text"), f"MAX COMBO: {self.combo_max}"]))

    def _is_dark_bg(self):
        bg = self.get_current_color("bg")
        try:
            r, g, b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
        except (ValueError, TypeError):
            return False
        return (0.299 * r + 0.587 * g + 0.114 * b) < 128

    def _combo_color(self, now):
        """Amber, fading into a cycling rainbow from COMBO_RAINBOW_FROM hits
        to COMBO_RAINBOW_FULL."""
        base = "#FFC107" if self._is_dark_bg() else "#FF8F00"
        t = (self.combo - COMBO_RAINBOW_FROM) / (COMBO_RAINBOW_FULL - COMBO_RAINBOW_FROM)
        if t <= 0:
            return base
        r, g, b = colorsys.hsv_to_rgb(self._combo_hue % 1.0, 0.85, 1.0)
        rainbow = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
        return self._blend_hex(base, rainbow, min(1.0, t))

    def _fit_combo_size(self, text, size):
        """`size`, shrunk if needed so `text` spans at most 90% of the
        panel's width (the COMBO BREAKER banner is long)."""
        max_w = 0.9 * max(1, self.main_width)
        key = (text, size, int(max_w))
        cache = self.__dict__.setdefault("_combo_fit_cache", {})
        if key not in cache:
            fitted = size
            while fitted > 12 and font.Font(root=self.root, family=self._combo_family, size=fitted,
                                            weight="bold", slant="italic").measure(text) > max_w:
                fitted = int(fitted * 0.92)
            if len(cache) > 400:
                cache.clear()
            cache[key] = fitted
        return cache[key]

    def _combo_animating(self):
        """True while the combo display needs the fast animation tick."""
        if not self.combo_mode:
            return False
        return (self.combo >= COMBO_RAINBOW_FROM or self._breaker_until > 0
                or self._splash_start is not None)

    def _update_combo_display(self, dt):
        if not self.combo_mode:
            return
        now = time.monotonic()
        self._combo_hue = (self._combo_hue + dt / 2500.0) % 1.0
        cx, cy = self.combo_base
        canvas = self.main_canvas
        self._repaint_combo_area()  # clears last frame's italic overhang

        # "N HIT COMBO": grows with the combo up to a cap, jumps on each hit.
        if self.combo >= COMBO_SHOW_AT:
            n = self.combo
            size = int(min(20 + 0.5 * (n - COMBO_SHOW_AT), 44) * self.ui_scale)
            text = f"{n} HIT COMBO"
            size = self._fit_combo_size(text, max(12, size))
            font_spec = (self._combo_family, size, "bold", "italic")
            if self._combo_shown_n != (n, size):
                self._combo_shown_n = (n, size)
                canvas.itemconfig(self.combo_text_id, text=text, font=font_spec)
                for hid in self.combo_halo_ids:
                    canvas.itemconfig(hid, text=text, font=font_spec)
            dx = dy = 0.0
            if n >= COMBO_SHAKE_FROM:
                level = (n - COMBO_SHAKE_FROM) // 25 + 1
                amp = min(10.0, 2.5 * level) * max(1.0, self.ui_scale)
                dx, dy = random.uniform(-amp, amp), random.uniform(-amp, amp)
            x, y = cx + dx, cy + dy - self._combo_jump["v"]
            canvas.coords(self.combo_text_id, x, y)
            canvas.itemconfig(self.combo_text_id, fill=self._combo_color(now))

            # A pulsing white glow from COMBO_RAINBOW_FULL hits.
            if n >= COMBO_RAINBOW_FULL:
                pulse = 0.55 + 0.45 * math.sin(now * 5.0)
                glow_to = "#FFFFFF" if self._is_dark_bg() else "#FFE082"
                glow = self._blend_hex(self.get_current_color("bg"), glow_to, pulse)
                r = max(2, round(2 * self.ui_scale))
                offsets = [(r, 0), (-r, 0), (0, r), (0, -r),
                           (r * 0.7, r * 0.7), (-r * 0.7, r * 0.7),
                           (r * 0.7, -r * 0.7), (-r * 0.7, -r * 0.7)]
                for hid, (ox, oy) in zip(self.combo_halo_ids, offsets):
                    canvas.coords(hid, x + ox, y + oy)
                    canvas.itemconfig(hid, fill=glow, state=tk.NORMAL)
            else:
                for hid in self.combo_halo_ids:
                    canvas.itemconfig(hid, state=tk.HIDDEN)

        # "C-C-C-COMBO BREAKER!!!": slams in big, shakes, then fades out.
        if self._breaker_until:
            if now >= self._breaker_until:
                self._breaker_until = 0.0
                canvas.itemconfig(self.breaker_text_id, state=tk.HIDDEN)
            else:
                el = now - self._breaker_start
                slam = max(0.0, 1.0 - el / 0.18)
                size = int((30 + 30 * slam) * self.ui_scale)
                amp = (12 * max(0.0, 1.0 - el / 0.7) + 1.5) * max(1.0, self.ui_scale)
                left = self._breaker_until - now
                fade = min(1.0, left / 0.4)
                color = self._blend_hex(self.get_current_color("bg"), "#FF1744", fade)
                size = self._fit_combo_size("C-C-C-COMBO BREAKER!!!", max(14, size))
                canvas.itemconfig(self.breaker_text_id, fill=color,
                                  font=(self._combo_family, size, "bold", "italic"))
                canvas.coords(self.breaker_text_id, cx + random.uniform(-amp, amp),
                              cy + random.uniform(-amp, amp))

        # "COMBO MODE!" splash when the mode is switched on.
        if self._splash_start is not None:
            el = now - self._splash_start
            if el >= 1.4:
                self._splash_start = None
                canvas.itemconfig(self.splash_text_id, state=tk.HIDDEN)
            else:
                grow = min(1.0, el / 0.25)
                size = self._fit_combo_size("COMBO MODE!", int((20 + 36 * (1 - (1 - grow) ** 3)) * self.ui_scale))
                fade = min(1.0, (1.4 - el) / 0.5)
                color = self._blend_hex(self.get_current_color("bg"), self._combo_color(now)
                                        if self.combo >= COMBO_RAINBOW_FROM else "#FF1744", fade)
                canvas.itemconfig(self.splash_text_id, text="COMBO MODE!", state=tk.NORMAL, fill=color,
                                  font=(self._combo_family, size, "bold", "italic"))
                canvas.tag_raise(self.splash_text_id)

    # ── CSV Manager Launcher ───────────────────────────────
    def open_csv_manager(self):
        """Launches the standalone vocab_manager.py companion tool, which
        now owns all deck creation/editing. Keeping it out-of-process keeps
        Keisetsu itself small and focused on studying, and lets the two
        tools be updated independently.

        The Windows .exe has the manager built in, so it starts a second
        copy of itself with CSV_MANAGER_ARG."""
        if getattr(sys, "frozen", False):
            try:
                subprocess.Popen([sys.executable, CSV_MANAGER_ARG], cwd=APP_DIR)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch CSV Manager: {str(e)}")
            return

        candidates = [
            os.path.join(APP_DIR, VOCAB_MANAGER_SCRIPT),
            os.path.abspath(VOCAB_MANAGER_SCRIPT),
        ]
        script_path = next((p for p in candidates if os.path.exists(p)), None)

        if not script_path:
            messagebox.showerror(
                "CSV Manager Not Found",
                f"Could not find '{VOCAB_MANAGER_SCRIPT}'.\n\n"
                "Please make sure it is saved in the same folder as Keisetsu."
            )
            return

        try:
            subprocess.Popen([sys.executable, script_path], cwd=os.path.dirname(script_path))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch CSV Manager: {str(e)}")

    def choose_bg_color(self):
        top = tk.Toplevel(self.root)
        top.title("Custom BG Settings")
        top.config(bg=self.themes[self.current_theme]["sidebar_bg"])
        
        tk.Label(top, text="Core Background Color", font=("Arial", 12, "bold"), bg=self.themes[self.current_theme]["sidebar_bg"], fg=self.themes[self.current_theme]["fg"]).pack(pady=15)
        
        def do_color():
            c = colorchooser.askcolor(title="Select Background Color")
            if c[1]:
                self.custom_bg_color = c[1]
                self.save_settings()
                self.apply_theme()
                
        tk.Button(top, text="Select HEX Tone", command=do_color, font=("Arial", 10, "bold")).pack(pady=5)
        
        tk.Label(top, text="Glass Panel Opacity (Themes only):", font=("Arial", 10), bg=self.themes[self.current_theme]["sidebar_bg"], fg=self.themes[self.current_theme]["fg"]).pack(pady=15)
        
        op_var = tk.DoubleVar(value=self.content_opacity)
        op_scale = tk.Scale(top, variable=op_var, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, length=self.px(200), bg=self.themes[self.current_theme]["sidebar_bg"], fg=self.themes[self.current_theme]["fg"], highlightthickness=0)
        op_scale.pack()

        def do_opacity():
            self.content_opacity = op_var.get()
            self.save_settings()
            self.apply_theme()
            
        tk.Button(top, text="Apply Opacity", command=lambda: [do_opacity(), top.destroy()], font=("Arial", 10, "bold")).pack(pady=15)
        self.fit_window(top, 340, 0)

    def set_mascot_position(self, position):
        if position == self.mascot_position or position not in MASCOT_POSITIONS:
            return
        self.mascot_position = position
        self.save_settings()
        self.on_main_resize()

    def change_buddy(self):
        top = tk.Toplevel(self.root)
        top.title("Choose Study Mascot")
        top.resizable(False, False)  # sized to fit its contents
        top.config(bg=self.themes[self.current_theme]["sidebar_bg"])

        tk.Label(top, text="Select your study companion:", font=("Arial", 11, "bold"),
                 bg=self.themes[self.current_theme]["sidebar_bg"], fg=self.themes[self.current_theme]["fg"]).pack(pady=12)

        side_bg = self.themes[self.current_theme]["sidebar_bg"]
        fg      = self.themes[self.current_theme]["fg"]

        # One column per folklore tradition (the "origin" of each mascot).
        buddy_var = tk.StringVar(value=self.current_buddy)
        columns_frame = tk.Frame(top, bg=side_bg)
        columns_frame.pack(padx=24)
        origins = list(dict.fromkeys(a["origin"] for a in ANIMALS.values()))
        for col, origin in enumerate(origins):
            tk.Label(columns_frame, text=origin, font=("Arial", 10, "bold", "underline"),
                     bg=side_bg, fg=fg).grid(row=0, column=col, sticky=tk.W, padx=16, pady=(0, 4))
            names = [n for n, a in ANIMALS.items() if a["origin"] == origin]
            for row, name in enumerate(names, start=1):
                tk.Radiobutton(columns_frame, text=name, variable=buddy_var, value=name, font=("Arial", 11),
                               bg=side_bg, fg=fg, activebackground=side_bg, activeforeground=fg,
                               selectcolor=side_bg).grid(row=row, column=col, sticky=tk.W, padx=16, pady=3)
        tk.Label(top, text="Mascot position:", font=("Arial", 11, "bold"),
                 bg=side_bg, fg=fg).pack(pady=(14, 6))

        # Laid out as a little map of the panel: top row, then bottom row.
        pos_var  = tk.StringVar(value=self.mascot_position)
        pos_grid = tk.Frame(top, bg=side_bg)
        pos_grid.pack(padx=16)
        for row, label in enumerate(("Top", "Bottom")):
            tk.Label(pos_grid, text=label, font=("Arial", 10, "bold"),
                     bg=side_bg, fg=fg).grid(row=row, column=0, sticky=tk.W, padx=(0, 6))
        columns = {"left": 1, "center": 2, "right": 3}
        for name, (vert, horiz) in MASCOT_POSITIONS.items():
            tk.Radiobutton(pos_grid, text=name.split()[1], variable=pos_var, value=name, font=("Arial", 10),
                           bg=side_bg, fg=fg, activebackground=side_bg, activeforeground=fg,
                           selectcolor=side_bg).grid(row=0 if vert == "top" else 1, column=columns[horiz],
                                                     sticky=tk.W, padx=4, pady=2)

        tk.Button(top, text="Apply Companion",
                  command=lambda: [self.set_buddy(buddy_var.get()),
                                   self.set_mascot_position(pos_var.get()), top.destroy()],
                  font=("Arial", 10, "bold"), bg=self.get_current_color("bg"), fg=self.get_current_color("fg")).pack(pady=15)
        self.fit_window(top, 320, 0)

    def resolve_font_family(self, name, language):
        """Returns `name` if it's installed, otherwise the first installed
        look-alike for `language` (see FALLBACK_FONTS). Falls back to `name`
        itself so Tk can still pick its own substitute as a last resort."""
        key = (name, language)
        if key not in self._font_family_cache:
            installed = {f.lower(): f for f in font.families(self.root)}
            chosen = installed.get(name.strip().lower())
            if not chosen:
                chosen = next((installed[f.lower()] for f in FALLBACK_FONTS[language]
                               if f.lower() in installed), name)
            self._font_family_cache[key] = chosen
        return self._font_family_cache[key]

    def active_font_family(self):
        return self.resolve_font_family(self.font_name.get(), self.study_language)

    def change_font(self):
        side_bg = self.themes[self.current_theme]["sidebar_bg"]
        fg      = self.themes[self.current_theme]["fg"]

        top = tk.Toplevel(self.root)
        top.title("Customize Font")
        top.config(bg=side_bg)

        # Edits are kept local until "Apply", so closing the window
        # discards them instead of half-applying a font change.
        lang_var  = tk.StringVar(value=self.study_language)
        pending   = dict(self.language_fonts)
        name_var  = tk.StringVar(value=pending[self.study_language])
        size_var  = tk.StringVar(value=str(self.font_size.get()))

        tk.Label(top, text="Study Language:", font=("Arial", 10, "bold"),
                 bg=side_bg, fg=fg).pack(pady=(12, 2))
        lang_row = tk.Frame(top, bg=side_bg)
        lang_row.pack()

        tk.Label(top, text="Font Name (e.g., MS Mincho, Yu Gothic, SimSun, Microsoft YaHei):",
                 bg=side_bg, fg=fg).pack(pady=(12, 2))
        families = sorted({f for f in font.families(self.root) if not f.startswith("@")})
        name_box = ttk.Combobox(top, textvariable=name_var, values=families, width=35)
        name_box.pack(pady=5)

        tk.Label(top, text="Font Size (Recommended: 48-72 for Japanese/Chinese):",
                 bg=side_bg, fg=fg).pack(pady=(10, 2))
        tk.Entry(top, textvariable=size_var, width=10).pack(pady=5)

        preview = tk.Label(top, bg=side_bg, fg=fg)
        preview.pack(pady=8)
        note = tk.Label(top, font=("Arial", 8, "italic"), bg=side_bg, fg=fg)
        note.pack()

        def refresh_preview(*_):
            lang = lang_var.get()
            name = name_var.get().strip() or DEFAULT_FONTS[lang]
            family = self.resolve_font_family(name, lang)
            preview.config(text=FONT_SAMPLE_TEXT[lang], font=(family, 22))
            note.config(text="" if family.lower() == name.lower()
                        else f"'{name}' isn't installed - showing '{family}' instead.")

        def on_language_change():
            # Remember what was typed for the old language before swapping.
            pending[on_language_change.prev] = name_var.get().strip() or DEFAULT_FONTS[on_language_change.prev]
            on_language_change.prev = lang_var.get()
            name_var.set(pending[lang_var.get()])
        on_language_change.prev = lang_var.get()

        for lang in LANGUAGES:
            tk.Radiobutton(lang_row, text=lang, variable=lang_var, value=lang, font=("Arial", 10),
                           command=on_language_change, bg=side_bg, fg=fg,
                           activebackground=side_bg, activeforeground=fg,
                           selectcolor=side_bg).pack(side=tk.LEFT, padx=10)

        def reset_default():
            name_var.set(DEFAULT_FONTS[lang_var.get()])

        def apply():
            try:
                size = int(size_var.get())
                if size <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Font Size", "Please enter a whole number for the font size.", parent=top)
                return
            lang = lang_var.get()
            pending[lang] = name_var.get().strip() or DEFAULT_FONTS[lang]
            self.language_fonts = pending
            self.study_language = lang
            self.font_name.set(pending[lang])
            self.font_size.set(size)
            self.apply_font()
            self.update_autokana_button_text()
            self.save_settings()
            top.destroy()

        name_var.trace_add("write", refresh_preview)
        lang_var.trace_add("write", refresh_preview)
        refresh_preview()

        btn_row = tk.Frame(top, bg=side_bg)
        btn_row.pack(pady=12)
        tk.Button(btn_row, text="Reset to Default", command=reset_default,
                  font=("Arial", 10)).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_row, text="Apply Font Configuration", command=apply,
                  font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=6)
        self.fit_window(top, 480, 0)

    def choose_fg_color(self):
        color = colorchooser.askcolor(title="Select Font Text Color")
        if color[1]:
            self.custom_fg_color = color[1]
            self.save_settings()
            self.apply_theme()

    def get_current_color(self, target_key):
        if target_key == "bg" and self.custom_bg_color: return self.custom_bg_color
        if target_key == "fg" and self.custom_fg_color: return self.custom_fg_color
        return self.themes[self.current_theme][target_key]

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        bg    = self.get_current_color("bg")
        fg    = self.get_current_color("fg")
        side_bg = theme["sidebar_bg"]

        self.root.config(bg=bg)
        self.sidebar.config(bg=side_bg)
        
        self.sidebar_bg_lbl.config(bg=side_bg)
        self.refresh_sidebar_bg()

        self.topbar_bg_lbl.config(bg=theme["progress_bg"])
        self.refresh_topbar_bg()

        for child in self.sidebar.winfo_children():
            if child.winfo_exists():
                if isinstance(child, tk.Label) and child != self.sidebar_bg_lbl and child != self.btn_autokana:
                    child.config(bg=side_bg, fg=fg)
                elif isinstance(child, tk.Button):
                    child.config(bg=bg, fg=fg, activebackground=side_bg, activeforeground=fg)
        
        # It lives inside its glow frame rather than directly in the
        # sidebar, so the loop above never reaches it.
        self.btn_autokana.config(bg=side_bg, fg=fg)
        if self.sidebar.winfo_width() > 1:
            self.rescale_sidebar_buttons(self.sidebar.winfo_width())

        self.workspace.config(bg=bg)
        self.progress_frame.config(bg=theme["progress_bg"])
        self.progress_label.config(bg=theme["progress_bg"], fg=theme["progress_fg"])
        self.progress_canvas.config(bg=theme["canvas_bg"])

        # Update Canvas text elements
        self.main_canvas.itemconfig(self.q_text_id, fill=fg)
        self.main_canvas.itemconfig(self.prompt_text_id, fill=fg)
        self.main_canvas.itemconfig(self.stats_text_id, fill=fg)
        self.main_canvas.itemconfig(self.feedback_text_id, fill=theme["success"])
        self.main_canvas.itemconfig(self.comment_text_id, fill=fg)
        
        self.answer_entry.config(bg=bg, fg=fg, insertbackground=fg, highlightbackground=side_bg, relief=tk.SOLID, bd=1)
        
        self.on_main_resize() 
        self.update_progress_display()

    def toggle_theme(self):
        self.current_theme = "Dark" if self.current_theme == "Light" else "Light"
        self.custom_bg_color = None
        self.custom_fg_color = None
        self.save_settings()
        self.apply_theme()

    def apply_font(self):
        # Actual on-screen font sizes are derived from self.font_name /
        # self.font_size combined with the current resolution scale factor
        # (see apply_scaled_fonts) - recomputing the layout re-applies both
        # in one pass instead of duplicating the sizing logic here.
        self.root.after(50, self.on_main_resize)

    # ── Flashcard Runtime Operations Engine ───────────────
    def import_csv(self):
        # A fresh import is a clean break from whatever came before -
        # if the perfect-run celebration is mid-dance, cut it short rather
        # than let it keep animating over a brand new session.
        self.stop_perfect_run_celebration()

        # Created here (rather than unconditionally at every startup) so
        # they only appear once the user actually starts using the deck
        # workflow, and named to match what vocab_manager.py expects so a
        # deck built/edited there shows up here with zero extra setup.
        # The exists-check means an existing folder (and everything in it)
        # is never touched, let alone overwritten.
        for folder in ("vocab_lists", "themes"):
            if not os.path.exists(folder):
                os.makedirs(folder)

        initial_d = os.path.abspath("vocab_lists") if os.path.exists("vocab_lists") else "/"
        # askopenfilenames (plural) lets the user ctrl/shift-click to select
        # several decks at once - e.g. every chapter glossary from a
        # textbook - which are then pooled into one shuffled study session.
        file_paths = filedialog.askopenfilenames(initialdir=initial_d, filetypes=[("CSV Files", "*.csv")])
        if not file_paths:
            return
        try:
            deck_frames = []
            for fp in file_paths:
                frame = pd.read_csv(fp)
                if "Question" not in frame.columns or "Answers" not in frame.columns:
                    raise ValueError(f"'{os.path.basename(fp)}' must contain 'Question' and 'Answers' columns.")
                deck_frames.append(frame)

            # ignore_index=True is what makes the pooling safe: every card
            # gets a fresh 0..N-1 index across ALL selected decks combined,
            # so study_queue/card_stats/iloc lookups all keep working
            # exactly as before regardless of how many files went in.
            self.df = pd.concat(deck_frames, ignore_index=True) if len(deck_frames) > 1 else deck_frames[0]

            self.current_csv_paths = list(file_paths)
            self.study_queue = list(self.df.index)
            random.shuffle(self.study_queue)
            self.card_stats = {
                idx: {"wrong_count": 0, "wrong_streak": 0, "correct_since_wrong": 0,
                      "mastered": False, "first_attempt": True}
                for idx in self.df.index
            }
            self.perfect_run = True 
            self._grudge_cards.clear()
            self._cancel_next_card()
            # Switching decks ends Combo Mode. Switched on before any deck
            # was loaded, it carries over to the first one.
            if self.combo_mode and self._combo_deck is not None:
                self.set_combo_mode(False)
            elif self.combo_mode:
                self._combo_deck = self.df
            self._reset_combo()

            theme = self.themes[self.current_theme]
            if len(file_paths) > 1:
                loaded_msg = f"{len(file_paths)} decks pooled ({len(self.df)} cards)! Press Enter to start."
            else:
                loaded_msg = "CSV Loaded! Press Enter to start."
            self.main_canvas.itemconfig(self.feedback_text_id, text=loaded_msg, fill=theme["success"])
            self.main_canvas.itemconfig(self.comment_text_id, text="")
            self.reflow_feedback_area()
            self.update_progress_display()
            self.answer_entry.config(state=tk.NORMAL)
            self.next_card()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV(s): {str(e)}")

    def update_progress_display(self):
        if self.df is None:
            return
        total    = len(self.df)
        mastered = sum(1 for s in self.card_stats.values() if s["mastered"])
        pct      = (mastered / total * 100) if total > 0 else 0

        self.progress_label.config(text=f"Progress: {mastered}/{total} mastered ({pct:.1f}%)")
        self._last_bar_frac = pct / 100
        self.redraw_progress_bar()

    def redraw_progress_bar(self):
        """Draws the bar at the canvas's current width, so it's called both
        when progress changes and whenever the canvas is resized."""
        if self._celebration_active:
            self._draw_rainbow_progress_bar(self._last_bar_frac)
            return
        self.progress_canvas.delete("progress_bar")
        self._rainbow_key = None
        bar_w = self.progress_canvas.winfo_width() * self._last_bar_frac
        bar_h = self.progress_canvas.winfo_height()
        if bar_w <= 0:
            return
        fill_col = self.themes[self.current_theme]["success"]
        self.progress_canvas.create_rectangle(0, 0, bar_w, bar_h, fill=fill_col, outline="", tags="progress_bar")

    def _draw_rainbow_progress_bar(self, frac):
        """Draws the bar as a hue-cycling gradient - called every animation
        tick during a perfect-run celebration with self._rainbow_phase
        shifted slightly each time, which gives it the shimmering "moving
        rainbow" look. The gradient is rendered once into an image two
        bar-widths wide (one full hue cycle per width), and each tick only
        slides that image left; a cover rectangle hides it past the bar's
        end."""
        total_w = self.progress_canvas.winfo_width()
        bar_h = self.progress_canvas.winfo_height()
        bar_w = total_w * frac
        if bar_w <= 0 or total_w <= 1:
            return
        key = (total_w, bar_h, bar_w)
        if key != self._rainbow_key:
            self.progress_canvas.delete("progress_bar")
            self._rainbow_key = key
            row = []
            for x in range(total_w * 2):
                r, g, b = colorsys.hsv_to_rgb((x / total_w) % 1.0, 0.85, 1.0)
                row.append("#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255)))
            self._rainbow_img = tk.PhotoImage(width=total_w * 2, height=bar_h)
            self._rainbow_img.put("{" + " ".join(row) + "}", to=(0, 0, total_w * 2, bar_h))
            self._rainbow_img_id = self.progress_canvas.create_image(
                0, 0, anchor=tk.NW, image=self._rainbow_img, tags="progress_bar")
            if bar_w < total_w:
                self.progress_canvas.create_rectangle(
                    bar_w, 0, total_w, bar_h, outline="",
                    fill=self.progress_canvas.cget("bg"), tags="progress_bar")
        # Showing the image from x = phase * total_w gives the colour at
        # screen x the hue (x / total_w + phase), same as the old slices.
        self.progress_canvas.coords(self._rainbow_img_id, -self._rainbow_phase * total_w, 0)

    def next_card(self):
        self.study_queue = [i for i in self.study_queue if not self.card_stats.get(i, {}).get("mastered", False)]

        theme = self.themes[self.current_theme]

        if not self.study_queue:
            self.answer_entry.config(state=tk.DISABLED)
            self.main_canvas.itemconfig(self.stats_text_id, text="Done!")
            
            if self.perfect_run:
                self.main_canvas.itemconfig(self.q_text_id, text="PERFECT RUN!", fill=theme["success"])
                self.main_canvas.itemconfig(self.comment_text_id, text="Incredible! You cleared the entire dataset without making a single mistake! 🎉", fill=theme["success"])
                self.start_perfect_run_celebration()
            else:
                self.main_canvas.itemconfig(self.q_text_id, text="All cards mastered!", fill=theme["success"])
                self.main_canvas.itemconfig(self.comment_text_id, text="Great job! You've mastered all cards.", fill=self.get_current_color("fg"))

            if self.combo_mode:
                self._show_combo_results()
            self.refit_question_text()
            self.reflow_feedback_area()
            self.update_progress_display()
            self.buddy_react_correct(self.current_question_text)
            return

        self.current_card_index = self.study_queue.pop(0)
        self.last_practiced_index = self.current_card_index
        row           = self.df.iloc[self.current_card_index]
        question_text = row["Question"] if not pd.isna(row["Question"]) else "Error: Empty Question"
        self.current_question_text = str(question_text)

        self.main_canvas.itemconfig(self.q_text_id, text=self.current_question_text, fill=self.get_current_color("fg"))
        self.refit_question_text()

        self.answer_entry.config(state=tk.NORMAL)
        self.answer_entry.focus_set()
        self.main_canvas.itemconfig(self.feedback_text_id, text="")
        self.main_canvas.itemconfig(self.comment_text_id, text="")
        self.reflow_feedback_area()

        remaining = len([i for i in self.study_queue if not self.card_stats.get(i, {}).get("mastered", False)])
        self.main_canvas.itemconfig(self.stats_text_id, text=f"Cards remaining: {remaining}")
        self.update_progress_display()

    # A missed card never comes back as the very next card (when there are
    # others left), so the retry isn't just an instant repeat.
    REQUEUE_MIN_GAP = 2

    def requeue_card(self, idx):
        """Puts a card that still needs work back into the deck at a random
        spot among the cards still to come, so a missed card resurfaces
        partway through the session instead of waiting at the end."""
        gap = min(self.REQUEUE_MIN_GAP, len(self.study_queue))
        self.study_queue.insert(random.randint(gap, len(self.study_queue)), idx)

    def _schedule_next_card(self, delay_ms):
        """Shows the next card after `delay_ms` (0 = right away, as in
        Combo Mode). Only one can be pending, and answers are ignored while
        one is, so pressing Enter twice can't grade a card twice or skip
        the card after it."""
        self._cancel_next_card()
        if delay_ms <= 0:
            self.next_card()
        else:
            self._next_card_job = self.root.after(delay_ms, self._run_next_card)

    def _run_next_card(self):
        self._next_card_job = None
        self.next_card()

    def _cancel_next_card(self):
        if self._next_card_job is not None:
            self.root.after_cancel(self._next_card_job)
            self._next_card_job = None

    def check_answer(self, event=None):
        if self.current_card_index is None or self.df is None:
            return
        if self._next_card_job is not None:
            return  # still showing the last result

        user_input = self.answer_entry.get().strip()
        if not user_input:
            return
        self.answer_entry.delete(0, tk.END)

        row          = self.df.iloc[self.current_card_index]
        answer_list  = [a.strip() for a in str(row["Answers"]).split(",") if a.strip()]
        raw_answers  = ", ".join(answer_list)
        possible     = [a.lower() for a in answer_list]
        user_clean   = user_input.lower().strip()
        comment_text = str(row["Comment"]) if "Comment" in row and pd.notna(row["Comment"]) else ""
        stats        = self.card_stats[self.current_card_index]

        if self.study_language == "Chinese":
            # Accept "ni3" as well as "nǐ", ignore spaces/apostrophes
            # ("nǐ hǎo" == "nǐhǎo"), and if the deck's answer was written
            # without tone marks, don't demand them from the user either.
            def norm(text, drop_tones):
                text = convert_to_pinyin(text).replace(" ", "").replace("'", "")
                return strip_pinyin_tones(text) if drop_tones else text
            matched = any(
                norm(user_clean, strip_pinyin_tones(a) == a) == norm(a, strip_pinyin_tones(a) == a)
                for a in possible
            )
        else:
            matched = user_clean in possible

        if matched:
            self.handle_correct(comment_text, stats, raw_answers)
        else:
            self.handle_incorrect(raw_answers, comment_text, stats)

    def handle_correct(self, comment, stats, raw_answers):
        idx   = self.current_card_index
        theme = self.themes[self.current_theme]

        if stats["first_attempt"]:
            stats["mastered"] = True
            self.main_canvas.itemconfig(self.feedback_text_id, text=f"Correct! First try! Mastered!\nAnswers: {raw_answers}", fill=theme["success"])
        else:
            wrong_count = stats["wrong_count"]
            if wrong_count == 0:
                stats["mastered"] = True
            else:
                increment = 100 / (wrong_count + 1)
                stats["correct_since_wrong"] += 1
                current_pct = min(100, stats["correct_since_wrong"] * increment)
                if current_pct >= 100:
                    stats["mastered"] = True
                    self.main_canvas.itemconfig(self.feedback_text_id, text=f"Correct! ({current_pct:.0f}%) Mastered!\nAnswers: {raw_answers}", fill=theme["success"])
                else:
                    self.requeue_card(idx)
                    self.main_canvas.itemconfig(self.feedback_text_id, text=f"Correct! ({current_pct:.0f}%) Keep going!\nAnswers: {raw_answers}", fill=theme["success"])

        if comment.strip():
            self.main_canvas.itemconfig(self.comment_text_id, text=f"Tip: {comment}", fill=theme["comment"])

        self.reflow_feedback_area()
        stats["first_attempt"] = False
        stats["wrong_streak"] = 0
        self.buddy_react_correct(self.current_question_text, idx, stats["mastered"])
        if self.combo_mode:
            self._combo_hit()
            self._schedule_next_card(0)
        else:
            self._schedule_next_card(5000)

    def handle_incorrect(self, correct_answer, comment, stats):
        idx   = self.current_card_index
        theme = self.themes[self.current_theme]

        self.perfect_run = False 

        stats["wrong_count"] += 1
        stats["wrong_streak"] = stats.get("wrong_streak", 0) + 1
        stats["correct_since_wrong"] = 0
        stats["first_attempt"] = False

        wrong_count  = stats["wrong_count"]
        increment    = 100 / (wrong_count + 1)
        current_pct  = stats["correct_since_wrong"] * increment

        self.requeue_card(idx)

        feedback = f"Wrong! ({current_pct:.0f}%)\nAnswers: {correct_answer}"
        if comment.strip():
            feedback += f"\n\nTip: {comment}"

        self.main_canvas.itemconfig(self.feedback_text_id, text=feedback, fill=theme["error"])
        self.main_canvas.itemconfig(self.comment_text_id, text="")
        self.reflow_feedback_area()

        self.buddy_react_incorrect(idx, stats)
        if self.combo_mode:
            self._combo_break(correct_answer)
            self._schedule_next_card(0)
        else:
            self._schedule_next_card(5000)

if __name__ == "__main__":
    # Settings, themes/ and vocab_lists/ are found relative to the working
    # directory, so start from Keisetsu's own folder however it was launched.
    os.chdir(APP_DIR)
    if CSV_MANAGER_ARG in sys.argv[1:]:
        import vocab_manager
        vocab_manager.main()
        sys.exit()
    # className sets the X11 WM_CLASS, so Linux panels/taskbars (e.g.
    # Cinnamon on Linux Mint) group and label the window as "Keisetsu".
    root = tk.Tk(className="Keisetsu")
    app  = KeisetsuApp(root)
    root.mainloop()