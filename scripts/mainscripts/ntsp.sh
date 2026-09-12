#!/bin/bash
# scripts/mainscripts/ntsp.sh
# Downloads videos from a channel handle or full URL (nts playlist variant) via yt-dlp.
# Usage: ntsp.sh <channel or URL> <y/n>  (y = use random cookies_1/2/3.txt, n = ghost mode)

# Hardening: undefined variables and broken pipes do not pass silently
set -uo pipefail

# Loads the project shared functions
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"

# --- ARGUMENT VALIDATION ---
if [ -z "${1:-}" ] || [ -z "${2:-}" ]; then
    echo "Error: insufficient arguments."
    echo "Correct usage: ntsp.sh <channel or URL> <y/n>"
    echo "  y = use cookies (random account between 1, 2 and 3)"
    echo "  n = do not count view (videos are not marked as watched)"
    echo "Example: ntsp.sh LofiGirl y"
    exit 1
fi

# Assign arguments to variables
CHANNEL_AT="$1"
CHOOSE_COOKIES="$2"

echo "=================================================="
echo " VONVAKVA'S ARCHIVE - Channel download (ntsp)"
echo " Channel/URL: $CHANNEL_AT"
echo "=================================================="

# --- COOKIE SELECTION ---
EXTRA_FLAGS=""

if [ "$CHOOSE_COOKIES" = "y" ]; then
    # Draws a number from 1 to 3 to select which account will be used
    ACCOUNT=$((1 + RANDOM % 3))
    case $ACCOUNT in
      1)
        echo " [ACCOUNT 1]: using cookies_1.txt"
        EXTRA_FLAGS="--cookies $(config_path cookies_1.txt)"
        ;;
      2)
        echo " [ACCOUNT 2]: using cookies_2.txt"
        EXTRA_FLAGS="--cookies $(config_path cookies_2.txt)"
        ;;
      3)
        echo " [ACCOUNT 3]: using cookies_3.txt"
        EXTRA_FLAGS="--cookies $(config_path cookies_3.txt)"
        ;;
    esac
else
    echo " [DO NOT COUNT VIEW]: videos will not be marked as watched"
    EXTRA_FLAGS="--no-mark-watched"
fi

echo "=================================================="

# --- ENGINE EXECUTION ---
yt-dlp -f "bv*[height<=720][vcodec^=av01]+ba/bv*[height<=720]+ba/best" \
--merge-output-format mp4 \
--write-thumbnail \
--embed-thumbnail \
--write-description \
--write-info-json \
--embed-metadata \
--yes-playlist \
--continue \
--download-archive "$(config_path archive.txt)" \
--concurrent-fragments 4 \
--js-runtime node \
--restrict-filenames \
$EXTRA_FLAGS \
-o "%(uploader)s/%(upload_date)s - %(title).150s [%(id)s].%(ext)s" \
"$CHANNEL_AT"

echo "=================================================="
echo " Download finished for $CHANNEL_AT."
echo "=================================================="
