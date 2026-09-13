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
