#!/bin/bash

# scripts/organizers/organizerv2.sh
# Organizer version 2: prepares an already organized folder for Internet Archive upload.
# Runs inside the channel folder and builds the ia/ structure with videos, descriptions and info.json.

# Hardening: undefined variables and broken pipes do not pass silently
set -uo pipefail

# Loads the project shared functions
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"

# Current folder name (channel name) in lowercase
channel=$(basename "$PWD")
channel=$(printf '%s' "$channel" | tr '[:upper:]' '[:lower:]')

mkdir ia

mkdir -p ia/Videos

# The profile image with "Videos" in the name becomes the itemimage (item cover on Internet Archive)
cp pfp/*Videos* "ia/${channel}_itemimage.jpg"

# Gathers videos, descriptions and info.json inside ia/Videos
cp videos/* descricao/* info_json/* ia/Videos
