#!/bin/bash
# scripts/masses/mass_organizer.sh
# Bulk organize: runs organizer.sh inside every channel folder (respects .dirignore).

# Hardening: undefined variables and broken pipes do not pass silently
set -uo pipefail

# Loads the project shared functions
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"

ORGANIZER_SCRIPT="$(script_path organizers/organizer.sh)"
IGNORE_FILE=".dirignore"

if [ ! -x "$ORGANIZER_SCRIPT" ]; then
    echo "Error: the organizer script was not found or is not executable at: $ORGANIZER_SCRIPT"
    exit 1
fi

echo "=== VONVAKVA'S ARCHIVE: BULK ORGANIZE ==="
echo "=========================================================="

for item in */; do
    item="${item%/}"

    # Checks if the folder is listed in .dirignore (skipping # lines and blanks)
    if [ -f "$IGNORE_FILE" ]; then
        if sed 's/#.*//' "$IGNORE_FILE" | grep -qxF "$item"; then
            echo " [SKIPPING]: '$item' (listed in $IGNORE_FILE)"
            echo "----------------------------------------------------------"
            continue
        fi
    fi

    echo ">>> ENTERING FOLDER: $item"
    echo "----------------------------------------------------------"

    (
        cd "$item" || exit
        bash "$ORGANIZER_SCRIPT"
    )

    echo "----------------------------------------------------------"
    echo ">>> DONE FOR: $item"
    echo "=========================================================="
    sleep 1
done

echo " [DONE] All folders were processed."
