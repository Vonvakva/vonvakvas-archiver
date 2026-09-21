#!/bin/bash
# mass_ntsn.sh - Bulk download of the channels in the list, full variant (ntsn.sh).
# Same as mass_nts.sh but calls mainscripts/ntsn.sh: Windows-safe original
# filenames + manual subtitles + comments (no auto-subs).

# Hardening: undefined variables and broken pipes do not pass silently
set -uo pipefail

# Loads the project shared functions
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"

LIST="$(config_path channel_list.txt)"

if [ ! -f "$LIST" ]; then
    echo "Error: create the file $LIST with the channel @handles (one per line)."
    exit 1
fi

# Asks once so the same rule is applied to the whole batch
echo "=== VONVAKVA'S ARCHIVE: BULK DOWNLOAD (NAMES) ==="
read -p "Use cookies (random account between 1, 2 and 3) for the whole batch? (y/n): " ANSWER

if [ "$ANSWER" != "y" ] && [ "$ANSWER" != "n" ]; then
    echo "Invalid option. Aborting."
    exit 1
fi

echo "Starting bulk update (full variant: original names + subs + comments)..."
echo "=================================================="

# Reads the file line by line, skipping empty lines and comments
while IFS= read -r channel || [ -n "$channel" ]; do
    # Skips lines starting with # or blank ones
    if [[ "$channel" =~ ^# ]] || [ -z "$channel" ]; then
        continue
    fi

    echo ">>> Next in queue: @$channel"

    # Calls the full-variant script passing the channel and the mask choice
    bash "$(script_path mainscripts/ntsn.sh)" "$channel" "$ANSWER"

    echo ">>> Waiting a random interval before the next download..."

    # --- RANDOM SLEEP LOGIC ---
    # Draws a minimum time between 2 and 4 seconds
    SLEEP_MIN=$((2 + RANDOM % 3))
    # Draws a maximum time between 6 and 10 seconds
    SLEEP_MAX=$((6 + RANDOM % 5))
    # Final sleep = random value between MIN and MAX
    SLEEP_TIME=$((SLEEP_MIN + RANDOM % (SLEEP_MAX - SLEEP_MIN + 1)))

    sleep "$SLEEP_TIME"

done < "$LIST"

echo "=================================================="
echo " [DONE] All channels in the list were processed!"
echo "=================================================="