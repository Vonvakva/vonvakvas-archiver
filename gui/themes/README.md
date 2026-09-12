# GUI Themes — Documentation

Each `.json` file in this directory represents an interface theme. The GUI automatically lists all available themes in the **Themes** tab (no manual registration in code is required — simply drop a JSON file here, and it appears in the app).

## Theme Format

```json
{
  "name": "Pretty Theme Name",
  "description": "One line describing the vibe of the theme",
  "bg": "#0d1017",
  "bg_alt": "#11151f",
  "panel": "#161b26",
  "panel_alt": "#1d2432",
  "border": "#262e40",
  "text": "#e8ebf2",
  "muted": "#8a93a8",
  "accent": "#8b5cf6",
  "accent_hover": "#a78bfa",
  "accent_pressed": "#7c3aed",
  "success": "#4ade80",
  "danger": "#f87171",
  "warning": "#fbbf24",
  "console_bg": "#0a0d13",
  "gif": {
    "header": "",
    "sidebar": "",
    "dashboard": ""
  },
  "extras": {
    "header_text": "",
    "header_text_color": "",
    "sidebar_text": ""
  }
}

```

* `name` and `description` are metadata displayed in the Themes tab.
* The theme **ID** is the filename without the `.json` extension (e.g., `light.json` → ID `light`).
* You **do not need to define every key**: missing values fall back to the default theme (`DEFAULT_COLORS` in `gui/theme.py`). A theme that only changes the accent color can be as short as 3 lines.
* Unknown keys are ignored; invalid JSON causes the theme to be skipped (the GUI will never crash due to a malformed theme file).

## Theme Tokens

| Token | Where it appears |
| --- | --- |
| `bg` | Main window background |
| `bg_alt` | Sidebar, header, input fields, lists |
| `panel` | Cards and panels |
| `panel_alt` | Default buttons, item hover states |
| `border` | Borders across all UI elements |
| `text` | Primary body text |
| `muted` | Secondary text and helper tips |
| `accent` / `accent_hover` / `accent_pressed` | Highlight color (primary buttons, selection highlights, logo) |
| `success` / `danger` / `warning` | Status chips (OK / error / warning) |
| `console_bg` | Console and file editor background |

Translucent chip backgrounds are **not defined in the theme file**: they are derived dynamically from `success`/`danger`/`warning`/`accent` at runtime (`_derived_tokens()` in `theme.py`). Therefore, a light theme automatically gets bright, readable chips.

## Decorations: GIFs, Images, and Text (Optional)

The `"gif"` and `"extras"` sections are **entirely optional** — empty strings (`""`) or missing keys are simply ignored. A theme without decorations functions identically.

### `"gif"` Section — Animations / Images

| Slot | Where it appears |
| --- | --- |
| `gif.header` | Header area, to the right of system info |
| `gif.sidebar` | Sidebar area, beneath the "VONVAKVA'S" logo |
| `gif.dashboard` | Dashboard area, aligned to the right |

Each slot supports **two sources**:

1. **Remote URL** — a direct web URL:
```json
"gif": { "sidebar": "[https://media.tenor.com/xyz/za-hando.gif](https://media.tenor.com/xyz/za-hando.gif)" }

```


Downloaded **only once** to `config/gui_cache/` (saved using the URL hash as the filename, allowing offline persistence after the initial fetch). Supports animated GIFs, PNGs, JPGs, WebPs, and BMPs.
2. **Local File** — filename ONLY, without path:
```json
"gif": { "sidebar": "za_hando.gif" }

```


Requires a **folder matching the JSON filename** inside `gui/themes/`:
```text
gui/themes/
├── terminal.json
└── terminal/            ← folder matching the JSON filename
    └── za_hando.gif

```


If the file is missing, the decoration element simply hides (no error raised).

### `"extras"` Section — Custom Text and Colors

| Key | Description |
| --- | --- |
| `header_text` | Custom string displayed in the header (e.g., file label or tagline) |
| `header_text_color` | Color for `header_text` (Hex format, e.g., `"#22d3ee"`) |
| `sidebar_text` | Extra tagline in the sidebar, underneath the logo |

Example:

```json
"extras": {
  "header_text": "personal archive • do not distribute",
  "header_text_color": "#fbbf24",
  "sidebar_text": "preserving since 2024 :3"
}

```

### Graceful Fallback

In the event of network timeouts, missing local files, or unparseable formats, the decoration widget **silently hides**. Visual decorations will never cause the main application to crash.

## Creating a New Theme (Step-by-Step)

1. Copy `default.json` into a new file, e.g., `mytheme.json` (the theme ID will be `mytheme`).
2. Adjust any desired color values. Tip: Start by tweaking `accent`, `accent_hover`, and `accent_pressed` to quickly refresh the look.
3. Update `name` and `description`.
4. Save the file. In the GUI, navigate to the **Themes** tab → click **Reload list** (or restart the app) → select the theme → click **Apply theme**.
5. The chosen selection persists in `config/gui_state.env` (`GUI_THEME="mytheme"`).

## Theme Resolution Hierarchy (Order of Precedence)

1. `DEFAULT_COLORS` (defined in `gui/theme.py`) — Base default
2. `gui/themes/<active>.json` — Overrides defaults
3. `config/gui_theme.json` — **Manual override**, takes highest priority (useful for quick testing without creating a file; delete when done)

## Contrast Guidelines

* `text` must contrast well against `bg` and `panel`.
* `muted` appears over `bg`/`panel` — keep it clear enough to read easily.
* `accent` buttons feature **white** label text: select an `accent` value with sufficient contrast for light text.
* The terminal panel uses `console_bg` alongside a fixed text color (`#c9d4e8`): keep `console_bg` dark to ensure log outputs remain legible.
