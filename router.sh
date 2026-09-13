#!/bin/bash
# api/router.sh
# Central router for the vonvakvas CLI

# Loads shared functions
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../scripts/lib/common.sh"

# Imports command definitions
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/commands.sh"

# Main routing function
route_command() {
    local command="$1"
    shift  # Removes the first argument (the command)
    
    case "$command" in
        archive|a)
            cmd_archive "$@"
            ;;
        archive-names|an)
            cmd_archive_names "$@"
            ;;
        organize|org)
            cmd_organize "$@"
            ;;
        organize-instagram|orgi)
            cmd_organize_instagram "$@"
            ;;
        organize-music|orgm)
            cmd_organize_music "$@"
            ;;
        desorganize|dorg)
            cmd_desorganize "$@"
            ;;
        desorganize-music|dorgm)
            cmd_desorganize_music "$@"
            ;;
        prepare-upload|prep)
            cmd_prepare_upload "$@"
            ;;
        archive-playlist|apl|archive-pro|ap)
            cmd_archive_playlist "$@"
            ;;
        upload|up)
            cmd_upload "$@"
            ;;
        check|c)
            cmd_check "$@"
            ;;
        mass-archive|ma)
            cmd_mass_archive "$@"
            ;;
        mass-archive-names|man)
            cmd_mass_archive_names "$@"
            ;;
        mass-organize|mo)
            cmd_mass_organize "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "Error: unknown command '$command'"
            echo "Use 'vonvakvas help' to see the available commands"
            exit 1
            ;;
    esac
}
