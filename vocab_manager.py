#!/usr/bin/env python3
"""
Vocab List Manager (Y2K Edition)
=================================
A little Windows-XP-flavored desktop app for building and editing
"Question, Answers, Comment, Instructions" style vocab CSVs
(the same shape as Intermediate_Japanese_会話１単語リスト.csv).

Highlights
----------
* New / Edit launcher screen.
* Spreadsheet-style view of the CSV (a ttk.Treeview).
* Double-click a row to edit just that row, with a "Batch Add" button
  that jumps into rapid-entry mode.
* Click a row and press "Delete" (or the Delete key) to remove it, after
  a confirmation prompt.
* Sizes itself to the display: row heights, columns, banners and the
  window follow the rendered font size, so it stays readable at any
  display scaling (Windows 125%/150%, Linux Mint fractional scaling...).
* Rapid-entry ("Batch Add") mode: type Question, Enter, type Answer,
  Enter, type Comment, Enter -> row is saved to disk immediately and
  a new blank row starts automatically. Built for transcribing a
  stack of vocab from a book without needing to touch the mouse.
* "Instructions" (constant across every row in the example file) is
  treated as a per-file "template" that's set once and auto-applied to
  every new row, so rapid entry only ever touches Question / Answers /
  Comment.
* Multiple answers are separated by commas and always saved as
  "answer, answer, answer", whether or not a space was typed.
* Follows Keisetsu's Bright/Dark mode (read from keisetsu_settings.json,
  so it works when run on its own too).
* "Pinyin tone input" toggle for Chinese decks: typing "bu2shi4" in
  the Question / Answers / Comment fields turns into "búshì" as you type.

Requires only the Python standard library (tkinter + csv).
"""

import os
import re
import sys
import csv
import json
import datetime
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox

# --------------------------------------------------------------------------
# Paths / constants
# --------------------------------------------------------------------------

APP_TITLE = "Vocab List Manager"
FIELDNAMES = ["Question", "Answers", "Comment", "Instructions"]

# Inside Keisetsu's Windows .exe, __file__ points into a temporary unpack
# folder, so use the folder that holds the .exe instead.
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DIR = os.path.join(BASE_DIR, "vocab_lists")
KEISETSU_SETTINGS = os.path.join(BASE_DIR, "keisetsu_settings.json")


def format_answers(text):
    """Normalizes a comma-separated answer list to "a, b, c" so it reads
    the same however it was typed ("a,b,c", "a , b,c", ...)."""
    return ", ".join(a.strip() for a in text.split(",") if a.strip())


def _keisetsu_setting(key, default):
    try:
        with open(KEISETSU_SETTINGS, encoding="utf-8") as f:
            return json.load(f).get(key, default)
    except (OSError, ValueError, AttributeError):
        return default


def keisetsu_language():
    """The study language last picked in Keisetsu's Customize Font menu,
    so Chinese-specific helpers can start switched on automatically."""
    return _keisetsu_setting("language", "Japanese")


def keisetsu_dark_mode():
    """True when Keisetsu was last left in Dark mode (its Bright/Dark
    toggle), so the manager opens dark too - even when run on its own."""
    return _keisetsu_setting("theme", "Light") == "Dark"

# --------------------------------------------------------------------------
# Y2K / Windows-XP "Luna" flavored color palette
# --------------------------------------------------------------------------

BG_COLOR = "#ECE9D8"        # classic XP dialog face (silver/tan)
PANEL_BG = "#ECE9D8"
FIELD_BG = "#FFFFFF"
FIELD_FG = "#000000"
FIELD_BORDER = "#7F9DB9"    # XP input-box border blue-gray
SELECT_BG = "#316AC5"       # XP selection blue
SELECT_FG = "#FFFFFF"
HEADER_BG = "#D4D0C8"
HEADER_ACTIVE = "#ECE9D8"
BORDER_DARK = "#716F64"
BANNER_TOP = "#0A246A"      # deep XP wizard-banner blue
BANNER_BOTTOM = "#B0C9EE"   # light blue fade
BANNER_SUB_FG = "#E4ECFB"
STRIPE_BG = "#F3F6FC"
GOOD_GREEN = "#0A6E1D"
TEXT_FG = "#000000"
HINT_FG = "#444444"         # small grey hint lines
GROUP_FG = "#333333"        # LabelFrame titles
BTN_FACE = "#D4D0C8"        # classic button-face gray -- deliberately a shade
BTN_ACTIVE = "#C8C4B8"      # cooler/darker than the tan dialog bg so buttons
BTN_HILITE = "#FFFFFF"      # actually read as raised, clickable controls

# Dark mode follows Keisetsu's Bright/Dark toggle (keisetsu_settings.json).
# Same layout and XP flavor, night-time colors - matched to Keisetsu's own
# Dark theme so switching between the two apps doesn't flash.
DARK_MODE = keisetsu_dark_mode()
if DARK_MODE:
    BG_COLOR = PANEL_BG = "#2B2B2B"
    FIELD_BG = "#1E1E1E"
    FIELD_FG = "#EAEAEA"
    FIELD_BORDER = "#56657A"
    HEADER_BG = "#3C3F41"
    HEADER_ACTIVE = "#4A4D50"
    BORDER_DARK = "#151515"
    BANNER_TOP = "#0A1A4A"
    BANNER_BOTTOM = "#2E4A7A"
    BANNER_SUB_FG = "#C8D6EE"
    STRIPE_BG = "#262A30"
    GOOD_GREEN = "#4CAF50"
    TEXT_FG = "#EAEAEA"
    HINT_FG = "#A8A8A8"
    GROUP_FG = "#C8C8C8"
    BTN_FACE = "#45484B"
    BTN_ACTIVE = "#55595D"
    BTN_HILITE = "#6A6E72"

_UI_FONT_FAMILY = None
_DATA_FONT_FAMILY = None

# How much bigger text actually renders than the ~15 px line height a 9 pt
# UI font has at 100% zoom on a 96-DPI screen. Set by compute_ui_scale().
# Fonts are sized in points, so the desktop's display scaling (Windows
# 125%/150%, Linux Mint's fractional scaling, a 4K panel...) already grows
# them; every *pixel* size in this file goes through px() so row heights,
# column widths, banners and the window itself grow along with the text
# instead of letting it overlap.
UI_SCALE = 1.0
_BASE_LINESPACE = 15


def compute_ui_scale():
    """Measures the rendered UI font rather than trusting the reported
    DPI, which on Linux often disagrees with what fontconfig really draws
    (e.g. Mint at 125% renders at 192 DPI while Tk reports 120). Must be
    called after resolve_fonts()."""
    global UI_SCALE
    linespace = tkfont.Font(font=UI_FONT(9)).metrics("linespace")
    UI_SCALE = max(1.0, min(4.0, linespace / _BASE_LINESPACE))


def px(n):
    """A pixel size from the 100%-zoom design, scaled for this display."""
    return int(round(n * UI_SCALE))


def line_height(font_spec):
    return tkfont.Font(font=font_spec).metrics("linespace")


def resolve_fonts():
    """Pick a Tahoma-ish UI font and a CJK-capable data font from what's
    actually installed, falling back gracefully. Must be called AFTER a
    Tk root exists."""
    global _UI_FONT_FAMILY, _DATA_FONT_FAMILY
    available = set(tkfont.families())

    for name in ("Tahoma", "Segoe UI", "MS Sans Serif", "Verdana", "Arial"):
        if name in available:
            _UI_FONT_FAMILY = name
            break
    else:
        _UI_FONT_FAMILY = "TkDefaultFont"

    if keisetsu_language() == "Chinese":
        data_fonts = ("Microsoft YaHei", "SimSun", "PingFang SC", "Noto Sans CJK SC",
                      "Noto Serif CJK SC", "WenQuanYi Micro Hei")
    else:
        data_fonts = ("Yu Gothic UI", "Meiryo", "MS Gothic", "Noto Sans CJK JP",
                      "Hiragino Sans", "TakaoGothic", "IPAGothic", "Noto Sans JP")
    for name in data_fonts:
        if name in available:
            _DATA_FONT_FAMILY = name
            break
    else:
        _DATA_FONT_FAMILY = _UI_FONT_FAMILY


def UI_FONT(size=9, weight="normal"):
    return (_UI_FONT_FAMILY, size, weight)


def DATA_FONT(size=11, weight="normal"):
    return (_DATA_FONT_FAMILY, size, weight)


# --------------------------------------------------------------------------
# Numbered pinyin -> tone marks (kept in sync with keisetsu.py)
# --------------------------------------------------------------------------

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


def bind_pinyin_input(entry, var, enabled):
    """Live-converts numbered pinyin in `entry` while the `enabled`
    BooleanVar is on, keeping the cursor where the user was typing."""
    busy = [False]

    def on_write(*_):
        if busy[0] or not enabled.get():
            return
        raw = var.get()
        converted = convert_to_pinyin(raw)
        if converted != raw:
            cursor = entry.index(tk.INSERT)
            busy[0] = True
            var.set(converted)
            busy[0] = False
            entry.icursor(cursor + len(converted) - len(raw))

    var.trace_add("write", on_write)


def make_pinyin_toggle(parent, variable, bg=BG_COLOR):
    return tk.Checkbutton(
        parent, text="Pinyin tone input (bu2shi4 \u2192 b\u00fash\u00ec)", variable=variable,
        font=UI_FONT(9), bg=bg, activebackground=bg, anchor="w",
    )


# --------------------------------------------------------------------------
# Small retro-styled widget helpers
# --------------------------------------------------------------------------

def make_button(parent, text, command, width=None, primary=False):
    b = tk.Button(
        parent, text=text, command=command,
        font=UI_FONT(9, "bold" if primary else "normal"),
        bg=BTN_FACE, activebackground=BTN_ACTIVE,
        relief="raised", bd=2, padx=px(12), pady=px(4), cursor="hand2",
    )
    if width:
        b.config(width=width)
    return b


def make_entry(parent, textvariable=None, width=32, font=None, justify="left"):
    return tk.Entry(
        parent, textvariable=textvariable, width=width,
        font=font or DATA_FONT(11), relief="sunken", bd=2,
        highlightthickness=1, highlightbackground=FIELD_BORDER,
        highlightcolor=FIELD_BORDER, justify=justify,
    )


def make_label(parent, text, bold=False, size=9, fg=TEXT_FG, bg=BG_COLOR, justify="left"):
    return tk.Label(parent, text=text, font=UI_FONT(size, "bold" if bold else "normal"),
                     fg=fg, bg=bg, justify=justify)


def make_banner(parent, title, subtitle=None, height=58):
    """A classic blue XP-wizard-style gradient banner with white title text.
    Its height follows the rendered title/subtitle, so they never clip."""
    title_font = (_UI_FONT_FAMILY, 13, "bold")
    title_h = line_height(title_font)
    sub_h = line_height(UI_FONT(8)) if subtitle else 0
    height = max(px(height), title_h + sub_h + px(12))
    canvas = tk.Canvas(parent, height=height, highlightthickness=0, bd=0)
    canvas.pack(fill="x", side="top")

    def hexmix(c1, c2, t):
        c1 = c1.lstrip("#")
        c2 = c2.lstrip("#")
        r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
        r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def draw(event=None):
        canvas.delete("grad")
        width = max(canvas.winfo_width(), 1)
        steps = 40
        for i in range(steps):
            t = i / steps
            color = hexmix(BANNER_TOP, BANNER_BOTTOM, t)
            x0 = int(width * t)
            x1 = int(width * (t + 1.0 / steps)) + 1
            canvas.create_rectangle(x0, 0, x1, height, outline="", fill=color, tags="grad")
        top = (height - title_h - sub_h) // 2
        canvas.create_text(px(16), top, anchor="nw", text=title,
                            font=title_font, fill="white", tags="grad")
        if subtitle:
            canvas.create_text(px(18), top + title_h, anchor="nw", text=subtitle,
                                font=UI_FONT(8), fill=BANNER_SUB_FG, tags="grad")

    canvas.bind("<Configure>", draw)
    return canvas


def focus_soon(window, widget, delay=40):
    """Forcibly grab keyboard focus for `widget` shortly after `window` is
    mapped. Using focus_force (not just focus_set) matters here: these are
    modal, just-opened dialogs that already own the input grab, so we want
    typing to land in the right field immediately -- no click required."""
    def _do():
        try:
            window.lift()
            window.focus_force()
            widget.focus_force()
        except tk.TclError:
            pass
    window.after(delay, _do)


def make_statusbar(parent):
    frame = tk.Frame(parent, bg=HEADER_BG, bd=1, relief="sunken")
    frame.pack(side="bottom", fill="x")
    label = tk.Label(frame, text="", anchor="w", bg=HEADER_BG,
                      font=UI_FONT(8), padx=6)
    label.pack(side="left", fill="x", expand=True)
    return frame, label


def apply_ttk_theme(root):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "Retro.Treeview",
        background=FIELD_BG, fieldbackground=FIELD_BG, foreground=FIELD_FG,
        # Row height from the data font's real line height, so rows can't
        # overlap however large the display scaling makes the text.
        rowheight=max(26, line_height(DATA_FONT(10)) + px(6)),
        font=DATA_FONT(10), bordercolor=FIELD_BORDER, borderwidth=1,
    )
    style.map("Retro.Treeview",
              background=[("selected", SELECT_BG)],
              foreground=[("selected", SELECT_FG)])
    style.configure(
        "Retro.Treeview.Heading",
        background=HEADER_BG, foreground=TEXT_FG,
        font=UI_FONT(9, "bold"), relief="raised", borderwidth=1,
    )
    style.map("Retro.Treeview.Heading", background=[("active", HEADER_ACTIVE)])

    style.configure("Retro.TCombobox", fieldbackground=FIELD_BG, foreground=FIELD_FG,
                     background=BTN_FACE, arrowsize=px(14))
    style.configure("Retro.Vertical.TScrollbar", background=BTN_FACE,
                     troughcolor=HEADER_BG, bordercolor=BORDER_DARK, arrowsize=px(14))
    if DARK_MODE:
        apply_dark_defaults(root, style)
    return style


def apply_dark_defaults(root, style):
    """Dark colors for everything that doesn't pick them explicitly: plain
    tk widgets (entries, checkboxes, menus) via the option database, ttk
    widgets via the "." style, and Tk's own message boxes and file picker,
    which are built out of both."""
    root.tk_setPalette(
        background=BG_COLOR, foreground=TEXT_FG,
        activeBackground=BTN_ACTIVE, activeForeground=TEXT_FG,
        highlightBackground=BG_COLOR, highlightColor=FIELD_BORDER,
        selectBackground=SELECT_BG, selectForeground=SELECT_FG,
        insertBackground=FIELD_FG, troughColor=HEADER_BG,
        disabledForeground=HINT_FG, selectColor=FIELD_BG,
    )
    for cls in ("Entry", "Text", "Listbox", "Spinbox"):
        root.option_add(f"*{cls}.background", FIELD_BG)
        root.option_add(f"*{cls}.foreground", FIELD_FG)
    root.option_add("*Button.background", BTN_FACE)

    style.configure(".", background=BG_COLOR, foreground=TEXT_FG,
                    fieldbackground=FIELD_BG, insertcolor=FIELD_FG,
                    selectbackground=SELECT_BG, selectforeground=SELECT_FG,
                    troughcolor=HEADER_BG, bordercolor=BORDER_DARK,
                    lightcolor=BTN_FACE, darkcolor=BORDER_DARK)
    style.map(".", background=[("active", BTN_ACTIVE), ("disabled", BG_COLOR)],
              foreground=[("disabled", HINT_FG)])
    style.configure("TButton", background=BTN_FACE)
    style.configure("TEntry", foreground=FIELD_FG)
    style.map("TCombobox", fieldbackground=[("readonly", FIELD_BG)],
              foreground=[("readonly", FIELD_FG)])

    # The file picker's file list is a canvas with a hard-coded white
    # background and black text (Tk's iconlist.tcl), so recolor it - and
    # its text color variable, which Tk reapplies on every selection - each
    # time the picker opens.
    def darken_file_list(event):
        path = str(event.widget)
        root.tk.eval(f"""
            catch {{
                if {{[winfo toplevel {path}] eq "{path}" && [winfo exists {path}.contents.icons]}} {{
                    set ns [info object namespace {path}.contents.icons]
                    set ${{ns}}::fill {FIELD_FG}
                    set cv [set ${{ns}}::canvas]
                    $cv configure -background {FIELD_BG}
                    $cv itemconfigure text -fill {FIELD_FG}
                }}
            }}""")
    root.bind_class("TkFDialog", "<Map>", darken_file_list, add="+")


# --------------------------------------------------------------------------
# Data layer -- no GUI code in here, so it's easy to test on its own.
# --------------------------------------------------------------------------

class VocabStore:
    """Owns one CSV file's worth of Question/Answers/Comment/Instructions
    rows, plus the 'template' defaults used to auto-fill new rows during
    rapid entry."""

    def __init__(self):
        self.filepath = None
        self.rows = []                      # list[dict] each with FIELDNAMES keys
        self.default_instructions = "Type the reading!"

    # -- creation / loading -------------------------------------------------

    def create_new(self, filepath, default_instructions):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.filepath = filepath
        self.rows = []
        self.default_instructions = default_instructions or "Type the reading!"
        with open(self.filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

    def load(self, filepath):
        with open(filepath, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or not set(FIELDNAMES).issubset(set(reader.fieldnames)):
                raise ValueError(
                    "That CSV doesn't have the expected columns:\n"
                    + ", ".join(FIELDNAMES)
                )
            outdated_header = reader.fieldnames != FIELDNAMES
            rows = []
            for raw in reader:
                rows.append({k: (raw.get(k) or "") for k in FIELDNAMES})

        self.filepath = filepath
        self.rows = rows
        if rows:
            self.default_instructions = rows[-1]["Instructions"] or self.default_instructions
        # Older lists carry a now-unused "Render as" column; rewrite them
        # with the current columns so appended rows line up with the header.
        if outdated_header:
            self.save_all()

    # -- writing --------------------------------------------------------

    @staticmethod
    def _normalize(row):
        full_row = {k: row.get(k, "") for k in FIELDNAMES}
        full_row["Answers"] = format_answers(full_row["Answers"])
        return full_row

    def append_row(self, row):
        """Fill in any missing keys, store in memory, and immediately
        append a single line to disk (no full-file rewrite needed)."""
        full_row = self._normalize(row)
        self.rows.append(full_row)
        with open(self.filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow(full_row)
        return full_row

    def update_row(self, index, row):
        full_row = self._normalize(row)
        self.rows[index] = full_row
        self.save_all()

    def delete_row(self, index):
        del self.rows[index]
        self.save_all()

    def save_all(self):
        with open(self.filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(self.rows)


# --------------------------------------------------------------------------
# New File wizard
# --------------------------------------------------------------------------

class NewFileDialog(tk.Toplevel):
    """Y2K wizard-style 'create a new vocab CSV' dialog. Filename, then
    then default Instructions, chained with Enter."""

    def __init__(self, master, on_created):
        super().__init__(master)
        self.on_created = on_created
        self.result = None

        self.title("New Vocabulary List")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        make_banner(self, "Create New Vocabulary List",
                    "Fill in each field and press Enter to continue.")

        body = tk.Frame(self, bg=BG_COLOR, padx=18, pady=14)
        body.pack(fill="both", expand=True)

        make_label(body, "File name:").grid(row=0, column=0, sticky="w", pady=6)
        self.var_filename = tk.StringVar()
        self.entry_filename = make_entry(body, self.var_filename, width=34, font=UI_FONT(10))
        self.entry_filename.grid(row=0, column=1, sticky="we", pady=6)
        make_button(body, "Browse...", self.browse, width=10).grid(row=0, column=2, padx=(8, 0))

        make_label(body, "Default Instructions:").grid(row=1, column=0, sticky="w", pady=6)
        self.var_instructions = tk.StringVar(value="Type the reading!")
        self.entry_instructions = make_entry(body, self.var_instructions, width=34, font=UI_FONT(10))
        self.entry_instructions.grid(row=1, column=1, sticky="we", pady=6)

        hint = ("This applies to every new row automatically (just like\n"
                "in the example file, where it stays the same for the whole\n"
                "list) so rapid entry only ever asks for Question / Answers / Comment.")
        make_label(body, hint, size=8, fg=HINT_FG).grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(4, 10))

        btns = tk.Frame(body, bg=BG_COLOR)
        btns.grid(row=3, column=0, columnspan=3, sticky="e")
        make_button(btns, "Cancel", self.cancel, width=10).pack(side="right", padx=(8, 0))
        make_button(btns, "Create", self.create, width=10, primary=True).pack(side="right")

        body.columnconfigure(1, weight=1)

        # Enter chains through the fields, XP-wizard style.
        self.entry_filename.bind("<Return>", lambda e: self.entry_instructions.focus_set())
        self.entry_instructions.bind("<Return>", lambda e: self.create())
        self.bind("<Escape>", lambda e: self.cancel())

        focus_soon(self, self.entry_filename)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

    def browse(self):
        os.makedirs(DEFAULT_DIR, exist_ok=True)
        path = filedialog.asksaveasfilename(
            parent=self, initialdir=DEFAULT_DIR, defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")], title="Save new list as",
        )
        if path:
            self.var_filename.set(path)
            self.entry_instructions.focus_set()

    def create(self):
        name = self.var_filename.get().strip()
        if not name:
            messagebox.showwarning(APP_TITLE, "Please enter a file name.", parent=self)
            self.entry_filename.focus_set()
            return

        if os.path.dirname(name):
            path = name
        else:
            os.makedirs(DEFAULT_DIR, exist_ok=True)
            path = os.path.join(DEFAULT_DIR, name)
        if not path.lower().endswith(".csv"):
            path += ".csv"

        if os.path.exists(path):
            if not messagebox.askyesno(
                APP_TITLE, f"'{os.path.basename(path)}' already exists.\nOverwrite it?",
                parent=self,
            ):
                return

        self.result = (path, self.var_instructions.get().strip())
        self.destroy()
        self.on_created(self.result)

    def cancel(self):
        self.result = None
        self.destroy()


# --------------------------------------------------------------------------
# Edit single row dialog
# --------------------------------------------------------------------------

class EditRowDialog(tk.Toplevel):
    def __init__(self, master, row_data, on_save, on_batch_add, pinyin_var):
        super().__init__(master)
        self.on_save = on_save
        self.on_batch_add = on_batch_add

        self.title("Edit Entry")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        make_banner(self, "Edit Entry", "Update the fields below, then click Save.")

        body = tk.Frame(self, bg=BG_COLOR, padx=18, pady=14)
        body.pack(fill="both", expand=True)

        self.vars = {}
        widgets = []
        for i, field in enumerate(FIELDNAMES):
            make_label(body, field + ":").grid(row=i, column=0, sticky="w", pady=5)
            var = tk.StringVar(value=row_data.get(field, ""))
            self.vars[field] = var
            font = DATA_FONT(11) if field in ("Question", "Answers", "Comment") else UI_FONT(10)
            w = make_entry(body, var, width=40, font=font)
            if field in ("Question", "Answers", "Comment"):
                bind_pinyin_input(w, var, pinyin_var)
            w.grid(row=i, column=1, sticky="we", pady=5)
            widgets.append(w)
        body.columnconfigure(1, weight=1)
        make_pinyin_toggle(body, pinyin_var).grid(row=len(FIELDNAMES), column=1, sticky="w")

        for i in range(len(widgets) - 1):
            widgets[i].bind("<Return>", lambda e, nxt=widgets[i + 1]: nxt.focus_set())
        widgets[-1].bind("<Return>", lambda e: self.save())

        btns = tk.Frame(body, bg=BG_COLOR)
        btns.grid(row=len(FIELDNAMES) + 1, column=0, columnspan=2, sticky="we", pady=(14, 0))
        make_button(btns, "Batch Add...", self.batch_add).pack(side="left")
        make_button(btns, "Cancel", self.destroy, width=10).pack(side="right", padx=(8, 0))
        make_button(btns, "Save", self.save, width=10, primary=True).pack(side="right")

        self.bind("<Escape>", lambda e: self.destroy())
        focus_soon(self, widgets[0])
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def collect(self):
        return {k: v.get() for k, v in self.vars.items()}

    def save(self):
        self.on_save(self.collect())
        self.destroy()

    def batch_add(self):
        row = self.collect()
        defaults = {"Instructions": row["Instructions"]}
        self.destroy()
        self.on_batch_add(defaults)


# --------------------------------------------------------------------------
# Rapid / batch entry window
# --------------------------------------------------------------------------

class BatchAddWindow(tk.Toplevel):
    """Type Question -> Enter -> Answer -> Enter -> Comment -> Enter and the
    row is saved to disk immediately; focus jumps back to Question so the
    user can keep going without touching the mouse."""

    def __init__(self, master, store: VocabStore, defaults, on_row_added, on_close, pinyin_var):
        super().__init__(master)
        self.store = store
        self.on_row_added = on_row_added
        self.on_close = on_close
        self.session_count = 0

        self.title("Batch Add - Rapid Entry Mode")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        make_banner(
            self, "Batch Add \u2014 Rapid Entry Mode",
            "Type a value and press Enter to move on. Finishing Comment saves the row and starts a new one.",
        )

        # --- template section --------------------------------------------------
        tmpl = tk.LabelFrame(self, text=" Template for new rows ", bg=BG_COLOR,
                              font=UI_FONT(8, "bold"), fg=GROUP_FG, padx=10, pady=8)
        tmpl.pack(fill="x", padx=14, pady=(12, 4))

        make_label(tmpl, "Instructions:").grid(row=0, column=0, sticky="w")
        self.var_tmpl_instr = tk.StringVar(value=defaults.get("Instructions", store.default_instructions))
        e_instr = make_entry(tmpl, self.var_tmpl_instr, width=28, font=UI_FONT(9))
        e_instr.grid(row=0, column=1, sticky="w", padx=(6, 20))

        # Enter in the template field just returns focus to Question --
        # it isn't part of the rapid per-row cycle.
        e_instr.bind("<Return>", lambda e: self.entry_q.focus_set())

        # --- rapid entry fields --------------------------------------------------
        fields = tk.Frame(self, bg=BG_COLOR, padx=14, pady=8)
        fields.pack(fill="x")

        make_label(fields, "Question:", bold=True).grid(row=0, column=0, sticky="w", pady=4)
        self.var_q = tk.StringVar()
        self.entry_q = make_entry(fields, self.var_q, width=44, font=DATA_FONT(13))
        self.entry_q.grid(row=0, column=1, sticky="we", pady=4)

        make_label(fields, "Answer(s):", bold=True).grid(row=1, column=0, sticky="w", pady=4)
        self.var_a = tk.StringVar()
        self.entry_a = make_entry(fields, self.var_a, width=44, font=DATA_FONT(13))
        self.entry_a.grid(row=1, column=1, sticky="we", pady=4)

        make_label(fields, "Comment:", bold=True).grid(row=2, column=0, sticky="w", pady=4)
        self.var_c = tk.StringVar()
        self.entry_c = make_entry(fields, self.var_c, width=44, font=DATA_FONT(13))
        self.entry_c.grid(row=2, column=1, sticky="we", pady=4)
        fields.columnconfigure(1, weight=1)
        make_label(fields, 'Separate multiple answers with commas, e.g. "answer, answer, answer".',
                   size=8, fg=HINT_FG).grid(row=3, column=1, sticky="w")
        make_pinyin_toggle(fields, pinyin_var).grid(row=4, column=1, sticky="w")
        for entry, var in ((self.entry_q, self.var_q), (self.entry_a, self.var_a), (self.entry_c, self.var_c)):
            bind_pinyin_input(entry, var, pinyin_var)

        self.entry_q.bind("<Return>", lambda e: self.entry_a.focus_set())
        self.entry_a.bind("<Return>", lambda e: self.entry_c.focus_set())
        self.entry_c.bind("<Return>", lambda e: self.commit_row())

        # --- status row --------------------------------------------------
        status = tk.Frame(self, bg=BG_COLOR, padx=14)
        status.pack(fill="x")
        self.lbl_count = make_label(status, "Rows added this session: 0", size=9)
        self.lbl_count.pack(side="left")
        self.lbl_saved = make_label(status, "", size=9, fg=GOOD_GREEN)
        self.lbl_saved.pack(side="right")

        # --- recently added preview --------------------------------------------------
        recent_frame = tk.LabelFrame(self, text=" Recently added ", bg=BG_COLOR,
                                      font=UI_FONT(8, "bold"), fg=GROUP_FG)
        recent_frame.pack(fill="both", expand=True, padx=14, pady=(8, 6))

        cols = ("q", "a", "c")
        self.recent_tree = ttk.Treeview(
            recent_frame, columns=cols, show="headings", height=6, style="Retro.Treeview",
        )
        for cid, label, w in (("q", "Question", 140), ("a", "Answers", 140), ("c", "Comment", 220)):
            self.recent_tree.heading(cid, text=label)
            self.recent_tree.column(cid, width=px(w), anchor="w")
        self.recent_tree.pack(fill="both", expand=True, padx=6, pady=6)

        # --- bottom buttons --------------------------------------------------
        bottom = tk.Frame(self, bg=BG_COLOR, padx=14, pady=10)
        bottom.pack(fill="x")
        make_button(bottom, "Save", self.finish, width=12, primary=True).pack(side="right")
        make_label(bottom, "Rows are saved to disk the instant you finish each Comment.",
                   size=8, fg=HINT_FG).pack(side="left")

        self.bind("<Escape>", lambda e: self.finish())
        self.protocol("WM_DELETE_WINDOW", self.finish)
        focus_soon(self, self.entry_q)

    def commit_row(self):
        q = self.var_q.get().strip()
        a = self.var_a.get().strip()
        c = self.var_c.get().strip()

        if not (q or a or c):
            # Nothing typed -- probably an accidental extra Enter. Don't
            # save a blank row, just keep the flow going.
            self.entry_q.focus_set()
            return

        row = {
            "Question": q,
            "Answers": a,
            "Comment": c,
            "Instructions": self.var_tmpl_instr.get().strip(),
        }
        row = self.store.append_row(row)
        self.store.default_instructions = row["Instructions"] or self.store.default_instructions

        self.session_count += 1
        self.lbl_count.config(text=f"Rows added this session: {self.session_count}")

        self.recent_tree.insert("", "end", values=(row["Question"], row["Answers"], row["Comment"]))
        children = self.recent_tree.get_children()
        if len(children) > 8:
            self.recent_tree.delete(children[0])
        self.recent_tree.yview_moveto(1.0)

        self.on_row_added()
        self.flash_saved()

        self.var_q.set("")
        self.var_a.set("")
        self.var_c.set("")
        self.entry_q.focus_set()

    def flash_saved(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.lbl_saved.config(text=f"\u2713 Saved to disk at {now}")

    def finish(self):
        self.on_close()
        self.destroy()


# --------------------------------------------------------------------------
# Main application
# --------------------------------------------------------------------------

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.configure(bg=BG_COLOR)

        resolve_fonts()
        compute_ui_scale()
        apply_ttk_theme(root)
        self._fit_window(920, 600, 700, 420)

        self.store = VocabStore()
        self.current_frame = None
        self.tree = None
        self.status_label = None
        self.menubar = None
        # Shared by every entry window so the choice sticks for the session.
        self.pinyin_var = tk.BooleanVar(value=keisetsu_language() == "Chinese")

        self.show_launcher()

    def _fit_window(self, w, h, min_w, min_h):
        """Opens at the design size scaled for this display, but never
        larger than 90% of the screen, and centered on it."""
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = min(px(w), int(sw * 0.9)), min(px(h), int(sh * 0.85))
        self.root.minsize(min(px(min_w), w), min(px(min_h), h))
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 3}")

    # -- frame management --------------------------------------------------

    def _clear(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.root.config(menu=tk.Menu(self.root))  # clear any menu

    # -- launcher --------------------------------------------------

    def show_launcher(self):
        self._clear()
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

        make_banner(frame, "Vocab List Manager", "Build and edit Question / Answer / Comment vocab lists.")

        body = tk.Frame(frame, bg=BG_COLOR)
        body.pack(fill="both", expand=True)

        center = tk.Frame(body, bg=BG_COLOR)
        center.place(relx=0.5, rely=0.46, anchor="center")

        make_label(center, "What would you like to do?", size=11, bold=True).pack(pady=(0, 18))

        row = tk.Frame(center, bg=BG_COLOR)
        row.pack()

        new_btn = tk.Button(
            row, text="New", command=self.action_new, font=UI_FONT(12, "bold"),
            bg=BTN_FACE, activebackground=BTN_ACTIVE, relief="raised", bd=3,
            width=14, height=4, cursor="hand2",
        )
        new_btn.grid(row=0, column=0, padx=14)

        edit_btn = tk.Button(
            row, text="Edit", command=self.action_edit, font=UI_FONT(12, "bold"),
            bg=BTN_FACE, activebackground=BTN_ACTIVE, relief="raised", bd=3,
            width=14, height=4, cursor="hand2",
        )
        edit_btn.grid(row=0, column=1, padx=14)

        make_label(center, "New starts a fresh CSV. Edit opens one you already made.",
                   size=8, fg=HINT_FG).pack(pady=(16, 0))

        _, self.status_label = make_statusbar(frame)
        self.status_label.config(text="Ready.")

    # -- actions --------------------------------------------------

    def action_new(self):
        NewFileDialog(self.root, on_created=self._on_new_file_created)

    def _on_new_file_created(self, result):
        path, instructions = result
        self.store.create_new(path, instructions)
        self.show_spreadsheet()
        # Jump straight into rapid entry so the list actually gets "started".
        self.open_batch_window()

    def action_edit(self):
        os.makedirs(DEFAULT_DIR, exist_ok=True)
        path = filedialog.askopenfilename(
            initialdir=DEFAULT_DIR, title="Open vocabulary list",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            self.store.load(path)
        except Exception as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        self.show_spreadsheet()

    # -- spreadsheet view --------------------------------------------------

    def show_spreadsheet(self):
        self._clear()
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

        self._build_menu()

        toolbar = tk.Frame(frame, bg=BG_COLOR, padx=px(8), pady=px(6))
        toolbar.pack(fill="x")
        gap = (px(8), 0)
        make_button(toolbar, "Batch Add...", self.open_batch_window).pack(side="left")
        make_button(toolbar, "New File...", self.action_new).pack(side="left", padx=gap)
        make_button(toolbar, "Open File...", self.action_edit).pack(side="left", padx=gap)
        make_button(toolbar, "Delete", self.delete_selected_row).pack(side="left", padx=gap)
        make_button(toolbar, "Start Menu", self.show_launcher).pack(side="left", padx=gap)

        # The pinyin toggle and hint get their own row, so a large display
        # scale doesn't push them off the end of the button row.
        hints = tk.Frame(frame, bg=BG_COLOR, padx=px(8))
        hints.pack(fill="x", pady=(0, px(4)))
        make_pinyin_toggle(hints, self.pinyin_var).pack(side="left")
        make_label(hints, "Double-click a row to edit it. Click a row, then Delete to remove it.",
                   size=8, fg=HINT_FG).pack(side="right")

        table_frame = tk.Frame(frame, bg=BG_COLOR, padx=px(8))
        table_frame.pack(fill="both", expand=True)

        cols = ("idx",) + tuple(FIELDNAMES)
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                 style="Retro.Treeview", selectmode="browse")
        widths = {"Question": 160, "Answers": 160, "Comment": 220, "Instructions": 140}
        headers = {"idx": "#"}
        for c in cols:
            self.tree.heading(c, text=headers.get(c, c))
            self.tree.column(c, width=px(widths.get(c, 120)), anchor="w")
        # Wide enough for a 4-digit row number in the data font.
        idx_w = tkfont.Font(font=DATA_FONT(10)).measure("0000") + px(12)
        self.tree.column("idx", width=idx_w, minwidth=idx_w, anchor="center", stretch=False)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview,
                             style="Retro.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.tag_configure("odd", background=FIELD_BG)
        self.tree.tag_configure("even", background=STRIPE_BG)

        self.tree.bind("<Double-1>", self.on_row_double_click)
        self.tree.bind("<Delete>", lambda e: self.delete_selected_row())

        _, self.status_label = make_statusbar(frame)
        self.refresh_treeview()

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New...", command=self.action_new, accelerator="Ctrl+N")
        filemenu.add_command(label="Open...", command=self.action_edit, accelerator="Ctrl+O")
        filemenu.add_separator()
        filemenu.add_command(label="Batch Add...", command=self.open_batch_window, accelerator="Ctrl+B")
        filemenu.add_command(label="Delete Row...", command=self.delete_selected_row, accelerator="Del")
        filemenu.add_separator()
        filemenu.add_command(label="Start Menu", command=self.show_launcher)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

        self.root.bind("<Control-n>", lambda e: self.action_new())
        self.root.bind("<Control-o>", lambda e: self.action_edit())
        self.root.bind("<Control-b>", lambda e: self.open_batch_window())

    def refresh_treeview(self, select=None):
        """Reloads the table. Scrolls to the last row (where Batch Add puts
        new ones), or, with `select`, highlights and shows that row."""
        if self.tree is None:
            return
        self.tree.delete(*self.tree.get_children())
        for i, row in enumerate(self.store.rows):
            tag = "even" if i % 2 else "odd"
            values = (i + 1,) + tuple(row.get(f, "") for f in FIELDNAMES)
            self.tree.insert("", "end", iid=str(i), values=values, tags=(tag,))
        children = self.tree.get_children()
        if select is not None and children:
            iid = str(min(select, len(children) - 1))
            self.tree.selection_set(iid)
            self.tree.focus(iid)
            self.tree.see(iid)
        elif children:
            self.tree.see(children[-1])
        if self.status_label is not None:
            name = os.path.basename(self.store.filepath) if self.store.filepath else "(no file)"
            self.status_label.config(
                text=f"{name}  \u2014  {len(self.store.rows)} row(s)  \u2014  {self.store.filepath or ''}"
            )

    def on_row_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        index = int(item_id)
        row_data = self.store.rows[index]
        EditRowDialog(
            self.root, row_data,
            on_save=lambda new_row, i=index: self._on_row_saved(i, new_row),
            on_batch_add=self.open_batch_window,
            pinyin_var=self.pinyin_var,
        )

    def _on_row_saved(self, index, new_row):
        self.store.update_row(index, new_row)
        self.refresh_treeview(select=index)

    def delete_selected_row(self):
        if self.tree is None or self.store.filepath is None:
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo(APP_TITLE, "Click a row to highlight it first, then click Delete.",
                                parent=self.root)
            return
        index = int(selected[0])
        row = self.store.rows[index]
        preview = f"#{index + 1}:  {row['Question'] or '(blank)'}"
        if row["Answers"]:
            preview += f"  →  {row['Answers']}"
        if not messagebox.askyesno(
            "Delete Row",
            f"Delete this row?\n\n{preview}\n\nThis can't be undone.",
            icon="warning", default="no", parent=self.root,
        ):
            return
        self.store.delete_row(index)
        # Highlight the row that took its place, so several rows can be
        # removed one after another without scrolling back to find them.
        self.refresh_treeview(select=index if self.store.rows else None)
        if self.status_label is not None:
            self.status_label.config(
                text=f"Deleted row #{index + 1}.  {len(self.store.rows)} row(s) left.")

    def open_batch_window(self, defaults=None):
        if self.store.filepath is None:
            messagebox.showinfo(APP_TITLE, "Create or open a list first.")
            return
        if defaults is None:
            defaults = {"Instructions": self.store.default_instructions}
        BatchAddWindow(
            self.root, self.store, defaults,
            on_row_added=self.refresh_treeview,
            on_close=self.refresh_treeview,
            pinyin_var=self.pinyin_var,
        )


def main():
    os.makedirs(DEFAULT_DIR, exist_ok=True)
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
