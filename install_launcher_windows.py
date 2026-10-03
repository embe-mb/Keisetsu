"""Creates a "Keisetsu" shortcut on the Windows desktop, so Keisetsu can be
started with a double-click instead of from a terminal.

Run it with the Python that has pandas and Pillow installed:

    python install_launcher_windows.py

The shortcut starts keisetsu.py with pythonw.exe (Python without a console
window), from this folder. Its icon is keisetsu.ico, made here from icon.png,
or logo.png if there's no icon.png. Rerun this after changing icon.png,
moving the Keisetsu folder or reinstalling Python: it rewrites the shortcut
with the current paths.
"""
import os
import subprocess
import sys

from PIL import Image

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ICO_PATH = os.path.join(APP_DIR, "keisetsu.ico")
ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def make_icon():
    """Converts icon.png (or logo.png) to keisetsu.ico. Returns its path, or
    None if neither PNG exists."""
    for name in ("icon.png", "logo.png"):
        src = os.path.join(APP_DIR, name)
        if os.path.exists(src):
            break
    else:
        return None
    img = Image.open(src).convert("RGBA")
    # Icons are square: center the image on a transparent square.
    side = max(img.size)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.paste(img, ((side - img.width) // 2, (side - img.height) // 2))
    square.save(ICO_PATH, sizes=ICO_SIZES)
    return ICO_PATH


def pythonw_path():
    """pythonw.exe next to the running Python, so Keisetsu starts without
    a console window. Falls back to the running Python itself."""
    candidate = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    return candidate if os.path.exists(candidate) else sys.executable


def ps_quote(text):
    return "'" + text.replace("'", "''") + "'"


def main():
    if sys.platform != "win32":
        sys.exit("This installer is for Windows. On Linux, run install_launcher.sh.")

    icon = make_icon()
    # WScript.Shell creates .lnk shortcuts. The desktop path is asked from
    # Windows, since it may be redirected (e.g. into OneDrive).
    script = "\n".join([
        "$desktop = [Environment]::GetFolderPath('Desktop')",
        "$lnk = Join-Path $desktop 'Keisetsu.lnk'",
        "$s = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk)",
        f"$s.TargetPath = {ps_quote(pythonw_path())}",
        f"$s.Arguments = {ps_quote(chr(34) + os.path.join(APP_DIR, 'keisetsu.py') + chr(34))}",
        f"$s.WorkingDirectory = {ps_quote(APP_DIR)}",
        "$s.Description = 'Keisetsu - flashcards for Japanese and Chinese vocabulary'",
        f"$s.IconLocation = {ps_quote((icon or pythonw_path()) + ',0')}",
        "$s.Save()",
        "Write-Output $lnk",
    ])
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit("Couldn't create the shortcut:\n" + result.stderr.strip())
    print(f"Created {result.stdout.strip()} (icon: {icon or 'Python default'})")


if __name__ == "__main__":
    main()
