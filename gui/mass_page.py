"""Página Em massa: mass-archive e mass-organize (com confirmação)."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import backend
import i18n
from widgets import Card, chip


class MassPage(QWidget):
    def __init__(self, runner, main):
        super().__init__()
        self.runner = runner
        self.main = main

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 0, 4, 16)
        lay.setSpacing(16)

        self.warn_card = Card(i18n.tr("mass.warn_title"))
        row = QHBoxLayout()
        row.addWidget(chip(i18n.tr("mass.warn_chip1"), "warn"))
        row.addWidget(chip(i18n.tr("mass.warn_chip2"), "warn"))
        row.addStretch()
        self.warn_card.body().addLayout(row)
        self.warn = QLabel()
        self.warn.setObjectName("muted")
        self.warn.setWordWrap(True)
        self.warn_card.body().addWidget(self.warn)
        lay.addWidget(self.warn_card)

        self.actions_card = Card(i18n.tr("mass.actions_title"))
        row2 = QHBoxLayout()
        self.btn_mass_archive = QPushButton(i18n.tr("mass.btn_archive"))
        self.btn_mass_archive.setObjectName("danger")
        self.btn_mass_archive.clicked.connect(self._run_archive)
        self.btn_mass_organize = QPushButton(i18n.tr("mass.btn_organize"))
        self.btn_mass_organize.clicked.connect(self._run_organize)
        row2.addWidget(self.btn_mass_archive)
        row2.addWidget(self.btn_mass_organize)
        row2.addStretch()
        self.actions_card.body().addLayout(row2)
        lay.addWidget(self.actions_card)
        lay.addStretch()

        self.refresh()

    def retranslate(self):
        self._set_title(self.warn_card, i18n.tr("mass.warn_title"))
        self._set_title(self.actions_card, i18n.tr("mass.actions_title"))
        self.btn_mass_archive.setText(i18n.tr("mass.btn_archive"))
        self.btn_mass_organize.setText(i18n.tr("mass.btn_organize"))
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
        self.warn.setText(
            i18n.tr("mass.warn_text",
                    perfil=perfil or i18n.tr("common.default_profile"))
        )

    def set_busy(self, busy: bool):
        self.btn_mass_archive.setEnabled(not busy)
        self.btn_mass_organize.setEnabled(not busy)

    def _run_archive(self):
        n = len(backend.read_channel_list())
        box = QMessageBox(self)
        box.setWindowTitle("Mass archive")
        box.setText(i18n.tr("mass.box_text", n=n))
        btn_cookies = box.addButton(i18n.tr("mass.box_cookies"), QMessageBox.AcceptRole)
        btn_ghost = box.addButton(i18n.tr("mass.box_ghost"), QMessageBox.AcceptRole)
        box.addButton(i18n.tr("mass.box_cancel"), QMessageBox.RejectRole)
        box.exec()
        clicked = box.clickedButton()
        if clicked is btn_cookies:
            mask = "y"
        elif clicked is btn_ghost:
            mask = "n"
        else:
            return
        # mass_nts.sh pergunta a máscara via `read -p`: injetamos a resposta.
        # cwd = pasta dos canais para que os downloads caiam lá.
        self.runner.run(
            ["mass-archive"], stdin_data=f"{mask}\n", cwd=backend.channels_dir()
        )

    def _run_organize(self):
        answer = QMessageBox.question(
            self,
            i18n.tr("mass.organize_q_title"),
            i18n.tr("mass.organize_q"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            # mass_organizer.sh itera as pastas do diretório atual
            self.runner.run(["mass-organize"], cwd=backend.channels_dir())