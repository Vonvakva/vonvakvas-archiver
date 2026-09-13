#!/bin/bash

# Hardening: undefined variables and broken pipes do not pass silently
set -uo pipefail

# Loads the project shared functions
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"

# desorganizarm.sh - Reverts the music organizing (musicas/ -> root).
# NOTE: keeps its legacy Portuguese filename and the legacy folder names
# (descricao/, musicas/) on purpose: renaming would break existing archives.
# Run inside the channel folder.

export WORKDIR=$(pwd)

echo "=================================================="
echo " VONVAKVA'S ARCHIVE - Revert music organizing"
echo " Folder: $WORKDIR"
echo "=================================================="

# Moves everything back to the root
mv "$WORKDIR"/descricao/* "$WORKDIR"/ 2>/dev/null
mv "$WORKDIR"/info_json/* "$WORKDIR"/ 2>/dev/null
mv "$WORKDIR"/thumbs/* "$WORKDIR"/ 2>/dev/null
mv "$WORKDIR"/pfp/* "$WORKDIR"/ 2>/dev/null
mv "$WORKDIR"/musicas/* "$WORKDIR"/ 2>/dev/null

# Removes the empty folders
rmdir "$WORKDIR"/descricao "$WORKDIR"/info_json "$WORKDIR"/thumbs "$WORKDIR"/pfp "$WORKDIR"/musicas 2>/dev/null

# Animation
echo ...
sleep 0.6
echo ..
sleep 0.6
echo .
sleep 1
echo "Reverting finished."
echo
ls --color=auto "$WORKDIR"/
