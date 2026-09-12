# Vonvakva's Archive - Technical Documentation

Technical documentation for users and contributors of the project.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Graphical User Interface (GUI)](#graphical-user-interface-gui)
- [Command Line Interface (CLI)](#command-line-interface-cli)
- [Directory Structure](#directory-structure)
- [Workflows](#workflows)
- [Command Reference](#command-reference)
- [Dependencies](#dependencies)
- [Troubleshooting](#troubleshooting)

---

## Installation

### Requirements

| Tool | Required | Description |
|------|----------|-------------|
| python3 (>=3.10) | Yes | GUI Runtime |
| ffmpeg | Yes | Video/audio merging |
| node.js | Recommended | JS runtime for yt-dlp |
| curl | Yes | Channel status monitoring |

### Quick Installation

```bash
./installer.sh

```

This will:

1. Copy the project to `~/.local/opt/vonvakvas-archive`
2. Create a Python virtual environment with required dependencies
3. Generate initial configuration files
4. Create an application menu shortcut

### Manual Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

---

## Configuration

### Configuration Files

All configuration files reside in `config/`:

| File | Purpose |
| --- | --- |
| `channel_list.txt` | List of channels to archive (one per line, `#` for comments) |
| `archive.txt` | Downloaded video history log (managed by yt-dlp) |
| `cookies_1.txt` | Cookies for YouTube Account 1 (Netscape format) |
| `cookies_2.txt` | Cookies for YouTube Account 2 |
| `cookies_3.txt` | Cookies for YouTube Account 3 |
| `telegram.env` | Telegram bot credentials |
| `settings.env` | General settings (channels directory) |

### Cookie Setup

Cookies are used to prevent rate-limiting and blocks from YouTube. To configure:

1. Log in to YouTube on your browser
2. Export cookies in Netscape format (the "Get cookies.txt" extension is recommended)
3. Save the file as `config/cookies_1.txt` (or 2/3 for additional accounts)

The system randomly picks between configured accounts to distribute request load.

### Telegram Setup (Optional)

```bash
cp config/telegram.env.example config/telegram.env

```

Edit the file with your credentials:

```env
TELEGRAM_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

```

### Channels Directory (External HDD)

To use a path other than the default (`your-directory/`):

```bash
# Edit config/settings.env
CHANNELS_ROOT="/path/to/your/directory"

```

---

## Graphical User Interface (GUI)

### Launching

```bash
./start-gui.sh

```

### Views & Pages

#### Dashboard

Archive overview featuring:

* Number of channels on the list
* Total archived videos
* Channels saved before going offline
* Existing channel folders
* Tool status (yt-dlp, ffmpeg, etc.)
* Quick actions (check channels, mass archive)

#### Archive

Download content from YouTube:

* **Channel**: YouTube handle (with or without `@`) — runs the `archive` command
* **Playlist**: Full playlist URL — runs the `archive-playlist` command
* **Mode**: With cookies (rotates through 3 accounts) or ghost mode without cookies (doesn't mark as watched)
* **Buttons**: "Download Channel (archive)" or "Download Playlist (archive-playlist)"

#### Organize

Sort downloaded files into subdirectories:

* **Available Actions**:
* Organize (`organize`) — sorts into `descricao/`, `info_json/`, `thumbs/`, `pfp/`, `videos/`
* Instagram (`organize-instagram`) — same structure without the `pfp/` folder
* Music (`organize-music`) — moves files into `musicas/`
* Undo Organize (`desorganize`) — restores files back to the root folder
* Undo Music (`desorganize-music`) — restores files from `musicas/`
* Prepare IA Upload (`prep`) — builds the `ia/` structure for upload



#### IA Upload

Upload content to the Internet Archive:

* Verifies that the `ia/` directory exists
* Requests channel URL for metadata entry
* Generates automatic Identifier: `<folder>-<date>`
* Populates metadata: channel, creator, title, collection, mediatype

#### Monitor

Check current channel availability:

* Parses all channels from `channel_list.txt`
* Performs HTTP 200 health checks for each entry
* Triggers a Telegram alert if any channel returns an offline status

#### Mass Processing

Batch process the entire list:

* **Mass archive**: downloads all channels using random anti-ban sleep intervals
* **Mass organize**: organizes all folders (respects `.dirignore`)

#### Editor

Modify configuration files directly in the GUI:

* **Cookies (1, 2, and 3)**: edit cookies in Netscape format
* **Channel List**: edit `channel_list.txt`
* **Telegram**: edit `telegram.env` (`token` and `chat_id`)

Uses a dark theme terminal style with monospaced font and one-click saving.

#### Settings

System configuration options:

* Channels storage location (supports external HDDs)
* Visual indicator for active configuration (Project directory vs. Configured directory)
* Copy configuration files from project to an external path

### Console View

The lower terminal pane displays:

* Real-time command output logs
* Execution status updates
* Quick actions: Clear, Stop, Hide/Show

---

## Command Line Interface (CLI)

### Syntax

```bash
./vonvakvas.sh <command> [options]

```

### Examples

```bash
# Download a channel
./vonvakvas.sh archive lofigirl y

# Organize a folder
./vonvakvas.sh organize ./channel-folder

# Health-check channels
./vonvakvas.sh check

# Mass archive the list
./vonvakvas.sh mass-archive

```

---

## Directory Structure

After running the organizer, each channel directory will adhere to this structure:

```text
channel-name/
├── descricao/          # .description files
├── info_json/          # .info.json metadata files
├── pfp/                # Profile picture files (.jpg/.png)
├── thumbs/             # Video thumbnails (.webp)
├── videos/             # Video files (.mp4/.mkv/.webm)
└── ia/                 # (created after prepare-upload)
    ├── itemimage.jpg   # Item cover image
    └── Videos/         # Video copies + metadata

```

---

## Workflows

### 1. Basic Download

```bash
./vonvakvas.sh archive <channel> y

```

### 2. Download + Organize + Upload

```bash
./vonvakvas.sh archive <channel> y
./vonvakvas.sh organize ./channel-folder
./vonvakvas.sh prepare-upload ./channel-folder
./vonvakvas.sh upload ./channel-folder

```

### 3. Mass Sync

```bash
./vonvakvas.sh mass-archive
./vonvakvas.sh mass-organize

```

### 4. Health Check Monitoring

```bash
./vonvakvas.sh check

```

---

## Command Reference

### archive (a)

Downloads videos from a YouTube channel.

```bash
./vonvakvas.sh archive <@channel> [y/n]

```

| Parameter | Required | Description |
| --- | --- | --- |
| `@channel` | Yes | YouTube handle |
| `y / n` | No (default: n) | `y` = use cookies, `n` = ghost mode |

**yt-dlp flags:** Up to 720p, MP4 format, thumbnails, video descriptions, `.info.json`, and embedded metadata.

### archive-playlist (apl)

Downloads a YouTube playlist. Accepts a playlist URL or a channel `@handle`.

```bash
./vonvakvas.sh archive-playlist <playlist-url> [y/n]

```

| Parameter | Required | Description |
| --- | --- | --- |
| `playlist-url` | Yes | Complete playlist URL |
| `y / n` | No (default: n) | `y` = use cookies, `n` = ghost mode |

### organize (org)

Organizes media and metadata files into subfolders by type.

```bash
./vonvakvas.sh organize <directory>

```

**Directory structure created:** `descricao/`, `info_json/`, `thumbs/`, `pfp/`, `videos/`

### organize-instagram (orgi)

Organizes Instagram media (excludes `pfp/` directory).

```bash
./vonvakvas.sh organize-instagram <directory>

```

### organize-music (orgm)

Organizes audio and music files.

```bash
./vonvakvas.sh organize-music <directory>

```

**Directory structure created:** `descricao/`, `info_json/`, `thumbs/`, `pfp/`, `musicas/`

### desorganize (dorg)

Reverts organization (moves all files back to the root folder).

```bash
./vonvakvas.sh desorganize <directory>

```

### desorganize-music (dorgm)

Reverts music directory organization.

```bash
./vonvakvas.sh desorganize-music <directory>

```

### prepare-upload (prep)

Prepares an organized directory for Internet Archive upload.

```bash
./vonvakvas.sh prepare-upload <directory>

```

**Prerequisite:** Folder must be organized containing `videos/`, `descricao/`, and `info_json/`.

**Generates:** `ia/`, `ia/Videos/`, and `ia/<channel>_itemimage.jpg`.

### upload (up)

Uploads content to the Internet Archive.

```bash
./vonvakvas.sh upload <directory>

```

**Prerequisite:** Requires an `ia/` directory (created via `prepare-upload`) and an installed/authenticated `ia` CLI tool.

**Automatic Metadata:**

* `channel`: Channel URL
* `creator`: Channel Name
* `title`: " archive"
* `collection`: opensource_movies
* `mediatype`: movies
* `subject`: youtube;youtuber;youtube-preservation;youtube-videos;asmr

### check (c)

Performs HTTP status checks on all channels listed in `channel_list.txt`.

```bash
./vonvakvas.sh check

```

Sends Telegram alerts if any target channel returns a non-200 status code.

### mass-archive (ma)

Downloads content for all channels defined in `channel_list.txt`.

```bash
./vonvakvas.sh mass-archive

```

**Features:**

* Random sleep intervals (2–10 seconds) between tasks to avoid rate-limiting
* Applies cookie settings uniformly across the batch
* Ignores comments (`#`) and empty lines automatically

### mass-organize (mo)

Organizes all directories in the current working location.

```bash
./vonvakvas.sh mass-organize

```

**Note:** Honors `.dirignore` rules (folders listed will be skipped).

---

## Dependencies

### Python (requirements.txt)

| Package | Version | Purpose |
| --- | --- | --- |
| PySide6 | >=6.6 | Qt Graphical Interface |
| psutil | >=5.9 | Process management |
| yt-dlp | latest | Video processing & downloading |
| internetarchive | latest | Internet Archive API wrapper |

### System Tools

| Tool | Purpose |
| --- | --- |
| ffmpeg | Video and audio remuxing |
| node.js | JS Engine runtime for yt-dlp |
| curl | HTTP requests and network checks |

---

## Troubleshooting

### Error: "This video is available to this channel's members"

**Cause:** Video is restricted to channel members.

**Solution:** Purchase a membership or ignore the warning (the script will skip the video).

### Issue: Logs showing multiple continuous "googlevideo.com" lines

**Cause:** The targeted channel is streaming live at the moment of download.

**Solution:**

1. Wait for the livestream to end and re-run the job
2. Temporarily comment out the channel in `channel_list.txt`

### Error: "Permission denied"

Grant executable permissions to entry scripts:

```bash
chmod +x vonvakvas.sh start-gui.sh

```

### Error: "command not found: yt-dlp"

Ensure `yt-dlp` is installed in your active environment:

```bash
pip install yt-dlp
# or
pip install -r requirements.txt

```

### Upload Fails

1. Ensure `ia/` exists (run `prepare-upload` first)
2. Verify the Internet Archive CLI installation: `ia --version`
3. Check user authentication setup: `ia configure`

### GUI Fails to Start

1. Confirm the Python virtual environment is activated
2. Ensure PySide6 is installed: `pip list | grep PySide6`
3. Launch directly with debug output enabled: `python gui/main.py`
