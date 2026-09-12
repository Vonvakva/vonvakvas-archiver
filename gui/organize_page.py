"""Página Organizar: os organizadores + prepare-upload, via CLI."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import backend
import i18n
from widgets import Card, PathEdit

ACTIONS = [
    ("organize", "org.ai_organize", False),
    ("organize-instagram", "org.ai_instagram", False),
    ("organize-music", "org.ai_music", False),
    ("desorganize", "org.ai_desorganize", False),
    ("desorganize-music", "org.ai_desorganize_music", False),
    ("prepare-upload", "org.ai_prepare", True),
]


class OrganizePage(QWidget):
    def __init__(self, runner, main):
        super().__init__()
        self.runner = runner
        self.main = main

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 0, 4, 16)
        lay.setSpacing(16)

        self.path_card = Card(i18n.tr("org.path_title"))
        row = QHBoxLayout()
        self.path_edit = PathEdit()
        row.addWidget(self.path_edit, 1)
        btn_browse = QPushButton(i18n.tr("btn.browse"))
        btn_browse.clicked.connect(self._browse)
        row.addWidget(btn_browse)
        btn_basedir = QPushButton(i18n.tr("org.btn_basedir"))
        btn_basedir.setToolTip(i18n.tr("org.btn_basedir_tip"))
        btn_basedir.clicked.connect(
            lambda: self.path_edit.set_text(str(backend.channels_dir()))
        )
        row.addWidget(btn_basedir)
        self.path_card.body().addLayout(row)

        self.dirs_list = QListWidget()
        self.dirs_list.setMaximumHeight(140)
        self.dirs_list.itemClicked.connect(
            lambda item: self.path_edit.set_text(
                str(backend.channels_dir() / item.text())
            )
        )
        self.path_card.body().addWidget(self.dirs_list)
        self.hint = QLabel()
        self.hint.setObjectName("muted")
        self.hint.setWordWrap(True)
        self.path_card.body().addWidget(self.hint)
        lay.addWidget(self.path_card)

        self.actions_card = Card(i18n.tr("org.actions_title"))
        grid = QGridLayout()
        grid.setSpacing(10)
        self.buttons: dict[str, QPushButton] = {}
        for i, (cmd, label_key, is_accent) in enumerate(ACTIONS):
            b = QPushButton(i18n.tr(label_key))
            if is_accent:
                b.setObjectName("accent")
            b.clicked.connect(lambda _=False, c=cmd: self._run(c))
            grid.addWidget(b, i // 3, i % 3)
            self.buttons[cmd] = b
        self.actions_card.body().addLayout(grid)
        note = QLabel(i18n.tr("org.note"))
        note.setObjectName("muted")
        note.setWordWrap(True)
        self.actions_card.body().addWidget(note)
        lay.addWidget(self.actions_card)
        lay.addStretch()

        self.refresh()

    def retranslate(self):
        self._set_title(self.path_card, i18n.tr("org.path_title"))
        self._set_title(self.actions_card, i18n.tr("org.actions_title"))
        for cmd, label_key, _accent in ACTIONS:
            self.buttons[cmd].setText(i18n.tr(label_key))
        self.refresh()

    @staticmethod
    def _set_title(card, title: str):
        for w in card.findChildren(QLabel):
            if w.objectName() == "cardTitle":
                w.setText(title.upper())
                break

    # ------------------------------------------------------------------

    def refresh(self):
        current = self.path_edit.text()
        self.dirs_list.clear()
        dirs = backend.list_channel_dirs()
        self.dirs_list.addItems(dirs) if dirs else self.dirs_list.addItem(
            i18n.tr("org.empty")
        )
        self.hint.setText(i18n.tr("org.hint", dir=backend.channels_dir()))
        if not current or current == str(backend.DEFAULT_WORKDIR):
            self.path_edit.set_text(str(backend.channels_dir()))
        else:
            self.path_edit.set_text(current)

    def set_folder(self, path: str):
        self.path_edit.set_text(path)

    def set_busy(self, busy: bool):
        for b in self.buttons.values():
            b.setEnabled(not busy)

    # ------------------------------------------------------------------

    def _browse(self):
        start = self.path_edit.text() or str(backend.channels_dir())
        chosen = QFileDialog.getExistingDirectory(self, i18n.tr("org.pick_title"), start)
        if chosen:
            self.path_edit.set_text(chosen)

    def _run(self, cmd: str):
        pasta = self.path_edit.text().strip() or str(backend.channels_dir())
        if not self.runner.run([cmd, pasta]):
            QMessageBox.information(self, i18n.tr("busy.title"),
                                    i18n.tr("busy.text"))