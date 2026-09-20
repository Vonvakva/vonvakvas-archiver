#!/bin/bash

# Hardening: undefined variables and broken pipes do not pass silently
set -uo pipefail

# Loads the project shared functions
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"

# organizeri.sh - Sorts Instagram files (no pfp/ folder).
# NOTE: "descricao/" keeps its legacy Portuguese name on purpose (see organizer.sh).
# Run inside the folder to organize.

export WORKDIR=$(pwd)

echo "=================================================="
echo " VONVAKVA'S ARCHIVE - File organizing (Instagram)"
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

# --- VIDEOS ---
mkdir -p "$WORKDIR"/videos
mv "$WORKDIR"/*.mp4 videos/ 2>/dev/null
mv "$WORKDIR"/*.mkv videos/ 2>/dev/null
mv "$WORKDIR"/*.webm videos/ 2>/dev/null

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
