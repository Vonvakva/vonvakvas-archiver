# GUI Themes — Documentation

Every `.json` file in this directory represents an interface theme. The GUI automatically lists all themes in the **Themes** tab (no code registration required — just drop a JSON file here and the theme will appear).

## Theme Format

```json
{
  "name": "Nice Theme Name",
  "description": "One-line description of the theme's vibe",
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
* The theme **id** is the filename without `.json` (e.g., `light.json` → id `light`).
* **You do not need to define every key**: missing keys inherit from the default theme (`DEFAULT_COLORS` in `gui/theme.py`). A theme that only changes the accent color can be as short as 3 lines.
* Unknown keys are ignored; invalid JSON causes the theme to be skipped (the GUI will never crash because of a broken theme).

## Color Tokens

| Token | Location / Application |
| --- | --- |
| `bg` | Main window background |
| `bg_alt` | Sidebar, header, text inputs, lists |
| `panel` | Cards and panels |
| `panel_alt` | Regular buttons, item hover states |
| `border` | Borders everywhere |
| `text` | Primary body text |
| `muted` | Secondary text / subtle hints |
| `accent` / `accent_hover` / `accent_pressed` | Accent color (primary buttons, active selections, logo) |
| `success` / `danger` / `warning` | Status chips (OK / error / warning) |
| `console_bg` | Console and file editor background |

Translucent background shades for status chips are **not hardcoded in theme files**: they are dynamically derived from `success`/`danger`/`warning`/`accent` at runtime (`_derived_tokens()` inside `theme.py`). Consequently, light themes automatically generate light-toned status chips.

## Visual Decorators: GIFs, Images, and Custom Text (Optional)

The `"gif"` and `"extras"` sections are **completely optional** — empty strings (`""`) or missing keys are simply ignored. A theme without decorators works perfectly.

### `"gif"` Section — Animations / Images

| Slot | Location |
| --- | --- |
| `gif.header` | Header area, to the right of system info |
| `gif.sidebar` | Sidebar, directly below the "VONVAKVA'S" logo |
| `gif.dashboard` | Dashboard, aligned to the right |

Each slot supports **two sources**:

1. **Internet** — A direct image URL:
```json
"gif": { "sidebar": "https://media.tenor.com/xyz/za-hando.gif" }

```


Downloaded **only once** to `config/gui_cache/` (hashed by URL name, allowing offline persistence without dumping files into `/tmp`). Supports animated GIFs, PNG, JPG, WebP, and BMP.
2. **Local File** — Filename **without path**:
```json
"gif": { "sidebar": "za_hando.gif" }

```


In this case, the theme **must have a subfolder inside `gui/themes/` sharing the EXACT same name as the JSON file**:
```
gui/themes/
├── terminal.json
└── terminal/            ← folder matching JSON name
    └── za_hando.gif

```


If the file is missing, the decoration widget gracefully hides itself without raising errors.

### `"extras"` Section — Text & Colors

| Key | Description |
| --- | --- |
| `header_text` | Custom text inside the header (e.g., file tag, status quote) |
| `header_text_color` | Color for `header_text` (hex, e.g., `"#22d3ee"`) |
| `sidebar_text` | Extra subtitle text in the sidebar below the logo |

Example:

```json
"extras": {
  "header_text": "personal archive • do not distribute",
  "header_text_color": "#fbbf24",
  "sidebar_text": "preserving history since 2024 :3"
}

```

### Error Handling

Broken URLs, missing files, or corrupt image formats will cause the decoration widget to **disappear silently**. Themes and decorations will never crash the GUI.

## Creating a New Theme (Step-by-Step)

1. Copy `default.json` to a new file, e.g., `mytheme.json` (making the theme id `mytheme`).
2. Edit any values you like. Tip: start by tweaking just `accent`, `accent_hover`, and `accent_pressed` to quickly refresh the look.
3. Update `name` and `description`.
4. Save the file. Open the GUI → **Themes** tab → click "Reload list" (or restart) → select your theme → **Apply Theme**.
5. Your selected theme persists in `config/gui_state.env` (`GUI_THEME="mytheme"`).

## Theme Resolution Priority (Hierarchy)

1. `DEFAULT_COLORS` (in `gui/theme.py`) — Fallback base
2. `gui/themes/<active>.json` — Overrides default values
3. `config/gui_theme.json` — **Manual override**, takes ultimate precedence (useful for live-testing colors without editing theme files; delete to restore normal behavior)

## Contrast Guidelines

* Ensure `text` contrasts sharply against `bg` and `panel` (it handles all main body copy).
* `muted` sits over `bg`/`panel` — keep it readable, not too dim.
* `accent` buttons render text in **white**: select an `accent` shade that retains proper contrast against white text.
* The console uses `console_bg` with a fixed light text color (`#c9d4e8`): keep `console_bg` dark for optimal terminal legibility.
