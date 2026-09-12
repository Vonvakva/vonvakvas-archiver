#!/usr/bin/env bash
# start-gui.sh - Starts the Vonvakva's Archive GUI

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activates the venv (supports install in an apps folder: ./venv,
# and direct execution from the repo: ../vonvakvas)
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    VENV_PATH="$SCRIPT_DIR/venv"
elif [ -f "$SCRIPT_DIR/../vonvakvas/bin/activate" ]; then
    VENV_PATH="$SCRIPT_DIR/../vonvakvas"
else
    echo "Error: venv not found."
    echo "Looked in: $SCRIPT_DIR/venv and $SCRIPT_DIR/../vonvakvas"
    exit 1
fi
source "$VENV_PATH/bin/activate"

# The `ia` CLI (upload to the Internet Archive) lives in a separate venv.
# We DO NOT activate it: two activations in a row cancel each other out
# (the second deactivate restores the PATH saved by the first).
# We append it to the END of the PATH so `python` remains the project
# venv python (the one with PySide6) — only the `ia` binary is picked up.
IA_VENV="/home/flucio/venvs/internetarchive"
if [[ -d "$IA_VENV/bin" ]]; then
    export PATH="$PATH:$IA_VENV/bin"
fi

# Clears the Python cache and starts the GUI
cd "$SCRIPT_DIR"
rm -rf gui/__pycache__
export PYTHONDONTWRITEBYTECODE=1
exec python -B gui/main.py
