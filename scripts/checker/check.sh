#!/bin/bash
# check.sh - HTTP check + Telegram notification

# Hardening: undefined variables and broken pipes do not pass silently
set -uo pipefail

# Loads the project shared functions
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"

# Loads Telegram credentials from an external file (safer)
load_env "$(config_path telegram.env)"

# Safe fallback: accepts TELEGRAM_TOKEN/TELEGRAM_CHAT_ID already exported
# in the environment. No secrets are embedded in the code (>= 30/08/2026).
TOKEN="${TELEGRAM_TOKEN:-${TOKEN:-}}"
CHAT_ID="${TELEGRAM_CHAT_ID:-${CHAT_ID:-}}"

LIST="$(config_path channel_list.txt)"

send_telegram() {
    local MESSAGE="$1"

    # Hardening: never sends without credentials (avoids silent failure)
    if [[ -z "$TOKEN" || -z "$CHAT_ID" ]]; then
        echo "WARNING: TELEGRAM_TOKEN/TELEGRAM_CHAT_ID not set." >&2
        echo "Check if '$(config_path telegram.env)' exists or export the variables." >&2
        return 2
    fi

    curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=${MESSAGE}" \
        -d "parse_mode=Markdown" > /dev/null
}

if [ ! -f "$LIST" ]; then
    echo "Error: $LIST not found."
    exit 1
fi

echo "=================================================="
echo " VONVAKVA'S ARCHIVE - Channel check"
echo "=================================================="

OFFLINE_CHANNELS=()

while IFS= read -r channel || [ -n "$channel" ]; do
    # Skips blank lines and comments (#)
    if [[ "$channel" =~ ^# ]] || [ -z "$channel" ]; then
        continue
    fi

    HTTP_CODE=$(curl -s -o /dev/null -I -w "%{http_code}" -L -A "Mozilla/5.0" "https://www.youtube.com/@$channel")

    if [ "$HTTP_CODE" -eq 200 ]; then
        echo " [200 OK]  -> @$channel"
    else
        echo " [$HTTP_CODE OFF] -> @$channel"
        OFFLINE_CHANNELS+=("$channel")
    fi

    sleep 0.5
done < "$LIST"

echo "=================================================="

# If there are offline channels, send the Telegram alert
if [ ${#OFFLINE_CHANNELS[@]} -gt 0 ]; then
    echo " OFFLINE CHANNELS DETECTED! Sending Telegram alert..."
    
    TEXT=" *[Vonvakva's Archive] Unavailable channels alert!*%0A%0A"
    TEXT+="The following channels went down or returned error 404:%0A"
    
    for off in "${OFFLINE_CHANNELS[@]}"; do
        TEXT+="• \`@${off}\`%0A"
    done
    
    if send_telegram "$TEXT"; then
        echo " Alert sent!"
    else
        echo " Failed to send the alert (missing credentials or API error)."
    fi
else
    echo " All channels in the list are ONLINE (200 OK)!"
fi

echo "=================================================="
