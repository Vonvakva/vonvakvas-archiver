"""Sistema de temas da GUI do Vonvakva's Archive.

COMO FUNCIONA
-------------
O estilo da interface é um grande bloco QSS com placeholders @nome
(ex: @bg, @accent). O build_qss() substitui cada placeholder pelo valor
do token no tema ATIVO.

Um tema é um arquivo JSON dentro de gui/themes/. Ele pode definir todas
as chaves de DEFAULT_COLORS ou só as que quiser sobrescrever — o resto
cai no padrão. Veja documentação completa e exemplos em:

    gui/themes/README.md

Prioridade de resolução das cores:
    1. tema escolhido (gui/themes/<id>.json) sobre DEFAULT_COLORS
    2. config/gui_theme.json (override manual, tem a palavra final)

O tema escolhido fica salvo em config/gui_state.env (GUI_THEME="id"),
junto com o perfil ativo. Tokens derivados (fundo translúcido dos
chips, por exemplo) são calculados a partir das cores do tema — então
qualquer tema novo fica consistente automaticamente.
"""

from __future__ import annotations

import json
from pathlib import Path

GUI_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = GUI_DIR.parent
THEMES_DIR = GUI_DIR / "themes"
STATE_FILE = PROJECT_ROOT / "config" / "gui_state.env"
# Override manual (opcional): tem prioridade sobre o tema escolhido.
# Mantido por compatibilidade com versões anteriores do theme.py.
OVERRIDE_FILE = PROJECT_ROOT / "config" / "gui_theme.json"

DEFAULT_THEME_ID = "default"

# Slots de decoração (opcionais). Cada valor é:
#   - "" (vazio/ausente)  -> ignorado
#   - "http(s)://..."     -> baixado para config/gui_cache/ (cache por hash)
#   - "arquivo.gif"       -> procurado em gui/themes/<id>/ (pasta com o
#                            MESMO NOME do json do tema)
GIF_SLOTS = ["header", "sidebar", "dashboard"]

# Extras de personalização (opcionais, todos ignorados se vazios)
EXTRA_KEYS = ["header_text", "header_text_color", "sidebar_text"]

DEFAULT_COLORS = {
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
}

# Fonte padrão da GUI (pode ser sobrescrita pelo tema)
# Use uma Nerd Font para ícones extras: "JetBrainsMono Nerd Font", "FiraCode Nerd Font", etc.
DEFAULT_FONT_FAMILY = "Sans Serif"
DEFAULT_FONT_SIZE = 13


# ---------------------------------------------------------------------------
# Carregamento de temas
# ---------------------------------------------------------------------------

def list_themes() -> list[dict]:
    """Temas disponíveis em gui/themes/*.json.

    Retorna lista de dicts: {id, name, description, colors}.
    Sempre inclui o tema padrão, mesmo que o arquivo dele sumir.
    """
    themes: list[dict] = []
    if THEMES_DIR.is_dir():
        for f in sorted(THEMES_DIR.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue  # tema quebrado: pula sem derrubar a GUI
            if not isinstance(data, dict):
                continue
            colors = {
                k: v for k, v in data.items()
                if k in DEFAULT_COLORS and isinstance(v, str)
            }
            themes.append({
                "id": f.stem,
                "name": str(data.get("name", f.stem)),
                "description": str(data.get("description", "")),
                "colors": {**DEFAULT_COLORS, **colors},
                "font": data.get("font", {}),
                "gif": _decor_section(data.get("gif"), GIF_SLOTS),
                "extras": _decor_section(data.get("extras"), EXTRA_KEYS),
            })
    if not any(t["id"] == DEFAULT_THEME_ID for t in themes):
        themes.insert(0, {
            "id": DEFAULT_THEME_ID,
            "name": "Padrão",
            "description": "dark violeta padrão da GUI",
            "colors": dict(DEFAULT_COLORS),
            "gif": {},
            "extras": {},
        })
    return themes


def _decor_section(raw, allowed_keys: list[str]) -> dict:
    """Valida a seção gif/extras: só chaves conhecidas, strings não vazias."""
    out: dict[str, str] = {}
    if not isinstance(raw, dict):
        return out
    for key, value in raw.items():
        if key in allowed_keys and isinstance(value, str) and value.strip():
            out[key] = value.strip()
    return out


def load_theme_meta(theme_id: str | None = None) -> dict:
    """Metadados completos do tema (cores + gif + extras), com fallback.

    Os valores da seção gif já vêm resolvidos: URLs passam direto,
    arquivos viram caminho absoluto dentro de gui/themes/<id>/.
    """
    target = theme_id if theme_id is not None else get_active_theme_id()
    for t in list_themes():
        if t["id"] == target:
            meta = dict(t)
            meta["gif"] = {
                k: resolve_asset(target, v)
                for k, v in t.get("gif", {}).items()
            }
            return meta
    return {
        "id": DEFAULT_THEME_ID,
        "name": "Padrão",
        "description": "",
        "colors": dict(DEFAULT_COLORS),
        "gif": {},
        "extras": {},
    }


def resolve_asset(theme_id: str | None, value: str) -> str:
    """Resolve o valor de um slot de decoração.

    - URL http(s): devolvida como está (o widget baixa para o cache).
    - Caminho/arquivo: resolvido relativo a gui/themes/<id>/ e devolvido
      como caminho absoluto (em string, mesmo se ainda não existir).
    """
    if value.startswith("http://") or value.startswith("https://"):
        return value
    base = THEMES_DIR / (theme_id or DEFAULT_THEME_ID)
    return str(base / value)


def load_theme_colors(theme_id: str | None = None) -> dict:
    """Cores do tema pedido (ou do ativo), com fallback no padrão."""
    target = theme_id if theme_id is not None else get_active_theme_id()
    for t in list_themes():
        if t["id"] == target:
            return dict(t["colors"])
    return dict(DEFAULT_COLORS)


def load_theme_font(theme_id: str | None = None) -> dict:
    """Fonte do tema pedido (ou do ativo), com fallback no padrão.
    Retorna dict com 'family' e 'size'."""
    target = theme_id if theme_id is not None else get_active_theme_id()
    for t in list_themes():
        if t["id"] == target:
            font = t.get("font", {})
            return {
                "family": str(font.get("family", DEFAULT_FONT_FAMILY)),
                "size": int(font.get("size", DEFAULT_FONT_SIZE)),
            }
    return {"family": DEFAULT_FONT_FAMILY, "size": DEFAULT_FONT_SIZE}


# ---------------------------------------------------------------------------
# Tema ativo (persistido em config/gui_state.env, junto do perfil)
# ---------------------------------------------------------------------------

def get_active_theme_id() -> str:
    if not STATE_FILE.exists():
        return DEFAULT_THEME_ID
    for line in STATE_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line.startswith("GUI_THEME"):
            _, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            if val:
                return val
    return DEFAULT_THEME_ID


def set_active_theme_id(theme_id: str) -> None:
    """Salva o tema escolhido preservando as outras linhas do arquivo."""
    lines: list[str]
    if STATE_FILE.exists():
        lines = STATE_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
    else:
        lines = ["# Estado da GUI (perfil ativo / tema). Arquivo somente da interface."]
    new_line = f'GUI_THEME="{theme_id or DEFAULT_THEME_ID}"'
    for i, line in enumerate(lines):
        if line.strip().startswith("GUI_THEME"):
            lines[i] = new_line
            break
    else:
        lines.append(new_line)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def resolve_colors(theme_id: str | None = None) -> dict:
    """Cores finais: tema escolhido + overrides de config/gui_theme.json."""
    colors = load_theme_colors(theme_id)
    if OVERRIDE_FILE.is_file():
        try:
            custom = json.loads(OVERRIDE_FILE.read_text(encoding="utf-8"))
            for key, value in custom.items():
                if key in colors and isinstance(value, str):
                    colors[key] = value
        except (json.JSONDecodeError, OSError):
            pass  # override quebrado/ilegivel: ignora
    return colors


_QSS = """
* { outline: none; font-family: @font_family; font-size: @font_size; }

QWidget {
    background-color: @bg;
    color: @text;
    font-size: @font_size;
    selection-background-color: @accent;
    selection-color: #ffffff;
}

QMainWindow { background-color: @bg; }
QScrollArea { background: transparent; border: none; }
QScrollArea > QWidget > QWidget { background: transparent; }

QWidget#sidebar {
    background-color: @bg_alt;
    border-right: 1px solid @border;
}
QWidget#header {
    background-color: @bg_alt;
    border-bottom: 1px solid @border;
}

QLabel { background: transparent; }
QLabel#logo {
    font-size: 19px;
    font-weight: 800;
    letter-spacing: 2px;
    color: @accent;
}
QLabel#logoSub {
    font-size: 12px;
    color: @muted;
    letter-spacing: 3px;
}
QLabel#h1 { font-size: 22px; font-weight: 700; }
QLabel#h2 { font-size: 15px; font-weight: 600; }
QLabel#muted { color: @muted; }
QLabel#cardTitle {
    font-size: 11px;
    font-weight: 700;
    color: @muted;
    letter-spacing: 2px;
}
QLabel#statValue { font-size: 26px; font-weight: 700; }
QLabel#consoleStatus { color: @muted; font-size: 12px; }
QLabel#busy { color: @warning; font-size: 12px; font-weight: 700; }
QLabel#headerLbl { color: @muted; font-size: 12px; }
QLabel#headerLbl b { color: @text; font-weight: 600; }

QFrame#card, QFrame#statCard {
    background-color: @panel;
    border: 1px solid @border;
    border-radius: 12px;
}
"""  # __QSS_PART2__

# Parte 2 do QSS (botoes, inputs, console, chips, scrollbars...) e a funcao
# build_qss() sao anexadas abaixo por build_qss(), montadas em duas partes
# para manter este arquivo organizado. Veja _QSS2 e build_qss() no fim.
_QSS2 = """
QPushButton {
    background-color: @panel_alt;
    color: @text;
    border: 1px solid @border;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}
QPushButton:hover { border-color: @accent; }
QPushButton:pressed { background-color: @accent_pressed; }
QPushButton:disabled {
    color: @muted;
    background-color: @bg_alt;
    border-color: @border;
}
QPushButton#accent {
    background-color: @accent;
    border: none;
    color: #ffffff;
}
QPushButton#accent:hover { background-color: @accent_hover; }
QPushButton#accent:pressed { background-color: @accent_pressed; }
QPushButton#accent:disabled { background-color: @accent_pressed; color: rgba(255,255,255,0.5); }
QPushButton#danger {
    background: transparent;
    border: 1px solid @danger;
    color: @danger;
}
QPushButton#danger:hover { background-color: @danger; color: #10131a; }
QPushButton#ghost {
    background: transparent;
    border: none;
    color: @muted;
    padding: 4px 8px;
    font-weight: 600;
}
QPushButton#ghost:hover { color: @text; }

QPushButton#navBtn {
    text-align: left;
    padding: 10px 14px;
    border: none;
    border-radius: 10px;
    color: @muted;
    background: transparent;
    font-weight: 600;
    font-size: @font_size;
}
QPushButton#navBtn:hover { background-color: @panel_alt; color: @text; }
QPushButton#navBtn:checked {
    background-color: @panel_alt;
    color: @accent_hover;
    border-left: 3px solid @accent;
}

QLineEdit, QComboBox, QSpinBox {
    background-color: @bg_alt;
    border: 1px solid @border;
    border-radius: 8px;
    padding: 8px 10px;
    color: @text;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border-color: @accent; }
QLineEdit:disabled, QComboBox:disabled { color: @muted; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background-color: @panel;
    border: 1px solid @border;
    border-radius: 8px;
    selection-background-color: @accent;
    selection-color: #ffffff;
    outline: none;
}

QPlainTextEdit#console, QPlainTextEdit#fileEdit {
    background-color: @console_bg;
    color: #c9d4e8;
    border: 1px solid @border;
    border-radius: 10px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
    font-size: 12px;
}

QListWidget {
    background-color: @bg_alt;
    border: 1px solid @border;
    border-radius: 10px;
    padding: 4px;
    outline: none;
}
QListWidget::item { padding: 6px 8px; border-radius: 6px; }
QListWidget::item:hover { background-color: @panel_alt; }
QListWidget::item:selected { background-color: @accent; color: #ffffff; }

QLabel#chipOk, QLabel#chipBad, QLabel#chipWarn, QLabel#chipMuted, QLabel#chipAccent {
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 12px;
    font-weight: 600;
}
QLabel#chipOk {
    color: @success;
    background-color: @chip_ok_bg;
    border: 1px solid @chip_ok_border;
}
QLabel#chipBad {
    color: @danger;
    background-color: @chip_bad_bg;
    border: 1px solid @chip_bad_border;
}
QLabel#chipWarn {
    color: @warning;
    background-color: @chip_warn_bg;
    border: 1px solid @chip_warn_border;
}
QLabel#chipMuted {
    color: @muted;
    background-color: @bg_alt;
    border: 1px solid @border;
}
QLabel#chipAccent {
    color: @accent_hover;
    background-color: @chip_accent_bg;
    border: 1px solid @chip_accent_border;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: @border;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: @muted; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background: @border;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: @muted; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }

QSplitter::handle { background-color: @bg; height: 4px; }

QToolTip {
    background-color: @panel;
    color: @text;
    border: 1px solid @border;
    padding: 4px 8px;
    border-radius: 6px;
}

QMessageBox { background-color: @panel; }
QMessageBox QLabel { background: transparent; }
"""


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Converte '#rrggbb' em 'rgba(r, g, b, alpha)' (para fundos translúcidos)."""
    h = hex_color.strip().lstrip("#")
    if len(h) != 6:
        return hex_color  # cor estranha: devolve como veio
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except ValueError:
        return hex_color
    return f"rgba({r}, {g}, {b}, {alpha})"


def _derived_tokens(colors: dict) -> dict:
    """Tokens calculados a partir do tema (fundo translúcido dos chips)."""
    return {
        "chip_ok_bg": _hex_to_rgba(colors["success"], 0.10),
        "chip_ok_border": _hex_to_rgba(colors["success"], 0.35),
        "chip_bad_bg": _hex_to_rgba(colors["danger"], 0.10),
        "chip_bad_border": _hex_to_rgba(colors["danger"], 0.35),
        "chip_warn_bg": _hex_to_rgba(colors["warning"], 0.10),
        "chip_warn_border": _hex_to_rgba(colors["warning"], 0.35),
        "chip_accent_bg": _hex_to_rgba(colors["accent"], 0.10),
        "chip_accent_border": _hex_to_rgba(colors["accent"], 0.40),
    }


def build_qss() -> str:
    """Monta o QSS final substituindo os tokens do tema ativo."""
    colors = resolve_colors()
    font = load_theme_font()
    tokens = {
        **colors,
        **_derived_tokens(colors),
        "font_family": font["family"],
        "font_size": f"{font['size']}px",
    }
    qss = _QSS + _QSS2
    # Substitui os nomes mais longos primeiro (@bg_alt antes de @bg)
    for name in sorted(tokens, key=len, reverse=True):
        qss = qss.replace("@" + name, tokens[name])
    return qss
