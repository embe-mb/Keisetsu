"""Builds the Windows version of Keisetsu with PyInstaller.

Run it with the Python that has pandas, Pillow and PyInstaller installed
(pip install pyinstaller):

    python build_windows.py

The result is dist/Keisetsu/ (Keisetsu.exe plus its _internal/ folder,
the sample deck and theme, and the images) and dist/Keisetsu-Windows.zip,
which is what users download. The CSV Manager is built into Keisetsu.exe.
keisetsu_settings.json is left out, so every download starts with the
default settings.
"""

import os
import shutil
import subprocess
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(APP_DIR, "dist")
BUILD_DIR = os.path.join(APP_DIR, "build")
OUT_DIR = os.path.join(DIST_DIR, "Keisetsu")
ICON_SOURCES = ("icon.png", "logo.png")
ICON_FILE = os.path.join(BUILD_DIR, "keisetsu.ico")
# Copied next to Keisetsu.exe, where the app looks for them. Only the
# sample deck and sample theme ship; the rest of vocab_lists/ and themes/
# are personal. Themes ship their .png files only (no .psd sources).
EXTRA_FILES = ("icon.png", "logo.png")
SAMPLE_DECKS = ("Select this deck to test the program!.csv",)
SAMPLE_THEMES = ("mb",)
# Optional pandas helpers Keisetsu never uses (it only reads plain CSVs).
# Leaving them out cuts about 100 MB from the download.
EXCLUDED_MODULES = ("pyarrow", "cryptography", "lxml", "zstandard")


def make_icon():
    """Makes the .exe icon from icon.png (or logo.png). Returns its path,
    or None if neither image exists."""
    from PIL import Image
    for name in ICON_SOURCES:
        src = os.path.join(APP_DIR, name)
        if os.path.exists(src):
            os.makedirs(BUILD_DIR, exist_ok=True)
            img = Image.open(src).convert("RGBA")
            img.save(ICON_FILE, sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)])
            return ICON_FILE
    return None


def main():
    shutil.rmtree(OUT_DIR, ignore_errors=True)
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--onedir",
        "--windowed",                         # no console window
        "--name", "Keisetsu",
        "--hidden-import", "vocab_manager",   # the built-in CSV Manager
        "--distpath", DIST_DIR,
        "--workpath", BUILD_DIR,
        "--specpath", BUILD_DIR,
    ]
    for module in EXCLUDED_MODULES:
        cmd += ["--exclude-module", module]
    icon = make_icon()
    if icon:
        cmd += ["--icon", icon]
    cmd.append(os.path.join(APP_DIR, "keisetsu.py"))

    print("Running PyInstaller...")
    subprocess.run(cmd, check=True, cwd=APP_DIR)

    decks_dir = os.path.join(OUT_DIR, "vocab_lists")
    os.makedirs(decks_dir)
    for name in SAMPLE_DECKS:
        shutil.copy2(os.path.join(APP_DIR, "vocab_lists", name), decks_dir)
    for theme in SAMPLE_THEMES:
        src = os.path.join(APP_DIR, "themes", theme)
        dst = os.path.join(OUT_DIR, "themes", theme)
        os.makedirs(dst)
        for name in os.listdir(src):
            if name.lower().endswith(".png"):
                shutil.copy2(os.path.join(src, name), dst)
    for name in EXTRA_FILES:
        src = os.path.join(APP_DIR, name)
        if os.path.exists(src):
            shutil.copy2(src, OUT_DIR)

    zip_base = os.path.join(DIST_DIR, "Keisetsu-Windows")
    archive = shutil.make_archive(zip_base, "zip", DIST_DIR, "Keisetsu")
    print(f"\nDone.\n  Folder: {OUT_DIR}\n  Zip:    {archive}")


if __name__ == "__main__":
    main()
