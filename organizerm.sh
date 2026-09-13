#!/bin/bash

# Hardening: undefined variables and broken pipes do not pass silently
set -uo pipefail

# Loads the project shared functions
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"

# organizerm.sh - Sorts music files (mp4/mkv/webm/mp3 -> musicas/).
# NOTE: "descricao/" and "musicas/" keep their legacy Portuguese names on purpose:
# renaming them would break existing archives and docs.
# Run inside the folder to organize.

export WORKDIR=$(pwd)

echo "=================================================="
echo " VONVAKVA'S ARCHIVE - Music organizing"
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
mv "$WORKDIR"/*[Vv]ideos*.jpg pfp/ 2>/dev/null
mv "$WORKDIR"/*[Vv]ideos*.png pfp/ 2>/dev/null
mv "$WORKDIR"/*[Cc]hannel*.jpg pfp/ 2>/dev/null
mv "$WORKDIR"/*[Cc]hannel*.png pfp/ 2>/dev/null
mv "$WORKDIR"/*.jpg pfp/ 2>/dev/null
mv "$WORKDIR"/*.png pfp/ 2>/dev/null

# --- MUSIC ---
mkdir -p "$WORKDIR"/musicas
mv "$WORKDIR"/*.mp4 musicas/ 2>/dev/null
mv "$WORKDIR"/*.mkv musicas/ 2>/dev/null
mv "$WORKDIR"/*.webm musicas/ 2>/dev/null
mv "$WORKDIR"/*.mp3 musicas/ 2>/dev/null

# --- ANIMATION ---
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
