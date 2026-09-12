#!/bin/bash
# scripts/iaupload/uploaderf.sh
# Full uploader: uploads an organized channel folder to the Internet Archive.
# (Keeps legacy filename uploaderf.sh for backward compatibility.)

# Hardening: undefined variables and broken pipes do not pass silently
set -uo pipefail

# Loads the project shared functions
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"

# Current working directory (must be the channel folder)

export WORKDIR=$(pwd)

# Current folder name = channel display name
channel="$(basename "$PWD")"

# Execution date
date_today="$(date +%F)"

# Item identifier
itemname="${channel,,}-${date_today}"

# Asks for the channel URL
read -rp "Channel URL: " channel_url

# Confirmation before the upload
echo
echo "=== Upload setup ==="
echo "Channel:     $channel"
echo "Date:        $date_today"
echo "Identifier:  $itemname"
echo "URL:         $channel_url"
echo

read -rp "All good? Do the upload? [y/N] " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Upload canceled."
    exit 0
fi

ia upload "$itemname" "$WORKDIR"/ia/ \
  --retries=10 \
  --metadata="channel:$channel_url" \
  --metadata="creator:$channel" \
  --metadata="title:$channel archive" \
  --metadata="collection:opensource_movies" \
  --metadata="mediatype:movies" \
  --metadata="scanner:Vonvakva's Archive" \
  --metadata="subject:youtube;youtuber;youtube-preservation;youtube-videos;asmr"

status=$?

if [[ $status -eq 0 ]]; then
    echo "Upload finished!"
    echo
    echo "Item:"
    echo "https://archive.org/details/$itemname"
else
    echo "The upload ended with an error."
    echo "Exit code: $status"
    exit "$status"
fi
