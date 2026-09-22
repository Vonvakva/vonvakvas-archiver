#!/usr/bin/env python3
"""Vonvakva's Archive — GUI (PySide6).

Iniciada por start-gui.sh: `python -B gui/main.py` a partir da raiz.
Todos os botões chamam a CLI ./vonvakvas.sh — a GUI não reimplementa
nenhuma lógica do backend (for-the-model/agentrules.md).

Layout: header fixo (perfil + hostname/OS/data/disco) • sidebar de
navegação • páginas empilhadas • console compartilhado embaixo.
"""

from __future__ import annotations

import sys
from pathlib import Path

GUI_DIR = Path(__file__).resolve().parent
if str(GUI_DIR) not in sys.path:
    sys.path.insert(0, str(GUI_DIR))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import backend
import i18n
import theme
from header import HeaderBar
from widgets import ConsolePanel

# Las páginas se listan por claves i18n "nav.X" y "sub.X"; el label real se
# resuelve con i18n.tr() en construcción y en retranslate_all().
PAGES = [
    ("dash", "nav.dash", "sub.dash"),
    ("archive", "nav.archive", "sub.archive"),
    ("organize", "nav.organize", "sub.organize"),
    ("upload", "nav.upload", "sub.upload"),
    ("monitor", "nav.monitor", "sub.monitor"),
    ("mass", "nav.mass", "sub.mass"),
    ("editor", "nav.editor", "sub.editor"),
    ("profiles", "nav.profiles", "sub.profiles"),
    ("themes", "nav.themes", "sub.themes"),
    ("extensions", "nav.extensions", "sub.extensions"),
    ("settings", "nav.settings", "sub.settings"),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vonvakva's Archive")
        self.resize(1180, 740)
        self.setMinimumSize(1000, 640)

        self.runner = backend.CommandRunner(self)
        self.runner.started.connect(self._on_started)
        self.runner.output_received.connect(self._on_output)
        self.runner.finished.connect(self._on_finished)

        central = QWidget()
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ---------------- sidebar ----------------
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(212)
        self.sidebar_widget = sidebar  # ref para retranslate_all()
        sv = QVBoxLayout(sidebar)
        sv.setContentsMargins(16, 22, 16, 16)
        sv.setSpacing(6)
        logo = QLabel("Vonvakva's")
        logo.setObjectName("logo")
        sub = QLabel("Archiver")
        sub.setObjectName("logoSub")
        self.logo_lbl = logo  # ref para retranslate_all() preservar a marca
        self.sub_lbl = sub  # ref para retranslate_all() preservar a marca
        sv.addWidget(logo)
        sv.addWidget(sub)
        # slot de decoração do tema (gif.sidebar / extras.sidebar_text)
        self.sidebar_decor = QVBoxLayout()
        self.sidebar_decor.setSpacing(8)
        sv.addLayout(self.sidebar_decor)
        sv.addSpacing(20)

        self.nav_buttons = {}
        for key, label_key, _sub in PAGES:
            b = QPushButton(i18n.tr(label_key))
            b.setObjectName("navBtn")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, k=key: self.show_page(k))
            sv.addWidget(b)
            self.nav_buttons[key] = b
        sv.addStretch()
        root_lbl = QLabel(str(backend.PROJECT_ROOT))
        root_lbl.setObjectName("muted")
        root_lbl.setWordWrap(True)
        sv.addWidget(root_lbl)

        # ---------------- área principal ----------------
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 12)
        rv.setSpacing(10)

        # header fixo: perfil + hostname/OS/data/disco
        self.header = HeaderBar()
        self.header.profile_changed.connect(self._on_profile_changed)
        rv.addWidget(self.header)

        # título da página
        title_row = QHBoxLayout()
        title_row.setContentsMargins(20, 6, 20, 0)
        tv = QVBoxLayout()
        tv.setSpacing(2)
        self.page_title = QLabel("")
        self.page_title.setObjectName("h1")
        self.page_subtitle = QLabel("")
        self.page_subtitle.setObjectName("muted")
        tv.addWidget(self.page_title)
        tv.addWidget(self.page_subtitle)
        title_row.addLayout(tv)
        title_row.addStretch()
        self.busy_lbl = QLabel("")
        self.busy_lbl.setObjectName("busy")
        title_row.addWidget(self.busy_lbl)
        rv.addLayout(title_row)

        self.stack = QStackedWidget()
        self.pages = self._build_pages()
        for key, _label, _sub in PAGES:
            scroll = QScrollArea()
            scroll.setObjectName("pageScroll")
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setWidget(self.pages[key])
            self.stack.addWidget(scroll)

        self.console = ConsolePanel()
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.stack)
        splitter.addWidget(self.console)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([520, 180])
        rv.addWidget(splitter, 1)

        outer.addWidget(sidebar)
        outer.addWidget(right, 1)

        self.show_page("dash")
        self._set_busy(False)
        self.rebuild_decorations()

    # ------------------------------------------------------------------

    def _build_pages(self) -> dict:
        from archive_page import ArchivePage
        from dashboard import DashboardPage
        from editor_page import EditorPage
        from extensions_page import ExtensionsPage
        from mass_page import MassPage
        from monitor_page import MonitorPage
        from organize_page import OrganizePage
        from profiles_page import ProfilesPage
        from settings_page import SettingsPage
        from themes_page import ThemesPage
        from upload_page import UploadPage

        return {
            "dash": DashboardPage(self.runner, self),
            "archive": ArchivePage(self.runner, self),
            "organize": OrganizePage(self.runner, self),
            "upload": UploadPage(self.runner, self),
            "monitor": MonitorPage(self.runner, self),
            "mass": MassPage(self.runner, self),
            "editor": EditorPage(self.runner, self),
            "profiles": ProfilesPage(self.runner, self),
            "themes": ThemesPage(self.runner, self),
            "extensions": ExtensionsPage(self.runner, self),
            "settings": SettingsPage(self.runner, self),
        }

    def show_page(self, key: str):
        keys = [k for k, _l, _s in PAGES]
        if key not in keys:
            return
        for k, b in self.nav_buttons.items():
            b.setChecked(k == key)
        self.stack.setCurrentIndex(keys.index(key))
        _k, label_key, sub_key = PAGES[keys.index(key)]
        self.page_title.setText(i18n.tr(label_key))
        self.page_subtitle.setText(i18n.tr(sub_key))
        page = self.pages[key]
        if hasattr(page, "refresh"):
            page.refresh()

    def open_organize_with(self, path: str):
        self.pages["organize"].set_folder(path)
        self.show_page("organize")

    def refresh_all(self):
        """Recarrega as páginas após troca de perfil / config."""
        for key, page in self.pages.items():
            if hasattr(page, "refresh"):
                page.refresh()
        self.header.refresh_disk()

    def retranslate_all(self):
        """Re-aplica todos os textos ao idioma ativo em toda a GUI.

        Estratégia em 2 passos:
          1. Componentes fixos/globais da janela (sidebar, header, console,
             botões de navegação, título da página ativa).
          2. Percorre RECURSIVAMENTE toda a árvore de widgets e chama
             retranslate() em qualquer widget que o implemente — assim
             chips, cards e sub-widgets aninhados nunca ficam de fora.
       Widgets visitados ficam num set para não serem atualizados 2x.
        """
        visited: set[int] = set()

        def _ret(widget) -> None:
            if id(widget) in visited:
                return
            visited.add(id(widget))
            fn = getattr(widget, "retranslate", None)
            if callable(fn):
                fn()

        # ---- 1. componentes fixos/globais da janela ----
        if hasattr(self, "sidebar_widget"):
            _ret(self.sidebar_widget)
        # marca fixa da sidebar — nunca traduzir, só preservar
        if hasattr(self, "logo_lbl"):
            self.logo_lbl.setText("Vonvakva's")
        if hasattr(self, "sub_lbl"):
            self.sub_lbl.setText("Archive")
        if hasattr(self, "header"):
            _ret(self.header)
        if hasattr(self, "console"):
            _ret(self.console)

        # botões de navegação (sidebar)
        for key, label_key, _sub in PAGES:
            b = self.nav_buttons.get(key)
            if b is not None:
                b.setText(i18n.tr(label_key))

        # título/subtítulo da página ativa
        keys = [k for k, _l, _s in PAGES]
        current = self.stack.currentIndex()
        if 0 <= current < len(PAGES):
            _k, label_key, sub_key = PAGES[current]
            self.page_title.setText(i18n.tr(label_key))
            self.page_subtitle.setText(i18n.tr(sub_key))

        # ---- 2. percorre toda a árvore de widgets ----
        # central widget cobre sidebar + header + stack (páginas) + console
        central = self.centralWidget()
        if central is not None:
            it = central.findChildren(QWidget)
            for w in it:
                _ret(w)
            _ret(central)
        self._ret_visited = visited

    # ---------------- decoração do tema ----------------

    def rebuild_decorations(self):
        """Recria os widgets de decoração (gifs/textos) do tema ativo.

        Chamado na abertura e pela aba Temas ao aplicar um tema. Cada
        área (header, sidebar, dashboard) cuida dos seus próprios slots.
        """
        import theme
        from decor import AnimatedImage, DecorText, make_gif

        # ---- sidebar ----
        while self.sidebar_decor.count():
            item = self.sidebar_decor.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        meta = theme.load_theme_meta()
        theme_id = meta["id"]
        extras = meta.get("extras", {})

        sidebar_text = extras.get("sidebar_text", "")
        if sidebar_text:
            self.sidebar_decor.addWidget(DecorText(sidebar_text))

        sidebar_gif = meta.get("gif", {}).get("sidebar", "")
        if sidebar_gif:
            widget = make_gif(theme_id, sidebar_gif, max_height=90)
            if widget is not None:
                self.sidebar_decor.addWidget(widget)

        # ---- outras áreas ----
        self.header.rebuild_decorations()
        dash = self.pages.get("dash")
        if hasattr(dash, "rebuild_decorations"):
            dash.rebuild_decorations()

    # ---------------- perfil ----------------

    def _on_profile_changed(self, name: str):
        if self.runner.is_running():
            QMessageBox.warning(
                self,
                i18n.tr("console.running_warn_title"),
                i18n.tr("console.running_warn"),
            )
            self.header.refresh_profiles()  # reverte o combo
            return
        backend.set_active_profile(name or None)
        default = i18n.tr("console.default_profile")
        self.console.append_output(
            i18n.tr("console.profile_active", name=name or default)
        )
        self.refresh_all()

    # ---------------- runner -> UI ----------------

    def _on_started(self, cmdline: str):
        self.console.append_output(f"\n$ {cmdline}\n")
        self.console.set_status(i18n.tr("console.status_running", cmd=cmdline))
        self._set_busy(True)

    def _on_output(self, text: str):
        self.console.append_output(text)

    def _on_finished(self, code: int, cmdline: str):
        self._set_busy(False)
        self.console.append_output(
            i18n.tr("console.finished", code=code)
        )
        if code == 0:
            status = i18n.tr("console.done")
        else:
            status = i18n.tr("console.failed", code=code)
        self.console.set_status(status)
        self.pages["dash"].refresh()
        self.header.refresh_disk()

    def _stop_runner(self):
        if not self.runner.is_running():
            return
        self.console.append_output(i18n.tr("console.stopping"))
        self.console.set_status(i18n.tr("console.parando"))
        self.runner.stop()

    def _set_busy(self, busy: bool):
        self.busy_lbl.setText(i18n.tr("busy.running") if busy else "")
        self.console.btn_stop.setEnabled(busy)
        for page in self.pages.values():
            page.set_busy(busy)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Vonvakva's Archive")
    app.setStyleSheet(theme.build_qss())
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
