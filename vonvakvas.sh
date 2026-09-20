#!/bin/bash
# vonvakvas.sh - Vonvakva's Archive CLI
# Entry point for every project command
#
# Usage: ./vonvakvas.sh <command> [options]
#        ./vonvakvas.sh help to see the available commands

set -e  # Stops execution on error

# Gets the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Loads the router
source "$SCRIPT_DIR/api/router.sh"

# Checks whether any command was provided
if [[ $# -eq 0 ]]; then
    echo "Vonvakva's Archive CLI"
    echo ""
    echo "Use './vonvakvas.sh help' to see the available commands"
    exit 0
fi

# Routes the command
route_command "$@"
