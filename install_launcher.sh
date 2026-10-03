#!/usr/bin/env bash
# Installs a Keisetsu launcher into the desktop menu so it can be pinned to
# the panel (e.g. Linux Mint's Cinnamon panel). Re-run this after adding
# icon.png or moving the Keisetsu folder - it rewrites the launcher with the
# current paths.
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/.local/share/applications/keisetsu.desktop"

ICON="$APP_DIR/icon.png"
[ -f "$ICON" ] || ICON="$APP_DIR/logo.png"

mkdir -p "$(dirname "$DEST")"
cat > "$DEST" <<EOF
[Desktop Entry]
Type=Application
Name=Keisetsu
GenericName=Flashcard Study App
Comment=Diligent studying for Japanese and Chinese vocabulary
Exec=/usr/bin/env python3 "$APP_DIR/keisetsu.py"
Path=$APP_DIR
Icon=$ICON
Terminal=false
Categories=Education;Languages;
StartupWMClass=Keisetsu
StartupNotify=true
EOF
chmod +x "$DEST"
update-desktop-database "$(dirname "$DEST")" 2>/dev/null || true

echo "Installed $DEST (icon: $ICON)"
