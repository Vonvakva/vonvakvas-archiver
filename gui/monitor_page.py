"""Página Monitor: lista de canais + `vonvakvas check` (alerta Telegram)."""

from __future__ import annotations

from PySide6.QtWidgets import (
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
from widgets import Card, StatCard


class MonitorPage(QWidget):
    def __init__(self, runner, main):
        super().__init__()
        self.runner = runner
        self.main = main

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 0, 4, 16)
        lay.setSpacing(16)

        top = QHBoxLayout()
        top.setSpacing(12)
        self.card_total = StatCard(i18n.tr("mon.total_title"), subtitle=i18n.tr("mon.total_sub"))
        self.card_saved = StatCard(i18n.tr("mon.saved_title"), subtitle=i18n.tr("mon.saved_sub"))
        top.addWidget(self.card_total)
        top.addWidget(self.card_saved)
        top.addStretch()
        lay.addLayout(top)

        self.list_card = Card(i18n.tr("mon.list_title"))
        self.list = QListWidget()
        self.list.setMaximumHeight(260)
        self.list_card.body().addWidget(self.list)
        self.hint = QLabel()
        self.hint.setObjectName("muted")
        self.hint.setWordWrap(True)
        self.list_card.body().addWidget(self.hint)
        lay.addWidget(self.list_card)

        self.btn_card = Card(i18n.tr("mon.actions_title"))
        row = QHBoxLayout()
        self.btn_check = QPushButton(i18n.tr("mon.btn_check"))
        self.btn_check.setObjectName("accent")
        self.btn_check.clicked.connect(self._run_check)
        self.btn_refresh = QPushButton(i18n.tr("mon.btn_refresh"))
        self.btn_refresh.clicked.connect(self.refresh)
        row.addWidget(self.btn_check)
        row.addWidget(self.btn_refresh)
        row.addStretch()
        self.btn_card.body().addLayout(row)
        known = QLabel(i18n.tr("mon.known"))
        known.setObjectName("muted")
        known.setWordWrap(True)
        self.btn_card.body().addWidget(known)
        lay.addWidget(self.btn_card)
        lay.addStretch()

        self.refresh()

    def retranslate(self):
        self._set_card_title(self.card_total, i18n.tr("mon.total_title"))
        self.card_total.set_subtitle(i18n.tr("mon.total_sub"))
        self._set_card_title(self.card_saved, i18n.tr("mon.saved_title"))
        self.card_saved.set_subtitle(i18n.tr("mon.saved_sub"))
        self._set_title(self.list_card, i18n.tr("mon.list_title"))
        self._set_title(self.btn_card, i18n.tr("mon.actions_title"))
        self.btn_check.setText(i18n.tr("mon.btn_check"))
        self.btn_refresh.setText(i18n.tr("mon.btn_refresh"))
        self.refresh()

    @staticmethod
    def _set_title(card, title: str):
        for w in card.findChildren(QLabel):
            if w.objectName() == "cardTitle":
                w.setText(title.upper())
                break

    @staticmethod
    def _set_card_title(stat_card, title: str):
        for w in stat_card.findChildren(QLabel):
            if w.objectName() == "cardTitle":
                w.setText(title.upper())
                break

    # ------------------------------------------------------------------

    def refresh(self):
        canais = backend.read_channel_list()
        self.list.clear()
        self.list.addItems([f"@{c}" for c in canais]) if canais else self.list.addItem(
            i18n.tr("mon.empty")
        )
        self.card_total.set_value(len(canais))
        self.card_saved.set_value(len(backend.successful_channels()))
        perfil = backend.active_profile()
        self.hint.setText(
            i18n.tr("mon.hint",
                    perfil=perfil or i18n.tr("common.default_profile"))
        )

    def set_busy(self, busy: bool):
        self.btn_check.setEnabled(not busy)
        self.btn_refresh.setEnabled(not busy)

    # ------------------------------------------------------------------

    def _run_check(self):
        if not self.runner.run(["check"]):
            QMessageBox.information(self, i18n.tr("busy.title"),
                                    i18n.tr("busy.text"))