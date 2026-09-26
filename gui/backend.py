"""Bridge between the GUI and the Bash backend (vonvakvas.sh).

The GUI does NOT implement the scripts logic: it only calls the CLI
`./vonvakvas.sh <command> [options]` via QProcess, as the project rules
require (for-the-model/agentrules.md). Reading/writing config/ is only for:
dashboard, file editor, settings and profiles.

Profiles: each profile in config/profiles/<name>/ isolates the config files
(channel_list.txt, cookies, telegram.env, archive.txt, settings.env). The
active profile is passed to the backend through the VONVAKVAS_PROFILE
environment variable — the project common.sh resolves the priority:
profile -> CHANNELS_ROOT/config -> project config/.
"""

from __future__ import annotations

import datetime
import os
import platform
import re
import shutil
import socket
from pathlib import Path

import psutil
from PySide6.QtCore import QObject, QProcess, QProcessEnvironment, Signal

GUI_DIR = Path(__file__).resolve().parent


def _detect_root() -> Path:
    """Walks up the tree until it finds .projectroot or config/ (same rule as common.sh)."""
    p = GUI_DIR
    while p != p.parent:
        if (p / ".projectroot").exists() or (p / "config").is_dir():
            return p
        p = p.parent
    return GUI_DIR.parent


PROJECT_ROOT = _detect_root()
VONVAKVAS_SH = PROJECT_ROOT / "vonvakvas.sh"
CONFIG_DIR = PROJECT_ROOT / "config"
PROFILES_DIR = CONFIG_DIR / "profiles"
SETTINGS_FILE = CONFIG_DIR / "settings.env"
GUI_STATE_FILE = CONFIG_DIR / "gui_state.env"
DEFAULT_WORKDIR = PROJECT_ROOT / "your-directory"
# Venv where the `ia` CLI (Internet Archive upload) lives
IA_VENV = Path("/home/flucio/venvs/internetarchive")

# Config files that can live on the HDD (same list as the common.sh fallback)
CONFIG_FILES = [
    "archive.txt",
    "cookies_1.txt",
    "cookies_2.txt",
    "cookies_3.txt",
    "channel_list.txt",
    "telegram.env",
]

# Files editable in the Editor tab.
#   scope "auto":    follows the backend config_path (profile -> HDD -> project)
#   scope "global":  always the project config/ (shared between profiles)
#   scope "workdir": lives in the channels folder (CHANNELS_ROOT), not in config/
EDITOR_FILES = [
    {"name": "channel_list.txt", "scope": "auto",
     "desc": "Channels to archive (one @ per line, # = comment)"},
    {"name": "cookies_1.txt", "scope": "auto",
     "desc": "Cookies of YouTube account 1 (Netscape format)"},
    {"name": "cookies_2.txt", "scope": "auto",
     "desc": "Cookies of YouTube account 2"},
    {"name": "cookies_3.txt", "scope": "auto",
     "desc": "Cookies of YouTube account 3"},
    {"name": "telegram.env", "scope": "auto",
     "desc": "Telegram bot credentials (TELEGRAM_TOKEN/CHAT_ID)"},
    {"name": "settings.env", "scope": "auto",
     "desc": "Local settings (CHANNELS_ROOT) — active profile scope"},
    {"name": "archive.txt", "scope": "auto",
     "desc": "yt-dlp download history (large file)"},
    {"name": "succeeded_archvings.txt", "scope": "global",
     "desc": "Channels saved before going down (global, all profiles)"},
    {"name": ".dirignore", "scope": "workdir",
     "desc": "Folders ignored by mass-organize (one per line)"},
]

_PROFILE_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9 _-]{0,39}$")

# ---------------------------------------------------------------------------
# Config reading (read-only, for display)
# ---------------------------------------------------------------------------

def _read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def read_channel_list() -> list[str]:
    """Channels from the list (active profile -> HDD -> project)."""
    return _read_lines(effective_config_path("channel_list.txt"))


def archive_history_count() -> int:
    """Already downloaded videos (effective archive.txt)."""
    return len(_read_lines(effective_config_path("archive.txt")))


def successful_channels() -> list[str]:
    """Channels archived successfully before going down (stays in the project)."""
    return _read_lines(CONFIG_DIR / "succeeded_archvings.txt")


def list_channel_dirs() -> list[str]:
    """Channel folders inside the configured channels folder."""
    base = channels_dir()
    if not base.is_dir():
        return []
    return sorted(
        d.name for d in base.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def tool_status() -> dict[str, bool]:
    """Status of the tools/files the backend uses (effective locations)."""
    return {
        "yt-dlp": shutil.which("yt-dlp") is not None,
        "ia CLI": (
            shutil.which("ia") is not None or (IA_VENV / "bin" / "ia").is_file()
        ),
        "cookies 1": effective_config_path("cookies_1.txt").exists(),
        "cookies 2": effective_config_path("cookies_2.txt").exists(),
        "cookies 3": effective_config_path("cookies_3.txt").exists(),
        "telegram.env": effective_config_path("telegram.env").exists(),
    }


# ---------------------------------------------------------------------------
# System (header extras)
# ---------------------------------------------------------------------------

def hostname() -> str:
    return socket.gethostname()


def os_name() -> str:
    system = platform.system() or "?"
    release = (platform.release() or "").split("-")[0]
    return f"{system} {release}".strip()


def date_now() -> str:
    return datetime.datetime.now().strftime("%a %d/%m/%Y • %H:%M")


def _existing_ancestor(path: Path) -> Path:
    """Walks up until it finds an existing directory (psutil.disk_usage requires it)."""
    p = path
    while not p.exists() and p != p.parent:
        p = p.parent
    return p


def disk_usage(path: Path | None = None) -> tuple[int, int]:
    """(free, total) in bytes of the device hosting the channels folder."""
    target = _existing_ancestor(path or channels_dir())
    try:
        usage = psutil.disk_usage(str(target))
        return usage.free, usage.total
    except (OSError, PermissionError):
        return 0, 0


def fmt_bytes(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024 or unit == "TB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024
    return f"{n:.1f} TB"


# ---------------------------------------------------------------------------
# File editor (profile aware)
# ---------------------------------------------------------------------------

def editor_entry(name: str) -> dict | None:
    for entry in EDITOR_FILES:
        if entry["name"] == name:
            return entry
    return None


def editor_read_path(name: str) -> Path:
    """Effective file the Editor loads (config_path rule)."""
    entry = editor_entry(name) or {"name": name, "scope": "auto"}
    if entry["scope"] == "global":
        return CONFIG_DIR / name
    if entry["scope"] == "workdir":
        return channels_dir() / name
    return effective_config_path(name)


def editor_save_path(name: str) -> Path:
    """Where the Editor writes: to the active profile (creating if needed) or to the project."""
    entry = editor_entry(name) or {"name": name, "scope": "auto"}
    if entry["scope"] == "global":
        return CONFIG_DIR / name
    if entry["scope"] == "workdir":
        return channels_dir() / name
    pdir = profile_dir()
    if pdir is not None:
        return pdir / name
    return CONFIG_DIR / name


def read_editor_file(name: str) -> str:
    path = editor_read_path(name)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def write_editor_file(name: str, content: str) -> Path:
    path = editor_save_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Profiles: definitions (the active profile lives in config/gui_state.env —
# shared with the CLI, see 'vonvakvas profile use')
# ---------------------------------------------------------------------------

def active_profile() -> str | None:
    """Active profile name (None = use the project default config/).

    Re-reads config/gui_state.env on every call: the CLI can switch the
    profile (vonvakvas profile use) while the GUI is open, and both sides
    must always agree on the active one.
    """
    return _load_active_profile()


def set_active_profile(name: str | None) -> None:
    """Sets the active profile and persists it to config/gui_state.env.

    That file is shared with the CLI ('vonvakvas profile use' writes the same
    GUI_PROFILE key), so both sides always agree. Preserves the other lines of
    the file (e.g. GUI_THEME from the theme system).
    """
    _set_env_value(
        GUI_STATE_FILE,
        "GUI_PROFILE",
        (name or "").strip(),
        "# GUI state (active profile / theme). Interface-only file.\n",
    )


def _load_active_profile() -> str | None:
    if not GUI_STATE_FILE.exists():
        return None
    for line in GUI_STATE_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line.startswith("GUI_PROFILE"):
            _, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            return val or None
    return None


def list_profiles() -> list[str]:
    if not PROFILES_DIR.is_dir():
        return []
    return sorted(
        d.name for d in PROFILES_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def profile_dir(name: str | None = None) -> Path | None:
    """Profile path (active, if name=None). None if no profile."""
    target = name if name is not None else active_profile()
    if not target:
        return None
    return PROFILES_DIR / target


def validate_profile_name(name: str) -> str | None:
    """Returns an error message, or None if the name is valid."""
    name = name.strip()
    if not name:
        return "Type a name for the profile."
    if not _PROFILE_NAME_RE.match(name):
        return (
            "Invalid name. Use letters, numbers, spaces, hyphen or underscore "
            "(max. 40 characters, starting with a letter/number)."
        )
    if (PROFILES_DIR / name).exists():
        return f"There is already a profile named '{name}'."
    return None


def create_profile(name: str, copy_base: bool = True) -> Path:
    """Creates config/profiles/<name>/ and, optionally, copies the base config.

    Does NOT copy archive.txt: each profile is an independent instance, with
    its own history (if you want to inherit the history, copy it manually).
    """
    pdir = PROFILES_DIR / name.strip()
    pdir.mkdir(parents=True, exist_ok=True)
    if copy_base:
        for fname in ("channel_list.txt", "cookies_1.txt", "cookies_2.txt",
                      "cookies_3.txt", "telegram.env"):
            src = CONFIG_DIR / fname
            dst = pdir / fname
            if src.is_file() and not dst.exists():
                shutil.copy2(src, dst)
    return pdir


def delete_profile(name: str) -> None:
    if name == active_profile():
        raise ValueError("Cannot delete the active profile.")
    shutil.rmtree(PROFILES_DIR / name)


def profile_files(name: str) -> list[str]:
    """Config files present in a profile."""
    pdir = PROFILES_DIR / name
    if not pdir.is_dir():
        return []
    return sorted(p.name for p in pdir.iterdir() if p.is_file())


# ---------------------------------------------------------------------------
# Settings: channels folder (can be an external HDD) — per profile
# ---------------------------------------------------------------------------

def _read_env_value(path: Path, key: str) -> str:
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line.startswith(key):
            _, _, val = line.partition("=")
            return val.strip().strip('"').strip("'")
    return ""


def _set_env_value(path: Path, key: str, value: str, header: str) -> None:
    """Updates (or appends) KEY=VALUE preserving the rest of the file."""
    lines: list[str]
    if path.exists():
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    else:
        lines = header.splitlines()
    new_line = f'{key}="{value}"'
    for i, line in enumerate(lines):
        if line.strip().startswith(key):
            lines[i] = new_line
            break
    else:
        lines.append(new_line)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_channels_root() -> Path | None:
    """Reads the effective CHANNELS_ROOT: profile settings.env > project (None if empty)."""
    value = ""
    pdir = profile_dir()
    if pdir is not None:
        value = _read_env_value(pdir / "settings.env", "CHANNELS_ROOT")
    if not value:
        value = _read_env_value(SETTINGS_FILE, "CHANNELS_ROOT")
    return Path(value).expanduser() if value else None


def channels_root_scope() -> str:
    """Where the effective CHANNELS_ROOT comes from: 'profile', 'project' or 'default'."""
    pdir = profile_dir()
    if pdir is not None and _read_env_value(pdir / "settings.env", "CHANNELS_ROOT"):
        return "profile"
    if _read_env_value(SETTINGS_FILE, "CHANNELS_ROOT"):
        return "project"
    return "default"


def write_channels_root(path: str | None) -> None:
    """Writes CHANNELS_ROOT to the active scope (profile if active, else project)."""
    header = (
        "# Vonvakva's Archive - local settings (written by the GUI)\n"
        "# Folder where the channels are stored (can be an external HDD).\n"
        "# If <folder>/config/ exists, the files there take priority\n"
        "# (per-file fallback to the project config/).\n"
    )
    pdir = profile_dir()
    target = (pdir / "settings.env") if pdir is not None else SETTINGS_FILE
    _set_env_value(target, "CHANNELS_ROOT", path or "", header)


def channels_dir() -> Path:
    """Folder where the channels are stored/downloaded (HDD if configured)."""
    root = load_channels_root()
    if root is not None and root.is_dir():
        return root
    return DEFAULT_WORKDIR


def effective_config_path(name: str) -> Path:
    """Same rule as the common.sh config_path() (profile -> HDD -> project)."""
    pdir = profile_dir()
    if pdir is not None and (pdir / name).is_file():
        return pdir / name
    root = load_channels_root()
    if (
        root is not None
        and root != PROJECT_ROOT
        and (root / "config" / name).is_file()
    ):
        return root / "config" / name
    return CONFIG_DIR / name


def missing_config_files(root: Path) -> list[str]:
    """Config files missing in <root>/config/."""
    cfg = root / "config"
    return [n for n in CONFIG_FILES if not (cfg / n).exists()]


def copy_project_configs(root: Path) -> list[str]:
    """Copies the project configs missing in <root>/config/ (without overwriting)."""
    cfg = root / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in CONFIG_FILES:
        src = CONFIG_DIR / name
        dst = cfg / name
        if src.is_file() and not dst.exists():
            shutil.copy2(src, dst)
            copied.append(name)
    return copied

# ---------------------------------------------------------------------------
# Runner: runs the vonvakvas.sh CLI in the background with live output
# ---------------------------------------------------------------------------

def _apply_child_env(proc: QProcess) -> None:
    """Prepares the environment of the child processes.

    1. Propagates VONVAKVAS_PROFILE so common.sh uses the profile config.
    2. Makes sure the children find the `ia` CLI of the internetarchive
       venv: uploaderf.sh calls `ia` directly; we append its bin to the
       END of the PATH (so it never shadows the project venv yt-dlp/python).
    """
    env = QProcessEnvironment.systemEnvironment()
    profile = active_profile() or ""
    if profile:
        env.insert("VONVAKVAS_PROFILE", profile)
    else:
        env.remove("VONVAKVAS_PROFILE")
    bin_dir = IA_VENV / "bin"
    if bin_dir.is_dir():
        current = env.value("PATH", "")
        if str(bin_dir) not in current.split(os.pathsep):
            env.insert("PATH", current + os.pathsep + str(bin_dir))
    proc.setProcessEnvironment(env)


class CommandRunner(QObject):
    """Runs `bash vonvakvas.sh <args>` without freezing the interface.

    Signals:
        output_received(str)  -> output chunks (stdout+stderr together)
        started(str)          -> command line that started running
        finished(int, str)    -> exit code and the command line
    """

    output_received = Signal(str)
    started = Signal(str)
    finished = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._proc: QProcess | None = None
        self._cmdline = ""

    def is_running(self) -> bool:
        return (
            self._proc is not None
            and self._proc.state() != QProcess.ProcessState.NotRunning
        )

    def run(
        self,
        args: list[str],
        stdin_data: str | None = None,
        cwd: Path | None = None,
    ) -> bool:
        """Starts a command. Returns False if one is already running."""
        if self.is_running():
            return False

        proc = QProcess(self)
        proc.setWorkingDirectory(str(cwd or PROJECT_ROOT))
        proc.setProgram("bash")
        proc.setArguments([str(VONVAKVAS_SH), *args])
        # Merges stderr into stdout so the console shows everything in order
        proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        _apply_child_env(proc)

        self._cmdline = "vonvakvas " + " ".join(args)
        proc.readyReadStandardOutput.connect(self._on_ready_read)
        proc.finished.connect(self._on_finished)

        self._proc = proc
        proc.start()

        # uploaderf.sh uses `read -rp` for URL and confirmation: the GUI injects
        # the answers via stdin (one line per question).
        if stdin_data:
            proc.write(stdin_data.encode("utf-8"))
            proc.closeWriteChannel()

        self.started.emit(self._cmdline)
        return True

    def stop(self) -> None:
        """Stops the running command.

        First kills the children (yt-dlp, ia, curl...) via psutil and then the
        bash process — without this the children would be orphaned and keep
        running. Does NOT use killpg: bash inherits the GUI's process group
        and we would kill ourselves.
        """
        if not self.is_running():
            return
        proc = self._proc
        try:
            parent = psutil.Process(proc.processId())
            children = parent.children(recursive=True)
            for child in children:
                child.terminate()
            _gone, alive = psutil.wait_procs(children, timeout=3)
            for child in alive:
                child.kill()
        except Exception:
            # psutil missing or process already dead: standard fallback
            pass
        proc.terminate()
        if not proc.waitForFinished(3000):
            proc.kill()

    def _on_ready_read(self) -> None:
        if self._proc is None:
            return
        data = self._proc.readAllStandardOutput().data().decode(
            "utf-8", errors="replace"
        )
        if data:
            self.output_received.emit(data)

    def _on_finished(self, code, _status) -> None:
        proc = self._proc
        self._proc = None
        if proc is not None:
            proc.deleteLater()
        self.finished.emit(int(code), self._cmdline)



