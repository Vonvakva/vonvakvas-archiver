# Vonvakva's Archive - Technical Documentation

Technical documentation for users and contributors of the project.

## Table of Contents

* [Installation](https://www.google.com/search?q=%2523installation&utm_source=gemini)
* [Configuration](https://www.google.com/search?q=%2523configuration&utm_source=gemini)
* [Graphical User Interface (GUI)](https://www.google.com/search?q=%2523graphical-user-interface-gui&utm_source=gemini)
* [Command Line Interface (CLI)](https://www.google.com/search?q=%2523command-line-interface-cli&utm_source=gemini)
* [Folder Structure](https://www.google.com/search?q=%2523folder-structure&utm_source=gemini)
* [Workflows](https://www.google.com/search?q=%2523workflows&utm_source=gemini)
* [Command Reference](https://www.google.com/search?q=%2523command-reference&utm_source=gemini)
* [Dependencies](https://www.google.com/search?q=%2523dependencies&utm_source=gemini)
* [Troubleshooting](https://www.google.com/search?q=%2523troubleshooting&utm_source=gemini)

---

## Installation

### Requirements

| Tool | Required | Description |
| --- | --- | --- |
| python3 (>=3.10) | Yes | GUI runtime |
| ffmpeg | Yes | Video/audio merging |
| node.js | Recommended | yt-dlp runtime |
| curl | Yes | Channel monitoring |

### Quick Installation

```bash
./installer.sh

```

This will:

1. Copy the project to `~/.local/opt/vonvakvas-archive`
2. Create a Python virtual environment with all required dependencies
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

All configuration files are located in `config/`:

| File | Purpose |
| --- | --- |
| `channel_list.txt` | List of channels to archive (one per line, `#` for comments) |
| `archive.txt` | Downloaded video history (managed by yt-dlp) |
| `cookies_1.txt` | YouTube account 1 cookies (Netscape format) |
| `cookies_2.txt` | YouTube account 2 cookies |
| `cookies_3.txt` | YouTube account 3 cookies |
| `telegram.env` | Telegram bot credentials |
| `settings.env` | General settings (channels directory) |

### Cookie Configuration

Cookies are used to bypass YouTube rate limits and restrictions. To set them up:

1. Log into YouTube in your web browser
2. Export your cookies in Netscape format (the "Get cookies.txt" extension is recommended)
3. Save to `config/cookies_1.txt` (or 2/3 for additional accounts)

The system randomly rotates between configured accounts to distribute requests.

### Telegram Setup (Optional)

```bash
cp config/telegram.env.example config/telegram.env

```

Edit the file with your credentials:

```env
TELEGRAM_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

```

### Channels Directory (External HDD)

To use a custom directory instead of the default (`your-directory/`):

```bash
# Edit config/settings.env
CHANNELS_ROOT="/path/to/your/folder"

```

---

## Graphical User Interface (GUI)

### Starting the GUI

```bash
./start-gui.sh

```

### Pages

#### Dashboard

Overview of your archive featuring:

* Number of channels on the list
* Total archived videos
* Saved channels prior to removal
* Existing channel folders
* Tool status (yt-dlp, ffmpeg, etc.)
* Quick actions (check channels, batch archive)

#### Archive

Download from YouTube:

* **Channel**: YouTube handle (with or without `@`) — uses the `archive` command
* **Playlist**: Full playlist URL — uses the `archive-playlist` command
* **Mode**: With cookies (rotation among 3 accounts) or without cookies (stealth mode, does not mark as watched)
* **Buttons**: "Download channel (archive)" or "Download playlist (archive-playlist)"

#### Organize

Organize downloaded files into subfolders:

* **Available actions**:
* Organize (organize) — splits files into `descricao/`, `info_json/`, `thumbs/`, `pfp/`, `videos/`
* Instagram (organize-instagram) — omits the `pfp/` folder
* Music (organize-music) — moves media to `musicas/`
* Undo organization (desorganize) — reverts file organization back to root
* Undo music organization (desorganize-music) — reverts `musicas/` folder
* Prepare AI upload (prep) — creates the `ia/` structure for uploading



#### IA Upload (Internet Archive)

Upload items to the Internet Archive:

* Validates whether the `ia/` folder exists
* Prompts for channel URL to extract metadata
* Automatic identifier: `<folder>-<date>`
* Metadata fields: channel, creator, title, collection, mediatype

#### Monitor

Check current channel status:

* Lists all channels from `channel_list.txt`
* Tests HTTP 200 response for each channel
* Sends a alert notification via Telegram if any channel is offline

#### Mass Processing

Batch process your channel list:

* **Mass archive**: downloads all channels with randomized anti-blocking delay
* **Mass organize**: organizes all folders (respects `.dirignore`)

#### Editor

Edit configuration files directly through the GUI:

* **Cookies (1, 2, and 3)**: edit cookies in Netscape format
* **Channel list**: edit `channel_list.txt`
* **Telegram**: edit `telegram.env` (token and chat_id)

The editor matches the console aesthetic (dark background, monospaced font) and saves with one click.

#### Settings

System preferences:

* Channels storage folder (supports external HDDs)
* active configuration tracker (project folder vs configured folder)
* Copy project configs to external storage

### Console Output

The bottom console pane displays:

* Real-time command output logs
* Execution status updates
* Controls: Clear, Stop, Hide/Show

---

## Command Line Interface (CLI)

### Syntax

```bash
./vonvakvas.sh <command> [options]

```

### Examples

```bash
# Archive a channel
./vonvakvas.sh archive lofigirl y

# Organize a directory
./vonvakvas.sh organize ./channel-folder

# Health-check channels
./vonvakvas.sh check

# Batch archive everything on the list
./vonvakvas.sh mass-archive

```

---

## Folder Structure

Once organized, each channel folder follows this layout:

```text
channel-name/
├── descricao/          # .description files
├── info_json/          # .info.json metadata files
├── pfp/                # Profile picture files (.jpg/.png)
├── thumbs/             # Video thumbnails (.webp)
├── videos/             # Video media (.mp4/.mkv/.webm)
└── ia/                 # (generated after prepare-upload)
    ├── itemimage.jpg   # Item cover image
    └── Videos/         # Video copies + metadata files

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

### 3. Mass Update Batch

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
| `y / n` | No (default: n) | `y` = use cookies, `n` = ghost/stealth mode |

**yt-dlp Flags:** max 720p resolution, mp4 format, thumbnails, descriptions, info.json, embedded metadata.

### archive-playlist (apl)

Downloads a YouTube playlist. Accepts a full playlist URL or a channel handle `@handle`.

```bash
./vonvakvas.sh archive-playlist <playlist-url> [y/n]

```

| Parameter | Required | Description |
| --- | --- | --- |
| `playlist-url` | Yes | Full playlist URL |
| `y / n` | No (default: n) | `y` = use cookies, `n` = stealth mode |

### organize (org)

Organizes loose files into categorised subfolders.

```bash
./vonvakvas.sh organize <folder>

```

**Directory structure created:** `descricao/`, `info_json/`, `thumbs/`, `pfp/`, `videos/`

### organize-instagram (orgi)

Organizes Instagram media (excludes the `pfp/` folder).

```bash
./vonvakvas.sh organize-instagram <folder>

```

### organize-music (orgm)

Organizes audio/music files.

```bash
./vonvakvas.sh organize-music <folder>

```

**Directory structure created:** `descricao/`, `info_json/`, `thumbs/`, `pfp/`, `musicas/`

### desorganize (dorg)

Reverts folder organization (moves all files back to the root level).

```bash
./vonvakvas.sh desorganize <folder>

```

### desorganize-music (dorgm)

Reverts music folder organization.

```bash
./vonvakvas.sh desorganize-music <folder>

```

### prepare-upload (prep)

Prepares an organized folder for uploading to the Internet Archive.

```bash
./vonvakvas.sh prepare-upload <folder>

```

**Requires:** Organized folder containing `videos/`, `descricao/`, `info_json/`

**Creates:** `ia/`, `ia/Videos/`, `ia/<channel>_itemimage.jpg`

### upload (up)

Uploads the content package to the Internet Archive.

```bash
./vonvakvas.sh upload <folder>

```

**Requires:** Existing `ia/` directory (created via `prepare-upload`), installed and configured `ia` CLI tool.

**Automated Metadata:**

* `channel`: Channel URL
* `creator`: Channel name
* `title`: " archive"
* `collection`: opensource_movies
* `mediatype`: movies
* `subject`: youtube;youtuber;youtube-preservation;youtube-videos;asmr

### check (c)

Performs an HTTP status health-check on all channels in the list.

```bash
./vonvakvas.sh check

```

Triggers a Telegram alert notification whenever a channel returns a status code other than 200.

### mass-archive (ma)

Sequentially downloads every channel listed in `channel_list.txt`.

```bash
./vonvakvas.sh mass-archive

```

**Key Features:**

* Randomized sleep delay between channels (2-10 seconds)
* Applies identical cookie configurations across the entire batch
* Ignores comments and blank lines

### mass-organize (mo)

Batch organizes all subdirectories within the current folder.

```bash
./vonvakvas.sh mass-organize

```

**Note:** Respects `.dirignore` rules (folders matching the ignore list are skipped).

---

## Dependencies

### Python (requirements.txt)

| Package | Version | Purpose |
| --- | --- | --- |
| PySide6 | >=6.6 | Qt GUI Framework |
| psutil | >=5.9 | Process management |
| yt-dlp | latest | Video downloader |
| internetarchive | latest | Internet Archive upload CLI |

### System Requirements

| Tool | Purpose |
| --- | --- |
| ffmpeg | Video/Audio muxing & encoding |
| node.js | JavaScript execution runtime (yt-dlp) |
| curl | HTTP network requests |

---

## Troubleshooting

### Error: "This video is available to this channel's members"

**Cause:** The requested video is restricted to channel members only.

**Fix:** Join the channel membership or ignore the warning (the video will be skipped).

### Error: Rapidly repeated "googlevideo.com" lines in output

**Cause:** The target channel is currently broadcasting a live stream.

**Fix:**

1. Wait for the stream to conclude and re-run the process
2. Alternatively, comment out the channel entry in `channel_list.txt` temporarily

### Error: "Permission denied"

```bash
chmod +x vonvakvas.sh start-gui.sh

```

### Error: "command not found: yt-dlp"

```bash
pip install yt-dlp
# or
pip install -r requirements.txt

```

### Upload Failure

1. Ensure the `ia/` folder has been generated (run `prepare-upload` first)
2. Verify that the `ia` CLI is available: `ia --version`
3. Verify your credentials setup: `ia configure`

### GUI Fails to Start

1. Confirm your virtual environment is activated
2. Check if PySide6 is installed: `pip list | grep PySide6`
3. Run with verbose debug mode: `python gui/main.py`
