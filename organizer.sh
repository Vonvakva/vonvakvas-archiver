#!/bin/bash

# Hardening: undefined variables and broken pipes do not pass silently
set -uo pipefail

# Loads the project shared functions
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"

# organizer.sh - Sorts the channel files into subfolders by type
# (descricao/, info_json/, thumbs/, pfp/, videos/, subs/).
# NOTE: "descricao/" keeps its legacy Portuguese name on purpose: renaming it
# would break existing archives, ia/ bundles, backend checks and docs.
# "subs/" holds manual subtitle files (.vtt/.srt/.ass/.ssa/.lrc), e.g. from
# the archive-names (ntsn.sh) full variant.
# Run inside the channel folder.

export WORKDIR=$(pwd)

echo "=================================================="
echo " VONVAKVA'S ARCHIVE - File organizing"
echo " Folder: $WORKDIR"
echo "=================================================="

# --- DESCRIPTION (legacy folder name: descricao/) ---
mkdir -p "$WORKDIR"/descricao
mv "$WORKDIR"/*.description descricao/ 2>/dev/null

# --- INFO JSON ---
mkdir -p "$WORKDIR"/info_json
mv "$WORKDIR"/*.info.json info_json/ 2>/dev/null

# --- THUMBS ---
mkdir -p "$WORKDIR"/thumbs
mv "$WORKDIR"/*.webp thumbs/ 2>/dev/null

# --- PFP (prioritizes files with "videos" or "channel" in the name) ---
mkdir -p "$WORKDIR"/pfp
# First: images with "videos" in the name (yt-dlp pattern for pfp)
mv "$WORKDIR"/*[Vv]ideos*.jpg pfp/ 2>/dev/null
mv "$WORKDIR"/*[Vv]ideos*.png pfp/ 2>/dev/null
# Second: images with "channel" in the name
mv "$WORKDIR"/*[Cc]hannel*.jpg pfp/ 2>/dev/null
mv "$WORKDIR"/*[Cc]hannel*.png pfp/ 2>/dev/null
# Third: any other .jpg/.png that is not a thumb (thumbs are .webp)
mv "$WORKDIR"/*.jpg pfp/ 2>/dev/null
mv "$WORKDIR"/*.png pfp/ 2>/dev/null

# --- SUBS ---
mkdir -p "$WORKDIR"/subs
mv "$WORKDIR"/*.vtt subs/ 2>/dev/null
mv "$WORKDIR"/*.srt subs/ 2>/dev/null
mv "$WORKDIR"/*.ass subs/ 2>/dev/null
mv "$WORKDIR"/*.ssa subs/ 2>/dev/null
mv "$WORKDIR"/*.lrc subs/ 2>/dev/null

# --- VIDEOS ---
mkdir -p "$WORKDIR"/videos
mv "$WORKDIR"/*.mp4 videos/ 2>/dev/null
mv "$WORKDIR"/*.mkv videos/ 2>/dev/null
mv "$WORKDIR"/*.webm videos/ 2>/dev/null

# --- ANIMATION (intentional eye-candy) ---
sleep 1
echo
echo ...
sleep 0.6
echo ..
sleep 0.6
echo .
sleep 1.5
echo
ls --color=auto "$WORKDIR"/
echo "Organizing finished."
