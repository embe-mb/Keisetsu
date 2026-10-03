"""Prints the release notes for a version tag (e.g. v1.11.1), used by
.github/workflows/release.yml. Fails if the tag doesn't match
BUILD_VERSION in keisetsu.py or the Build Log has no entry for it."""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEADER = """\
## Download

**Windows:** download **Keisetsu-Windows.zip** below, unzip it, and double-click `Keisetsu.exe` inside the `Keisetsu` folder. You don't need Python. If Windows says "Windows protected your PC", click **More info**, then **Run anyway**.

**Linux and macOS:** download the source code below and follow the steps in the [README](https://github.com/embe-mb/Keisetsu#linux).

## What's new
"""


def main():
    version = sys.argv[1].lstrip("v")

    with open(os.path.join(ROOT, "keisetsu.py"), encoding="utf-8") as f:
        match = re.search(r'^BUILD_VERSION = "Build ([^"]+)"', f.read(), re.M)
    if not match or match.group(1) != version:
        sys.exit(f"Tag v{version} doesn't match BUILD_VERSION "
                 f"({match.group(1) if match else 'not found'}) in keisetsu.py.")

    with open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8") as f:
        log = f.read()
    entry = re.search(rf"^### Build {re.escape(version)} .*?\n(.*?)(?=^### |\Z)", log, re.M | re.S)
    if not entry:
        sys.exit(f"No Build {version} entry in the CLAUDE.md Build Log.")

    sys.stdout.reconfigure(encoding="utf-8")
    print(HEADER)
    print(entry.group(1).strip())


if __name__ == "__main__":
    main()
