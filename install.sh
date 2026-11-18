#!/usr/bin/env bash
# Adds "Zelda 100% Tracker" to your app launcher (per-user, no root needed).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
apps="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
icons="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/scalable/apps"
mkdir -p "$apps" "$icons" "$HOME/.local/bin"

chmod +x "$here/zelda_tracker.py"
ln -sf "$here/zelda_tracker.py" "$HOME/.local/bin/zelda-tracker"
cp "$here/io.github.zelda_tracker.svg" "$icons/"

# Your own icon wins if you've put one at icons/app.png (git ignores the icons/ folder).
icon="io.github.zelda_tracker"
if [ -f "$here/icons/app.png" ]; then
    icon="$here/icons/app.png"
fi

cat > "$apps/io.github.zelda_tracker.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Zelda 100% Tracker
Comment=Track your progress toward 100% in the Zelda games
Exec=python3 "$here/zelda_tracker.py" %f
Icon=$icon
Terminal=false
Categories=Game;
Keywords=zelda;ocarina;majora;awakening;oracle;minish;twilight;heart;3ds;gba;snes;gamecube;save;
StartupWMClass=io.github.zelda_tracker
EOF

command -v update-desktop-database >/dev/null && update-desktop-database "$apps" || true
command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -q "${icons%/scalable/apps}" 2>/dev/null || true
echo "Installed. Launch 'Zelda 100% Tracker' from your app launcher, or run: zelda-tracker"
