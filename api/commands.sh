#!/bin/bash
# api/commands.sh
# vonvakvas CLI command definitions
# if you are that kind that like to see the internals or will edit something,
# ntsp = nts playlist :p

# ============================================
# COMMAND: archive
# Downloads videos from a YouTube channel
# Usage: vonvakvas archive <@channel> [y/n]
# ============================================
cmd_archive() {
    local channel="$1"
    local mask="${2:-n}"
    
    if [[ -z "$channel" ]]; then
        echo "Error: specify the channel @handle"
        echo "Usage: vonvakvas archive <@channel> [y/n]"
        echo "  y = use cookies (random account between 1, 2 and 3)"
        echo "  n = do not count view (no cookies)"
        exit 1
    fi
    
    # Removes the @ if the user includes it
    channel="${channel#@}"
    
    echo "=================================================="
    echo " VONVAKVA'S ARCHIVE - Channel: @$channel"
    echo " Cookies: $([ "$mask" = "y" ] && echo "Active (random account)" || echo "Disabled (do not count view)")"
    echo "=================================================="
    
    # Calls the download script
    bash "$(script_path mainscripts/nts.sh)" "$channel" "$mask"
}

# Helper function: runs an organizer (scripts/organizers/*.sh) inside a folder
# Internal usage: _run_organizer <script_name.sh> <folder>
_run_organizer() {
    local organizer="$1"      # e.g.: organizer.sh
    local folder="${2:-.}"

    if [[ -z "$organizer" ]]; then
        echo "Error: organizer name not provided"
        exit 1
    fi

    if [[ ! -d "$folder" ]]; then
        echo "Error: folder '$folder' not found"
        exit 1
    fi

    # Enters the folder and runs the organizer
    (
        cd "$folder" || exit 1
        bash "$(script_path "organizers/$organizer")"
    )
}

# ============================================
# COMMAND: organize
# Sorts files into subfolders
# Usage: vonvakvas organize <folder>
# ============================================
cmd_organize() {
    local folder="${1:-.}"
    
    echo "=================================================="
    echo " VONVAKVA'S ORGANIZE - Folder: $folder"
    echo "=================================================="
    
    _run_organizer organizer.sh "$folder"
}

# ============================================
# COMMAND: archive-names
# Downloads videos from a YouTube channel, full variant (ntsn.sh):
# original Windows-safe filenames + manual subtitles + comments
# Usage: vonvakvas archive-names <@channel> [y/n]
# ============================================
cmd_archive_names() {
    local channel="$1"
    local mask="${2:-n}"

    if [[ -z "$channel" ]]; then
        echo "Error: specify the channel @handle"
        echo "Usage: vonvakvas archive-names <@channel> [y/n]"
        echo "  y = use cookies (random account between 1, 2 and 3)"
        echo "  n = do not count view (no cookies)"
        exit 1
    fi

    # Removes the @ if the user includes it
    channel="${channel#@}"

    echo "=================================================="
    echo " VONVAKVA'S ARCHIVE NAMES - Channel: @$channel"
    echo " Cookies: $([ "$mask" = "y" ] && echo "Active (random account)" || echo "Disabled (do not count view)")"
    echo "=================================================="

    # Calls the full-variant download script
    bash "$(script_path mainscripts/ntsn.sh)" "$channel" "$mask"
}

# ============================================
# COMMAND: archive-playlist (nts playlist = ntsp.sh)
# Alternative variant of archive for playlists/URLs (ntsp.sh)
# Usage: vonvakvas archive-playlist <@channel|URL> [y/n]
# NOTE: "archive-pro" and "ap" are legacy aliases (backward compatibility)
# ============================================
cmd_archive_playlist() {
    local channel="$1"
    local mask="${2:-n}"
    
    if [[ -z "$channel" ]]; then
        echo "Error: specify the channel @handle or the URL"
        echo "Usage: vonvakvas archive-playlist <@channel|URL> [y/n]"
        echo "e.g.:  vonvakvas archive-playlist lofigirl y"
        echo "e.g.:  vonvakvas archive-playlist https://www.youtube.com/@lofigirl y"
        exit 1
    fi
    
    # Removes the @ if the user includes it
    channel="${channel#@}"
    
    # If it is not a full URL, builds the channel link
    if [[ "$channel" != http* ]]; then
        channel="https://www.youtube.com/@${channel}"
    fi
    
    echo "=================================================="
    echo " VONVAKVA'S ARCHIVE PLAYLIST - Channel/URL: $channel"
    echo " Cookies: $([ "$mask" = "y" ] && echo "Active (random account)" || echo "Disabled (do not count view)")"
    echo "=================================================="
    
    # Calls the download script
    bash "$(script_path mainscripts/ntsp.sh)" "$channel" "$mask"
}

# ============================================
# COMMAND: organize-instagram
# Sorts files downloaded from Instagram (no pfp)
# Usage: vonvakvas organize-instagram <folder>
# ============================================
cmd_organize_instagram() {
    local folder="${1:-.}"
    
    echo "=================================================="
    echo " VONVAKVA'S ORGANIZE INSTAGRAM - Folder: $folder"
    echo "=================================================="
    
    _run_organizer organizeri.sh "$folder"
}

# ============================================
# COMMAND: organize-music
# Sorts music files (mp4/mp3 -> musicas/)
# Usage: vonvakvas organize-music <folder>
# ============================================
cmd_organize_music() {
    local folder="${1:-.}"
    
    echo "=================================================="
    echo " VONVAKVA'S ORGANIZE MUSIC - Folder: $folder"
    echo "=================================================="
    
    _run_organizer organizerm.sh "$folder"
}

# ============================================
# COMMAND: desorganize
# Reverts the organizing (moves everything back to the root)
# Usage: vonvakvas desorganize <folder>
# ============================================
cmd_desorganize() {
    local folder="${1:-.}"
    
    echo "=================================================="
    echo " VONVAKVA'S DESORGANIZE - Folder: $folder"
    echo "=================================================="
    
    _run_organizer desorganizar.sh "$folder"
}

# ============================================
# COMMAND: desorganize-music
# Reverts the music organizing (organize-music)
# Usage: vonvakvas desorganize-music <folder>
# ============================================
cmd_desorganize_music() {
    local folder="${1:-.}"
    
    echo "=================================================="
    echo " VONVAKVA'S DESORGANIZE MUSIC - Folder: $folder"
    echo "=================================================="
    
    _run_organizer desorganizarm.sh "$folder"
}

# ============================================
# COMMAND: prepare-upload
# Prepares the organized folder for Internet Archive upload
# Usage: vonvakvas prepare-upload <folder>
# ============================================
cmd_prepare_upload() {
    local folder="${1:-.}"
    
    if [[ ! -d "$folder" ]]; then
        echo "Error: folder '$folder' not found"
        exit 1
    fi
    
    # organizerv2.sh expects an already organized folder
    for sub in videos descricao info_json; do
        if [[ ! -d "$folder/$sub" ]]; then
            echo "Warning: folder '$folder/$sub' not found."
            echo "Run 'vonvakvas organize $folder' before prepare-upload."
        fi
    done
    
    echo "=================================================="
    echo " VONVAKVA'S PREPARE UPLOAD - Folder: $folder"
    echo "=================================================="
    
    # Enters the folder and runs organizerv2
    (
        cd "$folder" || exit 1
        bash "$(script_path organizers/organizerv2.sh)"
    )
}

# ============================================
# COMMAND: upload
# Uploads to the Internet Archive
# Usage: vonvakvas upload <folder>
# ============================================
cmd_upload() {
    local folder="${1:-.}"
    
    if [[ ! -d "$folder" ]]; then
        echo "Error: folder '$folder' not found"
        exit 1
    fi
    
    # Checks if the ia/ folder exists inside the folder
    if [[ ! -d "$folder/ia" ]]; then
        echo "Error: 'ia/' folder not found in '$folder'"
        echo "Run 'vonvakvas organize $folder' first"
        exit 1
    fi
    
    # Enters the folder and runs the uploader
    (
        cd "$folder" || exit 1
        bash "$(script_path iaupload/uploaderf.sh)"
    )
}

# ============================================
# COMMAND: check
# Checks the status of the channels in the list
# Usage: vonvakvas check
# ============================================
cmd_check() {
    echo "=================================================="
    echo " VONVAKVA'S CHECK - Checking channels..."
    echo "=================================================="
    
    bash "$(script_path checker/check.sh)"
}

# ============================================
# COMMAND: mass-archive
# Downloads every channel in the list
# Usage: vonvakvas mass-archive
# ============================================
cmd_mass_archive() {
    echo "=================================================="
    echo " VONVAKVA'S MASS ARCHIVE - Archiving the list..."
    echo "=================================================="
    
    bash "$(script_path masses/mass_nts.sh)"
}

# ============================================
# COMMAND: mass-archive-names
# Downloads every channel in the list, full variant (ntsn.sh)
# Usage: vonvakvas mass-archive-names
# ============================================
cmd_mass_archive_names() {
    echo "=================================================="
    echo " VONVAKVA'S MASS ARCHIVE NAMES - Archiving the list..."
    echo "=================================================="

    bash "$(script_path masses/mass_ntsn.sh)"
}

# ============================================
# COMMAND: mass-organize
# Organizes every channel folder
# Usage: vonvakvas mass-organize
# ============================================
cmd_mass_organize() {
    echo "=================================================="
    echo " VONVAKVA'S MASS ORGANIZE - Organizing folders..."
    echo "=================================================="
    
    bash "$(script_path masses/mass_organizer.sh)"
}

# ============================================
# COMMAND: profile
# Manages configuration profiles (config/profiles/<name>/) — the same
# instances the GUI uses. The active profile is persisted in
# config/gui_state.env (GUI_PROFILE), the key the GUI reads/writes too.
# Usage: vonvakvas profile [list|use|create|delete|files] [options]
# ============================================

_profiles_dir()   { echo "$PROJECT_ROOT/config/profiles"; }
_gui_state_file() { echo "$PROJECT_ROOT/config/gui_state.env"; }

# Same rule as the GUI (gui/backend.py: _PROFILE_NAME_RE)
_PROFILE_NAME_RE='^[a-zA-Z0-9][a-zA-Z0-9 _-]{0,39}$'

_profile_trim() {
    local s="$1"
    s="${s#"${s%%[![:space:]]*}"}"
    s="${s%"${s##*[![:space:]]}"}"
    printf '%s' "$s"
}

# Prints the name-validation error (same messages as the GUI) and returns 0
# when the name is INVALID; returns 1 when the name is valid.
_profile_name_error() {
    local name="$1"
    if [[ -z "$name" ]]; then
        echo "Type a name for the profile."
        return 0
    fi
    if [[ ! "$name" =~ $_PROFILE_NAME_RE ]]; then
        echo "Invalid name. Use letters, numbers, spaces, hyphen or underscore (max. 40 characters, starting with a letter/number)."
        return 0
    fi
    return 1
}

# True while a project script (download/upload job) is running — the same
# guard the GUI uses before switching profiles.
_profile_job_running() {
    command -v pgrep >/dev/null 2>&1 || return 1
    local pattern="${PROJECT_ROOT//./\\.}"
    pgrep -f "$pattern/scripts/" >/dev/null 2>&1
}

# Persists the active profile in config/gui_state.env (GUI_PROFILE="..."),
# preserving the other lines (e.g. GUI_THEME). Same KEY="VALUE" format the
# GUI writes (gui/backend.py _set_env_value), so both sides stay in sync.
_profile_set_active() {
    local value="$1"
    local file tmp line found=0
    file="$(_gui_state_file)"
    tmp="$file.tmp.$$"
    {
        if [[ -f "$file" ]]; then
            while IFS= read -r line || [[ -n "$line" ]]; do
                if [[ "$found" -eq 0 && "${line#"${line%%[![:space:]]*}"}" == GUI_PROFILE* ]]; then
                    printf 'GUI_PROFILE="%s"\n' "$value"
                    found=1
                else
                    printf '%s\n' "$line"
                fi
            done < "$file"
            [[ "$found" -eq 1 ]] || printf 'GUI_PROFILE="%s"\n' "$value"
        else
            printf '# GUI state (active profile / theme). Interface-only file.\n'
            printf 'GUI_PROFILE="%s"\n' "$value"
        fi
    } > "$tmp"
    mv -f "$tmp" "$file"
}

_profile_usage() {
    cat << 'EOF'
Usage: vonvakvas profile <subcommand> [options]

Subcommands:
    list                      Lists the profiles ('*' = active)
    use <name>                Activates a profile (shared with the GUI)
    use --default             Back to the project default config/
    create <name> [--no-copy] Creates a profile (copies the base config by default)
    delete <name>             Deletes a profile (the active one is refused)
    files [name]              Lists the config files of a profile (default: active)

Notes:
    * Profiles live in config/profiles/<name>/ — the same storage the GUI uses
    * The active profile is saved in config/gui_state.env (GUI_PROFILE), so
      the CLI and the GUI always use the same profile
    * VONVAKVAS_PROFILE=<name> still overrides everything (per-command)
EOF
}

_profile_list() {
    local pdir active name d
    local names=()
    pdir="$(_profiles_dir)"
    active="${VONVAKVAS_PROFILE:-}"

    echo "=================================================="
    echo " VONVAKVA'S PROFILES"
    echo "=================================================="
    if [[ -n "$active" ]]; then
        echo "Active profile: $active"
    else
        echo "Active profile: (project default config/)"
    fi
    echo ""

    if [[ -d "$pdir" ]]; then
        for d in "$pdir"/*; do
            [[ -d "$d" ]] && names+=("${d##*/}")
        done
    fi

    if [[ ${#names[@]} -eq 0 ]]; then
        echo "No profiles yet. Create one with: vonvakvas profile create <name>"
        return 0
    fi

    printf '%s\n' "${names[@]}" | LC_ALL=C sort | while IFS= read -r name; do
        if [[ "$name" == "$active" ]]; then
            printf '  * %s\n' "$name"
        else
            printf '    %s\n' "$name"
        fi
    done
    echo ""
    echo "'*' marks the active profile (shared with the GUI)."
}

_profile_use() {
    local force=0 target="" got=0 err
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --force|-f) force=1 ;;
            --default|--none) target=""; got=1 ;;
            -*)
                echo "Error: unknown option '$1'"
                echo "Usage: vonvakvas profile use <name> [--force] | --default"
                exit 1
                ;;
            *) target="$1"; got=1 ;;
        esac
        shift
    done

    if [[ "$got" -eq 0 ]]; then
        echo "Error: specify the profile name (or --default)"
        echo "Usage: vonvakvas profile use <name> [--force] | --default"
        exit 1
    fi

    if [[ -n "$target" ]]; then
        target="$(_profile_trim "$target")"
        if err="$(_profile_name_error "$target")"; then
            echo "Error: $err"
            exit 1
        fi
        if [[ ! -d "$(_profiles_dir)/$target" ]]; then
            echo "Error: profile '$target' not found. Use 'vonvakvas profile list' to see the available ones."
            exit 1
        fi
        if [[ "$force" -eq 0 ]] && _profile_job_running; then
            echo "Error: a project task is running; wait for it to finish or use --force."
            exit 1
        fi
    fi

    _profile_set_active "$target"
    if [[ -n "$target" ]]; then
        echo "Active profile: $target"
    else
        echo "Active profile: project default config/"
    fi
    echo "(saved in config/gui_state.env — the GUI uses the same profile)"
}

_profile_create() {
    local name="" copy=1 err f pdir
    local copied=()
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --copy) copy=1 ;;
            --no-copy|--empty) copy=0 ;;
            -*)
                echo "Error: unknown option '$1'"
                echo "Usage: vonvakvas profile create <name> [--no-copy]"
                exit 1
                ;;
            *)
                if [[ -n "$name" ]]; then
                    echo "Error: only one profile name at a time."
                    exit 1
                fi
                name="$1"
                ;;
        esac
        shift
    done

    name="$(_profile_trim "$name")"
    if err="$(_profile_name_error "$name")"; then
        echo "Error: $err"
        exit 1
    fi
    if [[ -e "$(_profiles_dir)/$name" ]]; then
        echo "Error: there is already a profile named '$name'."
        exit 1
    fi

    pdir="$(_profiles_dir)/$name"
    mkdir -p "$pdir"

    if [[ "$copy" -eq 1 ]]; then
        # Same list the GUI copies (never archive.txt: each profile keeps
        # its own download history).
        for f in channel_list.txt cookies_1.txt cookies_2.txt cookies_3.txt telegram.env; do
            if [[ -f "$PROJECT_ROOT/config/$f" && ! -f "$pdir/$f" ]]; then
                cp -p "$PROJECT_ROOT/config/$f" "$pdir/$f"
                copied+=("$f")
            fi
        done
    fi

    echo "Profile created: config/profiles/$name"
    if [[ "$copy" -eq 1 ]]; then
        if [[ ${#copied[@]} -gt 0 ]]; then
            echo "Copied from the project config: ${copied[*]}"
        else
            echo "No base config files to copy."
        fi
    else
        echo "Created empty (--no-copy): missing files fall back to the project config/."
    fi
}

_profile_delete() {
    local name="" err
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -*)
                echo "Error: unknown option '$1'"
                echo "Usage: vonvakvas profile delete <name>"
                exit 1
                ;;
            *)
                if [[ -n "$name" ]]; then
                    echo "Error: only one profile name at a time."
                    exit 1
                fi
                name="$1"
                ;;
        esac
        shift
    done

    name="$(_profile_trim "$name")"
    if err="$(_profile_name_error "$name")"; then
        echo "Error: $err"
        exit 1
    fi
    if [[ "$name" == "${VONVAKVAS_PROFILE:-}" ]]; then
        echo "Error: cannot delete the active profile '$name'."
        echo "Switch first: vonvakvas profile use <other>"
        exit 1
    fi
    if [[ ! -d "$(_profiles_dir)/$name" ]]; then
        echo "Error: profile '$name' not found. Use 'vonvakvas profile list' to see the available ones."
        exit 1
    fi

    rm -rf -- "$(_profiles_dir)/$name"
    echo "Profile deleted: $name"
}

_profile_files() {
    local name="" err d
    local files=()
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -*)
                echo "Error: unknown option '$1'"
                echo "Usage: vonvakvas profile files [name]"
                exit 1
                ;;
            *)
                if [[ -n "$name" ]]; then
                    echo "Error: only one profile name at a time."
                    exit 1
                fi
                name="$1"
                ;;
        esac
        shift
    done

    if [[ -z "$name" ]]; then
        name="${VONVAKVAS_PROFILE:-}"
    fi
    if [[ -z "$name" ]]; then
        echo "Error: no active profile; specify one: vonvakvas profile files <name>"
        exit 1
    fi

    name="$(_profile_trim "$name")"
    if err="$(_profile_name_error "$name")"; then
        echo "Error: $err"
        exit 1
    fi
    if [[ ! -d "$(_profiles_dir)/$name" ]]; then
        echo "Error: profile '$name' not found. Use 'vonvakvas profile list' to see the available ones."
        exit 1
    fi

    for d in "$(_profiles_dir)/$name"/*; do
        [[ -f "$d" ]] && files+=("${d##*/}")
    done

    if [[ ${#files[@]} -eq 0 ]]; then
        echo "No configuration files in profile '$name' yet."
        echo "(missing files fall back to the project config/)"
        return 0
    fi

    echo "Files in profile '$name':"
    printf '%s\n' "${files[@]}" | LC_ALL=C sort | while IFS= read -r d; do
        printf '  %s\n' "$d"
    done
}

cmd_profile() {
    local sub="list"
    if [[ $# -gt 0 ]]; then
        sub="$1"
        shift
    fi

    case "$sub" in
        list|ls)             _profile_list "$@" ;;
        use|activate|switch) _profile_use "$@" ;;
        create|new)          _profile_create "$@" ;;
        delete|rm|remove)    _profile_delete "$@" ;;
        files|show)          _profile_files "$@" ;;
        help|--help|-h)      _profile_usage ;;
        *)
            echo "Error: unknown profile subcommand '$sub'"
            _profile_usage
            exit 1
            ;;
    esac
}

# ============================================
# HELP
# ============================================
show_help() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════╗
║                    VONVAKVA'S ARCHIVE CLI - Help                         ║
╚══════════════════════════════════════════════════════════════════════════╝

USAGE:
    vonvakvas <command> [options]

COMMANDS:

    archive, a <@channel> [y/n]
        Downloads videos from a YouTube channel
        y = use cookies (random account between 1, 2 and 3)
        n = do not count view (no cookies)
        Ex: vonvakvas archive lofigirl y

    archive-names, an <@channel> [y/n]
        Full-variant download (ntsn.sh): Windows-safe original
        filenames + manual subtitles + comments (no auto-subs)
        Ex: vonvakvas archive-names lofigirl y

    organize, org <folder>
        Sorts files into subfolders (videos, thumbs, etc)
        Ex: vonvakvas organize ./your-directory/FlucioVR

    organize-instagram, orgi <folder>
        Sorts files downloaded from Instagram (no pfp folder)
        Ex: vonvakvas organize-instagram ./your-directory/some_profile

    organize-music, orgm <folder>
        Sorts music files (mp4/mp3 -> musicas/)
        Ex: vonvakvas organize-music ./your-music-directory

    desorganize, dorg <folder>
        Reverts the organizing (moves everything back to the root)
        Ex: vonvakvas desorganize ./your-directory/FlucioVR

    desorganize-music, dorgm <folder>
        Reverts the music organizing (moves musicas/ back)
        Ex: vonvakvas desorganize-music ./your-music-folder

    prepare-upload, prep <folder>
        Prepares the organized folder for Internet Archive upload
        Requires videos/, descricao/, info_json/ subfolders (created by organize)
        Ex: vonvakvas prepare-upload ./your-directory/FlucioVR

    archive-playlist, apl <@channel|URL> [y/n]
        Alternative download variant for playlists/URLs (ntsp = nts playlist)
        Accepts @channel or the full channel URL
        Ex: vonvakvas archive-playlist lofigirl y

    upload, up <folder>
        Uploads the folder to the Internet Archive
        Requires the 'ia/' folder (created by organize)
        Ex: vonvakvas upload ./your-directory/FlucioVR

    check, c
        Checks the status of the channels in the list
        Ex: vonvakvas check

    mass-archive, ma
        Downloads every channel in the list (channel_list.txt)
        Ex: vonvakvas mass-archive

    mass-archive-names, man
        Downloads every channel in the list, full variant (ntsn.sh):
        original names + manual subtitles + comments
        Ex: vonvakvas mass-archive-names

    mass-organize, mo
        Organizes every channel folder
        Ex: vonvakvas mass-organize

    profile, prof <list|use|create|delete|files>
        Manages configuration profiles (same storage as the GUI)
        The active profile is shared with the GUI (config/gui_state.env)
        Ex: vonvakvas profile list
        Ex: vonvakvas profile use hdd
        Ex: vonvakvas profile create travel --no-copy

    help, --help, -h
        Shows this help message

EXAMPLES:

    # Download a specific channel
    ./vonvakvas.sh archive lofigirl y

    # Organize and upload
    ./vonvakvas.sh organize ./your-directory/FlucioVR
    ./vonvakvas.sh upload ./your-directory/FlucioVR

    # Check offline channels
    ./vonvakvas.sh check

    # Archive the whole channel list
    ./vonvakvas.sh mass-archive

WORKFLOWS:

    Simple download:
        vonvakvas archive <channel> y

    Full download (original names + subs + comments):
        vonvakvas archive-names <channel> y

    Download + Organize + Upload:
        vonvakvas archive <channel> y
        vonvakvas organize <folder>
        vonvakvas upload <folder>

    Update the whole list:
        vonvakvas mass-archive
        vonvakvas mass-organize

EOF
}
