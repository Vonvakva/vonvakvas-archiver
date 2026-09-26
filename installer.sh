#!/usr/bin/env bash
# installer.sh - Vonvakva's Archive installer
#
# Installs the project into a user applications folder, creates the
# Python environment with all dependencies, generates an initial empty
# configuration (cookies, channel list, telegram) and registers a
# shortcut in the applications menu.
#
# Usage:
#   ./installer.sh                    -> installs into ~/.local/opt/vonvakvas-archive
#   ./installer.sh /path/destination  -> installs into the given directory
#
# Optional environment variables:
#   INSTALLER_SKIP_PIP=1  does not create the venv nor install dependencies (for testing)
#
# Also creates ~/.local/bin/vonvakvas so the CLI can be run from any directory.

set -euo pipefail

APP_NAME="vonvakvas-archive"
DEFAULT_DIR="$HOME/.local/opt/$APP_NAME"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${1:-$DEFAULT_DIR}"

log()  { printf '[installer] %s\n' "$*"; }
warn() { printf '[installer] WARNING: %s\n' "$*"; }
die()  { printf '[installer] ERROR: %s\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Initial checks
# ---------------------------------------------------------------------------
[ "$(id -u)" -eq 0 ] && die "Do not run the installer as root (installation is per-user)."

command -v bash    >/dev/null 2>&1 || die "bash not found."
command -v python3 >/dev/null 2>&1 || die "python3 not found (Python 3.10 or higher required)."

command -v ffmpeg >/dev/null 2>&1 || warn "ffmpeg missing - required to merge video and audio. Install it via the package manager."
command -v node   >/dev/null 2>&1 || warn "node missing - recommended by yt-dlp. Install it via the package manager."
command -v curl   >/dev/null 2>&1 || warn "curl missing - required by the channel monitor (check)."

log "Source directory: $SRC_DIR"
log "Destination directory: $INSTALL_DIR"

# ---------------------------------------------------------------------------
# Program files copy
# ---------------------------------------------------------------------------
mkdir -p "$INSTALL_DIR"

log "Copying program files..."
cp -r "$SRC_DIR/api"     "$INSTALL_DIR/"
cp -r "$SRC_DIR/scripts" "$INSTALL_DIR/"
cp -r "$SRC_DIR/gui"     "$INSTALL_DIR/"
if [ -d "$SRC_DIR/errors-exp" ]; then
    cp -r "$SRC_DIR/errors-exp" "$INSTALL_DIR/"
fi
for f in .projectroot vonvakvas.sh start-gui.sh requirements.txt; do
    [ -f "$SRC_DIR/$f" ] && cp "$SRC_DIR/$f" "$INSTALL_DIR/"
done

# Clears caches and ensures execution permissions
find "$INSTALL_DIR" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
chmod +x "$INSTALL_DIR/vonvakvas.sh" "$INSTALL_DIR/start-gui.sh" 2>/dev/null || true
find "$INSTALL_DIR/scripts" -name '*.sh' -exec chmod +x {} +

mkdir -p "$INSTALL_DIR/your-directory"

# ---------------------------------------------------------------------------
# Initial configuration (does not overwrite a previous installation)
# ---------------------------------------------------------------------------
CFG="$INSTALL_DIR/config"
mkdir -p "$CFG"

copy_if_exists() { # copy_if_exists <source> <destination>
    if [ -f "$1" ] && [ ! -f "$2" ]; then
        cp "$1" "$2"
    fi
}

log "Creating initial configuration..."
# Canonical file names (English). Legacy Portuguese names (in this repo or
# from a previous install) are migrated automatically below.
for f in succeeded_archvings.txt; do
    if [ ! -f "$CFG/$f" ]; then
        : > "$CFG/$f"
    fi
done

# archive.txt: created empty (no download history)
if [ ! -f "$CFG/archive.txt" ]; then
    : > "$CFG/archive.txt"
fi

if [ ! -f "$CFG/channel_list.txt" ]; then
    printf '# Lines starting with # are ignored\n' > "$CFG/channel_list.txt"
else
    copy_if_exists "$SRC_DIR/config/channel_list.txt" "$CFG/channel_list.txt"
fi
# Legacy migration: old Portuguese names -> canonical English names
if [ ! -f "$CFG/channel_list.txt" ] && [ -f "$CFG/lista_canais.txt" ]; then
    cp "$CFG/lista_canais.txt" "$CFG/channel_list.txt"
fi
if [ ! -f "$CFG/succeeded_archvings.txt" ] && [ -f "$CFG/archivamentos_bem_sucedidos.txt" ]; then
    cp "$CFG/archivamentos_bem_sucedidos.txt" "$CFG/succeeded_archvings.txt"
fi
copy_if_exists "$SRC_DIR/config/lista_canais.txt" "$CFG/channel_list.txt"

# Cookies for accounts 1, 2 and 3: created empty for the user to fill in.
# Old names (alfa/beta/gama) are migrated automatically.
for n in 1 2 3; do
    [ -f "$CFG/cookies_$n.txt" ] || : > "$CFG/cookies_$n.txt"
done
copy_if_exists "$SRC_DIR/config/cookies_1.txt" "$CFG/cookies_1.txt"
copy_if_exists "$SRC_DIR/config/cookies_2.txt" "$CFG/cookies_2.txt"
copy_if_exists "$SRC_DIR/config/cookies_3.txt" "$CFG/cookies_3.txt"
copy_if_exists "$SRC_DIR/config/cookies_alfa.txt" "$CFG/cookies_1.txt"
copy_if_exists "$SRC_DIR/config/cookies_beta.txt" "$CFG/cookies_2.txt"
copy_if_exists "$SRC_DIR/config/cookies_gama.txt" "$CFG/cookies_3.txt"

if [ ! -f "$CFG/telegram.env" ]; then
    copy_if_exists "$SRC_DIR/config/telegram.env" "$CFG/telegram.env"
    if [ ! -f "$CFG/telegram.env" ]; then
        cp "$CFG/telegram.env.example" "$CFG/telegram.env" 2>/dev/null || \
            cp "$SRC_DIR/config/telegram.env.example" "$CFG/telegram.env"
    fi
fi
[ -f "$CFG/telegram.env.example" ] || cp "$SRC_DIR/config/telegram.env.example" "$CFG/telegram.env.example"

if [ ! -f "$CFG/settings.env" ]; then
    cat > "$CFG/settings.env" <<'EOF'
# Vonvakva's Archive - local settings
# Folder where the channels are stored (can be an external drive).
# If <folder>/config/ exists, the files there take priority
# (per-file fallback to the project config/).
# Leave empty to use your-directory/ inside the project.
# Example:
# CHANNELS_ROOT="/run/media/user/MyDrive/vonvakvas"
CHANNELS_ROOT=""
EOF
fi

chmod 600 "$CFG"/cookies_*.txt "$CFG/telegram.env" 2>/dev/null || true

# ---------------------------------------------------------------------------
# Python environment (venv) and dependencies
# ---------------------------------------------------------------------------
VENV_DIR="$INSTALL_DIR/venv"

if [ "${INSTALLER_SKIP_PIP:-0}" = "1" ]; then
    warn "INSTALLER_SKIP_PIP=1: venv creation and dependency installation skipped."
elif [ ! -x "$VENV_DIR/bin/python" ]; then
    log "Creating Python environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    log "Installing dependencies (PySide6, psutil, yt-dlp, internetarchive)..."
    "$VENV_DIR/bin/pip" install --upgrade pip >/dev/null
    "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    log "Dependencies installed (yt-dlp and ia included in the venv)."
else
    log "Python environment already exists in $VENV_DIR (kept)."
fi

# ---------------------------------------------------------------------------
# CLI launcher
# ---------------------------------------------------------------------------
# The wrapper points to this installation, including when a custom destination
# was supplied. An existing command is never overwritten without consent.
BIN_DIR="${HOME}/.local/bin"
BIN_FILE="$BIN_DIR/vonvakvas"
mkdir -p "$BIN_DIR"

if [[ -e "$BIN_FILE" || -L "$BIN_FILE" ]]; then
    warn "CLI launcher already exists at $BIN_FILE; it was not changed."
else
    printf '#!/usr/bin/env bash\nset -e\nexec %q "$@"\n' "$INSTALL_DIR/vonvakvas.sh" > "$BIN_FILE"
    chmod 755 "$BIN_FILE"
    log "CLI launcher created: $BIN_FILE"
fi

case ":${PATH}:" in
    *":${BIN_DIR}:"*) ;;
    *) warn "Add $BIN_DIR to your PATH to run 'vonvakvas' from any directory." ;;
esac

# ---------------------------------------------------------------------------
# Applications menu shortcut
# ---------------------------------------------------------------------------
DESKTOP_DIR="${HOME}/.local/share/applications"
mkdir -p "$DESKTOP_DIR"
cat > "$DESKTOP_DIR/$APP_NAME.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Vonvakva's Archive
Comment=YouTube channel archiving system
Exec=$INSTALL_DIR/start-gui.sh
Icon=applications-internet
Terminal=false
Categories=Network;AudioVideo;Utility;
EOF

log "Installation finished in: $INSTALL_DIR"
log "Shortcut created: $DESKTOP_DIR/$APP_NAME.desktop"
log ""
log "Next steps:"
log "  1. Fill in the cookies in: $CFG/cookies_1.txt, cookies_2.txt and cookies_3.txt"
log "     (export the YouTube cookies in Netscape format)"
log "  2. Edit the channel list: $CFG/channel_list.txt"
log "  3. Set up Telegram (optional): $CFG/telegram.env"
log "  4. Start from the applications menu or run: $INSTALL_DIR/start-gui.sh"
log "  5. From any directory, run: vonvakvas help (if $BIN_DIR is in PATH)"
