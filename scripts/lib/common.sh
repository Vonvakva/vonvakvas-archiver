#!/bin/bash
# scripts/lib/common.sh
# Shared functions for all project scripts
# This file must be sourced by the other scripts

# Detects the project root directory
# Works regardless of where the script is called from
detect_project_root() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Walks up until it finds a project marker (config/ or .projectroot)
    while [[ "$script_dir" != "/" ]]; do
        if [[ -d "$script_dir/config" ]] || [[ -f "$script_dir/.projectroot" ]]; then
            echo "$script_dir"
            return 0
        fi
        script_dir="$(dirname "$script_dir")"
    done
    
    echo "Error: could not find the project root" >&2
    return 1
}

# Exports PROJECT_ROOT for all scripts
export PROJECT_ROOT="$(detect_project_root)"

export VONVAKVAS_PROFILE="${VONVAKVAS_PROFILE:-}"

# Returns the active profile directory (empty if no profile is active)
# NOTE: defined BEFORE the legacy migration below, which relies on it.
profile_dir() {
    if [[ -n "$VONVAKVAS_PROFILE" ]]; then
        echo "$PROJECT_ROOT/config/profiles/$VONVAKVAS_PROFILE"
    fi
}

# Legacy file names -> canonical names (English). The canonical names are
# used everywhere now, but the old Portuguese names are still recognized and
# migrated automatically so nothing breaks for existing installs.
# NOTE: "succeeded_archvings.txt" keeps your requested spelling.
declare -A _LEGACY_CONFIG_FILES=(
    ["lista_canais.txt"]="channel_list.txt"
    ["archivamentos_bem_sucedidos.txt"]="succeeded_archvings.txt"
)

# Returns the canonical (English) file name for a config file, mapping
# legacy Portuguese names automatically.
canonical_config_name() {
    local name="$1"
    if [[ -n "${_LEGACY_CONFIG_FILES[$name]:-}" ]]; then
        echo "${_LEGACY_CONFIG_FILES[$name]}"
    else
        echo "$name"
    fi
}

# Migrates legacy config files to their canonical names by copying them.
# Search order: profile dir -> <CHANNELS_ROOT>/config -> project config/.
# Never overwrites an existing canonical file, never deletes the legacy one.
migrate_legacy_config() {
    local legacy="$1"
    local canonical="$2"
    local dirs=()
    local pdir
    pdir="$(profile_dir)"
    if [[ -n "$pdir" ]]; then
        dirs+=("$pdir")
    fi
    if [[ -n "${CHANNELS_ROOT:-}" ]]; then
        dirs+=("$CHANNELS_ROOT/config")
    fi
    dirs+=("$PROJECT_ROOT/config")
    local d
    for d in "${dirs[@]}"; do
        if [[ -f "$d/$legacy" && ! -f "$d/$canonical" ]]; then
            cp "$d/$legacy" "$d/$canonical" 2>/dev/null || true
        fi
    done
}

# Runs the migration for every known legacy file.
migrate_all_legacy_configs() {
    local legacy
    for legacy in "${!_LEGACY_CONFIG_FILES[@]}"; do
        migrate_legacy_config "$legacy" "${_LEGACY_CONFIG_FILES[$legacy]}"
    done
}

# NOTE: the migration itself runs further below, AFTER settings.env is
# loaded, so files living on an external CHANNELS_ROOT drive are migrated too.

# Optional settings (config/settings.env), e.g. moving channels to an HDD
# drive. If CHANNELS_ROOT points to a valid folder, files under
# <CHANNELS_ROOT>/config/ take priority over the project config/.
SETTINGS_FILE="$PROJECT_ROOT/config/settings.env"
if [[ -f "$SETTINGS_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$SETTINGS_FILE"
fi

# Active profile settings (if any) override the project ones,
# allowing a different CHANNELS_ROOT per profile.
_PDIR="$(profile_dir)"
if [[ -n "$_PDIR" && -f "$_PDIR/settings.env" ]]; then
    # shellcheck disable=SC1090
    source "$_PDIR/settings.env"
fi
unset _PDIR

# Migrate legacy Portuguese file names on load so every script that sources
# common.sh gets the canonical files even if the user still has the old names.
migrate_all_legacy_configs

# Helper function: returns the full path of a config file.
# Priority order:
#   1. config/profiles/<profile>/<file>  (if active profile and file exists)
#   2. <CHANNELS_ROOT>/config/<file>    (if file exists there)
#   3. project config/<file>         (fallback — nothing breaks if the
#                                           HDD is missing)
config_path() {
    local requested="$1"
    local name
    name="$(canonical_config_name "$requested")"
    local pdir
    pdir="$(profile_dir)"
    if [[ -n "$pdir" ]]; then
        if [[ -f "$pdir/$name" ]]; then
            echo "$pdir/$name"
            return
        fi
        # Legacy fallback: old Portuguese name still works inside the profile.
        if [[ "$name" != "$requested" && -f "$pdir/$requested" ]]; then
            echo "$pdir/$requested"
            return
        fi
    fi
    if [[ -n "${CHANNELS_ROOT:-}" && "$CHANNELS_ROOT" != "$PROJECT_ROOT" ]]; then
        if [[ -f "$CHANNELS_ROOT/config/$name" ]]; then
            echo "$CHANNELS_ROOT/config/$name"
            return
        fi
        # Legacy fallback on the external drive.
        if [[ "$name" != "$requested" && -f "$CHANNELS_ROOT/config/$requested" ]]; then
            echo "$CHANNELS_ROOT/config/$requested"
            return
        fi
    fi
    echo "$PROJECT_ROOT/config/$name"
}

# Helper: returns the full path inside scripts/
# Usage: script_path mainscripts/nts.sh
script_path() {
    echo "$PROJECT_ROOT/scripts/$1"
}

# Helper: loads environment variables from a .env file
# Usage: load_env config/telegram.env
load_env() {
    local env_file="$1"
    if [[ -f "$env_file" ]]; then
        set -a
        source "$env_file"
        set +a
    else
        echo "Warning: file $env_file not found" >&2
    fi
}
