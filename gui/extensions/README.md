# GUI Extensions — Documentation

Extensions are custom Python widgets: a single `.py` file in this folder collects data (from system metrics, files, or any source) for display in the GUI's **header** (compact chip) and/or **dashboard** (large card), periodically updating on a set interval.

> ⚠️ **Security Warning:** Extensions run code directly on your system under your user permissions — equivalent in security scope to the Bash scripts in `scripts/`. Only run `.py` files that you wrote yourself or explicitly trust.

## Extension Contract

```python
# gui/extensions/my_widget.py

NAME = "Display Name"            # Required (str)

WHERE = ["header", "dashboard"]   # Required: "header", "dashboard", or both

REFRESH = 5                       # Optional: refresh interval in seconds
                                  # (Default: 5, Min: 1, Max: 3600)

def get_value():
    # Required: returns (text, status)
    return ("42°C", "warn")

```

### `get_value()`

* Returns a tuple `(text, status)` — or a plain text string (defaulting status to `"ok"`).
* **Status Options** (dynamically styled according to the active theme):
* `"ok"` — Green (green chip in header / standard card in dashboard)
* `"warn"` — Yellow
* `"bad"` — Red
* `"muted"` — Neutral / Gray


* **Performance Requirement:** Execution must be fast (~<100ms) as it runs on the UI thread. Reading local files, parsing `psutil` data, or running fast subprocess commands with short timeouts is fine. Fetching live network data directly inside `get_value()` is **not recommended** (use background caching mechanisms instead).

## Extension Directory Rules

| Rule | Behavior |
| --- | --- |
| Only `*.py` files are parsed | All other file types are skipped |
| Filenames starting with `_` | **Ignored** (used for templates, e.g., `_exemplo.py`) |
| Syntax / Import errors | Extension is skipped + warning shown in the Extensions tab |
| Unhandled exception in `get_value()` | Widget displays "error" (red); GUI continues running |
| Missing `NAME`, `WHERE`, or `get_value` | Extension is skipped + warning shown |

The extension **ID** is the filename without `.py` (this ID corresponds to entries in `EXT_DISABLED` within `config/gui_state.env`).

## Managing Extensions via GUI

Navigate to the **Extensions** tab to:

* Inspect all loaded extensions alongside their latest reported values.
* **Enable / Disable** extensions (saved to `config/gui_state.env` via `EXT_DISABLED="id1,id2"`). Disabled extensions are removed from the header/dashboard view while remaining in the list.
* **Reload** — Rescan the folder for changes after creating or modifying a `.py` file.
* **Open Folder** — Open the extension directory in your file manager.

## Step-by-Step Example (Fictional GPU Temperature Monitor)

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


2. Open GUI Extensions Tab → Click **Reload** → The extension appears and is enabled by default.
3. The chip "GPU: 62°C" appears in the header with color indicators matching the active theme.

*Tip: `_exemplo.py` in the extensions folder serves as a working template (tracks GUI uptime) — feel free to copy and edit it.*

## Button Interactions

To add clickable UI action controls:

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

## Valid Status Types

* `"ok"` — Green (Healthy)
* `"warn"` — Yellow (Warning)
* `"bad"` — Red (Error)
* `"muted"` — Gray (Neutral / Inactive)

## Execution & Sandbox Environment

* 5-second execution timeout enforced for `get_value()` and `on_interaction()`
* Asynchronous thread execution prevents UI freezing
* Extension runtime errors will **never** crash the main application thread

## Complete Example: Music Player Extension

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

## Nerd Fonts & Custom Icons

The GUI natively supports **Nerd Fonts**! Unicode icons can be used in button labels and widget text outputs.

### Configuring a Nerd Font

In your active theme JSON file (`gui/themes/<id>.json`), configure the `font` parameters:

```json
{
    "name": "My Theme",
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

### Popular Nerd Font Families

* `JetBrainsMono Nerd Font`
* `FiraCode Nerd Font`
* `Hack Nerd Font`
* `SourceCodePro Nerd Font`
* `UbuntuMono Nerd Font`

### Example Using Nerd Font Glyphs

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

### Font Compatibility Matrix

* ✅ **Standard Unicode Symbols** (▶, ⏸, ⏮, ⏭) — Supported across system fonts
* ✅ **Emojis** (🎵, 🔥, 💾) — Rendered properly if system font has emoji support
* ✅ **Nerd Font Glyphs** (󰒮, 󰐊) — Requires a Nerd Font configured in theme settings
* ⚠️ If the configured font lacks a glyph, a fallback rectangle or question mark will render
