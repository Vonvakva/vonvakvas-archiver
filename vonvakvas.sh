#!/bin/bash
# vonvakvas.sh - Vonvakva's Archive CLI
# Entry point for every project command
#
# Usage: ./vonvakvas.sh <command> [options]
#        vonvakvas <command> [options]       # after installation

set -e  # Stops execution on error

# Resolve the project without depending on the caller's working directory.
# Precedence:
#   1. VONVAKVAS_ROOT (for custom installations and external launchers)
#   2. The directory containing this script, even when reached by symlink
#   3. The installer's default location: ~/.local/opt/vonvakvas-archive
resolve_project_root() {
    local entry_path="${BASH_SOURCE[0]}"
    local entry_dir
    local candidate

    # A launcher can be a symlink in a directory such as ~/.local/bin.
    # Resolve it so the real project is found before using the default path.
    if command -v readlink >/dev/null 2>&1; then
        entry_path="$(readlink -f -- "$entry_path")"
    fi
    entry_dir="$(cd -- "$(dirname -- "$entry_path")" && pwd -P)"

    if [[ -n "${VONVAKVAS_ROOT:-}" ]]; then
        candidate="$VONVAKVAS_ROOT"
    elif [[ -f "$entry_dir/api/router.sh" ]]; then
        candidate="$entry_dir"
    elif [[ -n "${HOME:-}" ]]; then
        candidate="$HOME/.local/opt/vonvakvas-archive"
    else
        printf 'Error: could not locate Vonvakva'"'"'s Archive.\n' >&2
        printf 'Set VONVAKVAS_ROOT to the installation directory and try again.\n' >&2
        return 1
    fi

    if [[ ! -f "$candidate/api/router.sh" || ! -f "$candidate/scripts/lib/common.sh" ]]; then
        printf 'Error: invalid Vonvakva'"'"'s Archive installation: %s\n' "$candidate" >&2
        printf 'Expected api/router.sh and scripts/lib/common.sh in that directory.\n' >&2
        return 1
    fi

    (cd -- "$candidate" && pwd -P)
}

PROJECT_ROOT="$(resolve_project_root)"

# Loads the router
source "$PROJECT_ROOT/api/router.sh"

# Checks whether any command was provided
if [[ $# -eq 0 ]]; then
    echo "Vonvakva's Archive CLI"
    echo ""
    echo "Use 'vonvakvas help' to see the available commands"
    exit 0
fi

# Routes the command
route_command "$@"
