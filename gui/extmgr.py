"""Gerenciador das extensões da GUI (gui/extensions/*.py).

CONTRATO DE UMA EXTENSÃO
-------------------------

    NAME = "Nome exibido"            # obrigatório, str
    WHERE = ["header", "dashboard"]  # onde mostrar (obrigatório)
    REFRESH = 5                      # segundos entre atualizações (opcional)
    def get_value():                 # obrigatório, retorna (texto, estado)
        return ("42%", "ok")

    # ---- Interações (opcional) ----
    INTERACTIONS = [
        {"id": "play", "label": "▶", "tooltip": "Tocar"},
        {"id": "pause", "label": "⏸", "tooltip": "Pausar"},
    ]

    def on_interaction(interaction_id: str, ext: Extension):
        if interaction_id == "play":
            return ("Tocando...", "ok")
        return None

Estados válidos: "ok", "warn", "bad" (cores do tema ativo) ou "muted".

SANDBOX: Timeout de 5s, thread separada, nunca derruba a GUI.
"""

from __future__ import annotations
import importlib.util
import threading
import time
from pathlib import Path
from PySide6.QtCore import QObject, QTimer, Signal
import theme

GUI_DIR = Path(__file__).resolve().parent
EXTENSIONS_DIR = GUI_DIR / "extensions"
STATE_FILE = theme.STATE_FILE
VALID_WHERE = {"header", "dashboard"}
DEFAULT_REFRESH = 5
HEADER_LIMIT = 5
SANDBOX_TIMEOUT = 5

class Extension(QObject):
    """Uma extensão carregada, com o último valor lido dela."""

    updated = Signal(str)

    def __init__(self, ext_id, name, where, refresh, get_value, path,
                 interactions=None, on_interaction=None):
        super().__init__()
        self.id = ext_id
        self.name = name
        self.where = where
        self.refresh = refresh
        self.get_value = get_value
        self.path = path
        self.interactions = interactions or []
        self.on_interaction = on_interaction
        self.enabled = True
        self.last_text = "—"
        self.last_state = "muted"
        self.error: str | None = None
        self._due = 0.0

    def has_interactions(self) -> bool:
        """Retorna True se a extensão define botões de interação."""
        return len(self.interactions) > 0

    def tick(self) -> bool:
        """Lê o valor se chegou a hora. Retorna True se mudou algo."""
        if not self.enabled:
            return False
        now = time.monotonic()
        if now < self._due:
            return False
        self._due = now + max(1, self.refresh)
        try:
            result = self._run_sandboxed(self.get_value)
            self.error = None
            if result is None:
                result = ("—", "muted")
            if isinstance(result, tuple) and len(result) == 2:
                text, state = result
            else:
                text, state = result, "ok"
            self.last_text = str(text)
            self.last_state = state if state in ("ok", "warn", "bad", "muted") else "ok"
        except Exception as exc:
            self.error = f"{type(exc).__name__}: {exc}"
            self.last_text = "erro"
            self.last_state = "bad"
        self.updated.emit(self.id)
        return True

    def handle_action(self, action_id: str) -> None:
        """Executa uma ação de forma sandboxed em thread separada."""
        if not self.enabled or self.on_interaction is None:
            return

        def _run():
            try:
                result = self._run_sandboxed(self.on_interaction, action_id, self)
                if isinstance(result, tuple) and len(result) == 2:
                    self.last_text = str(result[0])
                    self.last_state = result[1] if result[1] in ("ok", "warn", "bad", "muted") else "ok"
                    self.updated.emit(self.id)
                elif result is not None:
                    self.last_text = str(result)
                    self.updated.emit(self.id)
            except Exception as exc:
                self.error = f"action {action_id}: {type(exc).__name__}: {exc}"
                self.last_text = "erro"
                self.last_state = "bad"
                self.updated.emit(self.id)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def _run_sandboxed(self, func, *args):
        """Executa função com timeout para proteger a GUI."""
        result = [None]
        error = [None]

        def _target():
            try:
                result[0] = func(*args)
            except Exception as e:
                error[0] = e

        thread = threading.Thread(target=_target, daemon=True)
        thread.start()
        thread.join(timeout=SANDBOX_TIMEOUT)

        if thread.is_alive():
            raise TimeoutError(f"Extensão excedeu {SANDBOX_TIMEOUT}s")

        if error[0] is not None:
            raise error[0]

        return result[0]


def _read_env_value(path: Path, key: str) -> str:
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line.startswith(key):
            _, _, val = line.partition("=")
            return val.strip().strip('"')
    return ""


def _write_env_value(path: Path, key: str, value: str) -> None:
    lines: list[str] = []
    if path.exists():
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    new_line = f'{key}="{value}"'
    for i, line in enumerate(lines):
        if line.strip().startswith(key + "="):
            lines[i] = new_line
            break
    else:
        lines.append(new_line)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def disabled_ids() -> set[str]:
    raw = _read_env_value(STATE_FILE, "EXT_DISABLED")
    return {x.strip() for x in raw.split(",") if x.strip()}


def set_disabled(ids: set[str]) -> None:
    _write_env_value(STATE_FILE, "EXT_DISABLED", ",".join(sorted(ids)))


class ExtensionManager(QObject):
    """Carrega, agenda e disponibiliza as extensões."""

    reloaded = Signal()
    updated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.extensions: dict[str, Extension] = {}
        self.load_errors: list[str] = []

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def load(self) -> None:
        old = self.extensions
        self.extensions = {}
        self.load_errors = []
        disabled = disabled_ids()

        if EXTENSIONS_DIR.is_dir():
            for f in sorted(EXTENSIONS_DIR.glob("*.py")):
                if f.name.startswith("_"):
                    continue
                ext = self._load_file(f)
                if ext is None:
                    continue
                old_ext = old.get(ext.id)
                if old_ext is not None:
                    ext.last_text = old_ext.last_text
                    ext.last_state = old_ext.last_state
                    ext.error = old_ext.error
                ext.enabled = ext.id not in disabled
                self.extensions[ext.id] = ext

        self.reloaded.emit()

    def _load_file(self, path: Path) -> Extension | None:
        try:
            spec = importlib.util.spec_from_file_location(
                f"_vonvakvas_ext_{path.stem}", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as exc:
            self.load_errors.append(f"{path.name}: falhou ao importar ({exc})")
            return None

        name = getattr(mod, "NAME", None)
        where = getattr(mod, "WHERE", None)
        getter = getattr(mod, "get_value", None)

        if not isinstance(name, str) or not name.strip() or not getter:
            self.load_errors.append(
                f"{path.name}: precisa de NAME (str) e get_value()"
            )
            return None

        if not callable(getter):
            self.load_errors.append(
                f"{path.name}: get_value precisa ser callable"
            )
            return None

        if isinstance(where, str):
            where = [where]
        if not isinstance(where, (list, tuple)) or not where:
            where = ["dashboard"]
        where = [w for w in where if w in VALID_WHERE] or ["dashboard"]

        try:
            refresh = int(getattr(mod, "REFRESH", DEFAULT_REFRESH))
        except (TypeError, ValueError):
            refresh = DEFAULT_REFRESH
        refresh = min(max(refresh, 1), 3600)

        # ---- Interações (opcional) ----
        interactions: list[dict] = []
        raw_interactions = getattr(mod, "INTERACTIONS", None)
        if raw_interactions is not None:
            if not isinstance(raw_interactions, (list, tuple)):
                self.load_errors.append(
                    f"{path.name}: INTERACTIONS deve ser lista"
                )
            else:
                for item in raw_interactions:
                    if isinstance(item, dict) and "id" in item and "label" in item:
                        interactions.append(item)
                    else:
                        self.load_errors.append(
                            f"{path.name}: item inválido em INTERACTIONS: {item}"
                        )

        on_interaction = getattr(mod, "on_interaction", None)
        if interactions and on_interaction and not callable(on_interaction):
            self.load_errors.append(
                f"{path.name}: on_interaction precisa ser callable"
            )
            on_interaction = None

        return Extension(
            path.stem, name.strip(), where, refresh, getter, path,
            interactions=interactions or None,
            on_interaction=on_interaction,
        )

    def set_enabled(self, ext_id: str, enabled: bool) -> None:
        ext = self.extensions.get(ext_id)
        if ext is not None:
            ext.enabled = enabled
            ext._due = 0.0
        disabled = disabled_ids()
        if enabled:
            disabled.discard(ext_id)
        else:
            disabled.add(ext_id)
        set_disabled(disabled)
        self.reloaded.emit()

    def by_where(self, place: str) -> list[Extension]:
        return [
            e for e in self.extensions.values()
            if e.enabled and place in e.where
        ]

    def _tick(self) -> None:
        changed = False
        for ext in list(self.extensions.values()):
            if ext.tick():
                changed = True
        if changed:
            self.updated.emit()


_manager = None


def get_manager() -> ExtensionManager:
    """Singleton do manager (crie após o QApplication)."""
    global _manager
    if _manager is None:
        _manager = ExtensionManager()
        _manager.load()
    return _manager
