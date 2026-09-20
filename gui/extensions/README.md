# GUI Extensions — Documentation

Extensions are custom Python widgets: a `.py` file in this directory fetches information (from the system, a file, or any source) and the GUI displays it in the **header** (as a compact chip) and/or in the **dashboard** (as a large card), updating periodically.

> ⚠️ **Security Warning:** Extensions are code running directly on your machine under your user account — possessing the same level of trust as the Bash scripts in `scripts/`. Only place `.py` files here that you wrote yourself or completely trust.

## Extension Structure Contract

```python
# gui/extensions/my_widget.py

NAME = "Display Name"            # Required (str)

WHERE = ["header", "dashboard"]   # Required: "header", "dashboard",
                                 # or both

REFRESH = 5                      # Optional: seconds between updates
                                 # (default 5, min 1, max 3600)

def get_value():
    # Required: returns (text, status)
    return ("42°C", "warn")

```

### `get_value()`

* Returns `(text, status)` — or just the text string (the status defaults to `"ok"`).
* **Statuses** (colored according to the active theme):
* `"ok"` — Green (green chip in the header / normal card in the dashboard)
* `"warn"` — Yellow
* `"bad"` — Red
* `"muted"` — Neutral / Gray


* **Must be fast** (~<100ms): runs on the UI thread. Reading a file, calling `psutil`, or executing a subprocess with a short timeout is fine. Downloading files over the internet directly inside `get_value()` is **not** recommended (use an external cache or asynchronous updater instead).

## Directory Rules

| Rule | Effect |
| --- | --- |
| Only `*.py` files are parsed | Other file formats are ignored |
| Filenames starting with `_` | **Will not load** (use for templates — see `_exemplo.py`) |
| Syntax / Import errors | Extension skipped + warning shown in the Extensions tab |
| `get_value()` throws an error | Widget displays "error" (red); GUI continues running |
| Missing `NAME`/`WHERE`/`get_value` | Extension skipped + warning shown |

Extension `id` = filename without the `.py` extension (matches entries in `EXT_DISABLED` inside `config/gui_state.env`).

## Managing via the GUI

**Extensions** Tab:

* Lists all loaded extensions along with their latest values
* **Enable / Disable** — Persisted in `config/gui_state.env` (`EXT_DISABLED="id1,id2"`); disabled extensions are hidden from the header/dashboard but remain in the list
* **Reload** — Rescans the directory (after creating or editing a `.py` file)
* **Open Folder** — Opens the directory in your default file manager

In the terminal: `VONVAKVAS_*` variables will not interfere; to manually disable an extension, simply edit `EXT_DISABLED` (or remove the file from the folder).

## Step-by-Step Example (Fictional GPU Temperature)

1. Create `gui/extensions/gpu_temp.py`:
```python
NAME = "GPU"
WHERE = ["header"]
REFRESH = 10

def get_value():
    with open("/sys/class/drm/card0/temp1_input") as f:
        milli = int(f.read().strip())
    c = milli // 1000
    if c > 85:
        return (f"{c}°C", "bad")
    if c > 70:
        return (f"{c}°C", "warn")
    return (f"{c}°C", "ok")

```


2. Go to Extensions Tab → Click **Reload** → The extension appears in the list (enabled by default).
3. The "GPU: 62°C" chip appears in the header, dynamic in green/yellow/red depending on the temperature, styled using active theme colors.

Tip: `_exemplo.py` in the extensions folder is a ready-to-use template (showing GUI uptime) — copy, rename, and edit it.

## Interactions (Buttons)

To add clickable interactive buttons:

```python
INTERACTIONS = [
    {"id": "play", "label": "▶", "tooltip": "Play"},
    {"id": "pause", "label": "⏸", "tooltip": "Pause"},
]

def on_interaction(interaction_id: str, ext):
    if interaction_id == "play":
        return ("Playing...", "ok")
    return None

```

## Valid Statuses

* `"ok"` - Green (healthy/normal)
* `"warn"` - Yellow (warning)
* `"bad"` - Red (error)
* `"muted"` - Gray (neutral/inactive)

## Sandbox Runtime Rules

* 5-second timeout limit for both `get_value()` and `on_interaction()`
* Executes in an isolated thread (prevents UI freezing)
* Errors inside extensions will NEVER crash the main GUI

## Summary Rules

* Files starting with `_` are ignored (treated as templates)
* `get_value()` must execute quickly (<100ms)
* Use non-blocking `subprocess` for long-running operations
* Extensions refresh dynamically when clicking "Reload" in the GUI

## Complete Example: Music Player

```python
import subprocess

NAME = "🎵 Player"
WHERE = ["dashboard"]
REFRESH = 2

INTERACTIONS = [
    {"id": "prev", "label": "⏮", "tooltip": "Previous"},
    {"id": "play", "label": "▶", "tooltip": "Play"},
    {"id": "pause", "label": "⏸", "tooltip": "Pause"},
    {"id": "next", "label": "⏭", "tooltip": "Next"},
]

_is_playing = False

def get_value():
    if _is_playing:
        return ("Playing", "ok")
    return ("Stopped", "muted")

def on_interaction(interaction_id, ext):
    global _is_playing
    if interaction_id == "play":
        subprocess.Popen(["mpc", "play"])
        _is_playing = True
        return ("Playing", "ok")
    elif interaction_id == "pause":
        subprocess.Popen(["mpc", "pause"])
        _is_playing = False
        return ("Paused", "warn")
    return None

```

## Nerd Fonts and Icons

The GUI supports **Nerd Fonts**! You can use Unicode icons in button labels and widget output text.

### Configuring a Nerd Font

In your theme's JSON file (`gui/themes/<id>.json`), add the `font` configuration block:

```json
{
    "name": "My Custom Theme",
    "font": {
        "family": "JetBrainsMono Nerd Font",
        "size": 13
    },
    "colors": {
        "bg": "#0d1017",
        "accent": "#8b5cf6"
    }
}

```

### Popular Nerd Fonts

* `JetBrainsMono Nerd Font`
* `FiraCode Nerd Font`
* `Hack Nerd Font`
* `SourceCodePro Nerd Font` (CodeNewRoman)
* `UbuntuMono Nerd Font`

### Example with Nerd Font Icons

```python
NAME = "🎵 Player"
WHERE = ["dashboard"]

INTERACTIONS = [
    {"id": "prev", "label": "󰒮", "tooltip": "Previous"},
    {"id": "play", "label": "󰐊", "tooltip": "Play"},
    {"id": "pause", "label": "󰏤", "tooltip": "Pause"},
    {"id": "next", "label": "󰒭", "tooltip": "Next"},
]

```

### Compatibility Matrix

* ✅ Standard Unicode (▶, ⏸, ⏮, ⏭) - Works with any installed font
* ✅ Emojis (🎵, 🔥, 💾) - Works if the font or system supports emoji rendering
* ✅ Nerd Font Icons (󰒮, 󰐊) - Works when a Nerd Font is properly set in the active theme
* ⚠️ If the font lacks a glyph, a missing character box or question mark will be displayed
