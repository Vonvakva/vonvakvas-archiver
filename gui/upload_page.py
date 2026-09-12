"""Página Upload IA: chama `vonvakvas upload <pasta>` via CLI.

O uploaderf.sh pergunta a URL do canal e a confirmação com `read -rp`;
a GUI injeta as respostas via stdin (URL digitada + "y").
"""

from __future__ import annotations

import pathlib

from PySide6.QtWidgets import (
    QFileDialog,
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
from widgets import Card, PathEdit, chip


class UploadPage(QWidget):
    def __init__(self, runner, main):
        super().__init__()
        self.runner = runner
        self.main = main

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 0, 4, 16)
        lay.setSpacing(16)

        self.path_card = Card(i18n.tr("upload.path_title"))
        row = QHBoxLayout()
        self.path_edit = PathEdit()
        self.path_edit.on_change = self._validate
        row.addWidget(self.path_edit, 1)
        btn_browse = QPushButton(i18n.tr("btn.browse"))
        btn_browse.clicked.connect(self._browse)
        row.addWidget(btn_browse)
        self.path_card.body().addLayout(row)

        self.dirs_list = QListWidget()
        self.dirs_list.setMaximumHeight(140)
        self.dirs_list.itemClicked.connect(self._pick_dir)
        self.path_card.body().addWidget(self.dirs_list)

        valid_row = QHBoxLayout()
        self.valid_chip = chip(i18n.tr("upload.valid_na"), "muted")
        valid_row.addWidget(self.valid_chip)
        valid_row.addStretch()
        self.path_card.body().addLayout(valid_row)
        lay.addWidget(self.path_card)

        self.up_card = Card(i18n.tr("upload.up_title"))
        url_row = QHBoxLayout()
        self.url_label = QLabel(i18n.tr("upload.url_label"))
        self.url_edit = PathEdit("https://www.youtube.com/@canal")
        url_row.addWidget(self.url_label)
        url_row.addWidget(self.url_edit, 1)
        self.up_card.body().addLayout(url_row)

        self.btn_upload = QPushButton(i18n.tr("upload.btn_upload"))
        self.btn_upload.setObjectName("accent")
        self.btn_upload.clicked.connect(self._run)
        self.up_card.body().addWidget(self.btn_upload)

        note = QLabel(i18n.tr("upload.note"))
        note.setObjectName("muted")
        note.setWordWrap(True)
        self.up_card.body().addWidget(note)
        lay.addWidget(self.up_card)
        lay.addStretch()

        self.refresh()

    def retranslate(self):
        self._set_title(self.path_card, i18n.tr("upload.path_title"))
        self._set_title(self.up_card, i18n.tr("upload.up_title"))
        self.url_label.setText(i18n.tr("upload.url_label"))
        self.btn_upload.setText(i18n.tr("upload.btn_upload"))
        self._validate()
        self.refresh()

    @staticmethod
    def _set_title(card, title: str):
        for w in card.findChildren(QLabel):
            if w.objectName() == "cardTitle":
                w.setText(title.upper())
                break

    # ------------------------------------------------------------------

    def refresh(self):
        self.dirs_list.clear()
        dirs = backend.list_channel_dirs()
        self.dirs_list.addItems(dirs) if dirs else self.dirs_list.addItem(
            i18n.tr("org.empty")
        )
        self._validate()

    def set_busy(self, busy: bool):
        self.btn_upload.setEnabled(not busy)

    def _pick_dir(self, item):
        name = item.text()
        if name.startswith("("):
            return
        path = str(backend.channels_dir() / name)
        self.path_edit.set_text(path)
        if not self.url_edit.text().strip():
            self.url_edit.set_text(f"https://www.youtube.com/@{name}")

    def _browse(self):
        start = self.path_edit.text() or str(backend.channels_dir())
        chosen = QFileDialog.getExistingDirectory(
            self, i18n.tr("upload.pick_title"), start
        )
        if chosen:
            self.path_edit.set_text(chosen)
            self._validate()

    def _validate(self):
        pasta = pathlib.Path(self.path_edit.text().strip())
        has_ia = (pasta / "ia").is_dir()
        if self.path_edit.text().strip() and has_ia:
            self.valid_chip.setText(i18n.tr("upload.valid_ok"))
            self.valid_chip.setObjectName("chipOk")
        elif self.path_edit.text().strip():
            self.valid_chip.setText(i18n.tr("upload.valid_bad"))
            self.valid_chip.setObjectName("chipBad")
        else:
            self.valid_chip.setText(i18n.tr("upload.valid_na"))
            self.valid_chip.setObjectName("chipMuted")
        self.valid_chip.style().unpolish(self.valid_chip)
        self.valid_chip.style().polish(self.valid_chip)

    def _run(self):
        pasta = pathlib.Path(self.path_edit.text().strip())
        url = self.url_edit.text().strip()
        if not pasta.is_dir():
            QMessageBox.warning(self, i18n.tr("upload.title"),
                                i18n.tr("upload.warn_no_folder"))
            return
        if not (pasta / "ia").is_dir():
            QMessageBox.warning(
                self,
                i18n.tr("upload.title"),
                i18n.tr("upload.warn_no_ia", pasta=pasta),
            )
            return
        if not url:
            QMessageBox.warning(
                self,
                i18n.tr("upload.title"),
                i18n.tr("upload.warn_no_url"),
            )
            return
        stdin_data = f"{url}\ny\n"
        if not self.runner.run(["upload", str(pasta)], stdin_data=stdin_data):
            QMessageBox.information(self, i18n.tr("busy.title"),
                                    i18n.tr("busy.text"))