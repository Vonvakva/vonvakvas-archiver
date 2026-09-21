"""Página Arquivar: archive, archive-names e archive-playlist (nts/ntsn/ntsp via CLI)."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import backend
import i18n
from widgets import Card, PathEdit

MODES = {
    "n": "archive.mode_n",
    "y": "archive.mode_y",
}


class ArchivePage(QWidget):
    def __init__(self, runner, main):
        super().__init__()
        self.runner = runner
        self.main = main

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 0, 4, 16)
        lay.setSpacing(16)

        self.card = Card(i18n.tr("archive.title"))

        canal_row = QHBoxLayout()
        self.canal_label = QLabel(i18n.tr("archive.canal_label"))
        self.canal_edit = PathEdit(i18n.tr("archive.placeholder"))
        canal_row.addWidget(self.canal_label)
        canal_row.addWidget(self.canal_edit, 1)
        self.card.body().addLayout(canal_row)

        mode_row = QHBoxLayout()
        self.mode_label = QLabel(i18n.tr("archive.mode_label"))
        self.mode_combo = QComboBox()
        for key in MODES:
            self.mode_combo.addItem(i18n.tr(MODES[key]))
        self.mode_combo.setToolTip(i18n.tr("archive.tooltip"))
        mode_row.addWidget(self.mode_label)
        mode_row.addWidget(self.mode_combo, 1)
        self.card.body().addLayout(mode_row)

        btn_row = QHBoxLayout()
        self.btn_archive = QPushButton(i18n.tr("archive.btn_normal"))
        self.btn_archive.setObjectName("accent")
        self.btn_archive.clicked.connect(self._run_normal)
        self.btn_playlist = QPushButton(i18n.tr("archive.btn_playlist"))
        self.btn_playlist.clicked.connect(self._run_playlist)
        self.btn_names = QPushButton(i18n.tr("archive.btn_names"))
        self.btn_names.clicked.connect(self._run_names)
        btn_row.addWidget(self.btn_archive)
        btn_row.addWidget(self.btn_playlist)
        btn_row.addWidget(self.btn_names)
        btn_row.addStretch()
        self.card.body().addLayout(btn_row)

        self.note = QLabel()
        self.note.setObjectName("muted")
        self.note.setWordWrap(True)
        self.card.body().addWidget(self.note)

        lay.addWidget(self.card)
        lay.addStretch()

        self.refresh()

    def retranslate(self):
        self._set_title(self.card, i18n.tr("archive.title"))
        self.canal_label.setText(i18n.tr("archive.canal_label"))
        self.canal_edit.set_placeholder(i18n.tr("archive.placeholder"))
        self.mode_label.setText(i18n.tr("archive.mode_label"))
        self.mode_combo.setToolTip(i18n.tr("archive.tooltip"))
        self.btn_archive.setText(i18n.tr("archive.btn_normal"))
        self.btn_playlist.setText(i18n.tr("archive.btn_playlist"))
        self.btn_names.setText(i18n.tr("archive.btn_names"))
        # recargar nombres de modos sin perder la selección
        selected = self._selected_mode()
        self.mode_combo.blockSignals(True)
        self.mode_combo.clear()
        for key in MODES:
            self.mode_combo.addItem(i18n.tr(MODES[key]))
        idx = list(MODES).index(selected)
        self.mode_combo.setCurrentIndex(idx)
        self.mode_combo.blockSignals(False)
        self.refresh()

    @staticmethod
    def _set_title(card, title: str):
        for w in card.findChildren(QLabel):
            if w.objectName() == "cardTitle":
                w.setText(title.upper())
                break

    # ------------------------------------------------------------------

    def refresh(self):
        perfil = backend.active_profile()
        destino = backend.channels_dir()
        self.note.setText(
            i18n.tr("archive.note_line1") + "\n"
            + i18n.tr("archive.note_line2") + "\n"
            + i18n.tr("archive.note_line2b") + "\n"
            + i18n.tr("archive.note_line3") + "\n"
            + i18n.tr("archive.note_perfil",
                      perfil=perfil or i18n.tr("common.default_profile"),
                      destino=destino)
        )

    def _selected_mode(self) -> str:
        label = self.mode_combo.currentText()
        for key in MODES:
            if i18n.tr(MODES[key]) == label:
                return key
        return "n"

    def _run_normal(self):
        self._run("archive")

    def _run_playlist(self):
        self._run("archive-playlist")

    def _run_names(self):
        self._run("archive-names")

    def _run(self, cmd: str):
        canal = self.canal_edit.text().strip().lstrip("@")
        if not canal:
            QMessageBox.warning(self, i18n.tr("archive.warn_title"),
                                i18n.tr("archive.warn_no_canal"))
            return
        args = [cmd, canal, self._selected_mode()]
        # cwd = pasta dos canais (HDD externo se configurado) para que os
        # downloads caiam la (nts.sh / ntsn.sh usam o diretorio atual como destino)
        ok = self.runner.run(args, cwd=backend.channels_dir())
        if not ok:
            QMessageBox.information(self, i18n.tr("busy.title"),
                                    i18n.tr("busy.text"))

    def set_busy(self, busy: bool):
        self.btn_archive.setEnabled(not busy)
        self.btn_playlist.setEnabled(not busy)
        self.btn_names.setEnabled(not busy)