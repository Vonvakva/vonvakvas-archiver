"""Página Extensões: gerencia os widgets custom (gui/extensions/*.py).

Uma extensão é um .py nessa pasta que define NAME, WHERE e get_value()
— veja o contrato completo em gui/extensions/README.md. Aqui você vê o
que carregou, o valor atual, liga/desliga (persistente) e recarrega.
"""

from __future__ import annotations

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import extmgr
import i18n
from widgets import Card, chip


class ExtensionsPage(QWidget):
    def __init__(self, runner, main):
        super().__init__()
        self.runner = runner
        self.main = main

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 0, 4, 16)
        lay.setSpacing(16)

        self.card = Card(i18n.tr("ext.title"))
        row = QHBoxLayout()
        self.chip_count = chip("", "accent")
        row.addWidget(self.chip_count)
        row.addStretch()
        self.card.body().addLayout(row)

        self.list = QListWidget()
        self.list.setMinimumHeight(200)
        self.list.itemSelectionChanged.connect(self._update_details)
        self.card.body().addWidget(self.list)

        self.details = QLabel(i18n.tr("ext.details_prompt"))
        self.details.setObjectName("muted")
        self.details.setWordWrap(True)
        self.card.body().addWidget(self.details)

        btns = QHBoxLayout()
        self.btn_toggle = QPushButton(i18n.tr("ext.btn_toggle_off"))
        self.btn_toggle.setObjectName("accent")
        self.btn_toggle.clicked.connect(self._toggle)
        self.btn_reload = QPushButton(i18n.tr("btn.reload"))
        self.btn_reload.setToolTip(i18n.tr("ext.reload_tip"))
        self.btn_reload.clicked.connect(self._reload)
        self.btn_open = QPushButton(i18n.tr("ext.btn_open"))
        self.btn_open.clicked.connect(self._open_folder)
        btns.addWidget(self.btn_toggle)
        btns.addWidget(self.btn_reload)
        btns.addWidget(self.btn_open)
        btns.addStretch()
        self.card.body().addLayout(btns)
        lay.addWidget(self.card)

        # ---------------- como criar ----------------
        self.help_card = Card(i18n.tr("ext.help_title"))
        self.note = QLabel(i18n.tr("ext.help_note"))
        self.note.setObjectName("muted")
        self.note.setWordWrap(True)
        self.help_card.body().addWidget(self.note)
        self.err_lbl = QLabel("")
        self.err_lbl.setObjectName("muted")
        self.err_lbl.setWordWrap(True)
        self.help_card.body().addWidget(self.err_lbl)
        lay.addWidget(self.help_card)
        lay.addStretch()

        mgr = extmgr.get_manager()
        mgr.reloaded.connect(self.refresh)
        mgr.updated.connect(self._update_values)
        self.refresh()

    # ------------------------------------------------------------------

    def retranslate(self):
        """Re-aplica todos os textos ao idioma ativo."""
        self.card.set_title(i18n.tr("ext.title"))
        self.help_card.set_title(i18n.tr("ext.help_title"))
        self.btn_reload.setText(i18n.tr("btn.reload"))
        self.btn_reload.setToolTip(i18n.tr("ext.reload_tip"))
        self.btn_open.setText(i18n.tr("ext.btn_open"))
        self.note.setText(i18n.tr("ext.help_note"))
        self.refresh()

    # ------------------------------------------------------------------

    def refresh(self):
        mgr = extmgr.get_manager()
        selected = self._selected_id()
        self.list.blockSignals(True)
        self.list.clear()
        for ext in mgr.extensions.values():
            flag = "" if ext.enabled else i18n.tr("ext.disabled_suffix")
            self.list.addItem(i18n.tr("ext.files_row",
                                      name=ext.name, id=ext.id, flag=flag))
        self.list.blockSignals(False)
        if selected:
            matches = self.list.findItems(f"({selected})", Qt.MatchContains)
            if matches:
                self.list.setCurrentItem(matches[0])

        total = len(mgr.extensions)
        ativas = len([e for e in mgr.extensions.values() if e.enabled])
        self.chip_count.setText(i18n.tr("ext.count", ativas=ativas, total=total))

        if mgr.load_errors:
            self.err_lbl.setText(
                i18n.tr("ext.errors") + "\n• ".join(mgr.load_errors)
            )
        else:
            self.err_lbl.setText("")
        self._update_details()
        self._update_values()

    def set_busy(self, busy: bool):
        self.btn_toggle.setEnabled(not busy)
        self.btn_reload.setEnabled(not busy)

    # ------------------------------------------------------------------

    def _selected_id(self) -> str | None:
        item = self.list.currentItem()
        if item is None:
            return None
        text = item.text()
        start = text.rfind("(")
        end = text.rfind(")")
        return text[start + 1:end] if start != -1 and end != -1 else None

    def _update_details(self):
        mgr = extmgr.get_manager()
        ext_id = self._selected_id()
        ext = mgr.extensions.get(ext_id or "")
        if ext is None:
            self.details.setText(i18n.tr("ext.details_prompt"))
            self.btn_toggle.setText(i18n.tr("ext.btn_toggle_off"))
            self.btn_toggle.setEnabled(False)
            return
        estado = (i18n.tr("ext.state_active") if ext.enabled
                  else i18n.tr("ext.state_disabled"))
        self.details.setText(i18n.tr(
            "ext.details_file",
            path=ext.path.name,
            where=", ".join(ext.where),
            refresh=ext.refresh,
            estado=estado,
            last=ext.last_text,
        ) + (i18n.tr("ext.detail_error", error=ext.error) if ext.error else ""))
        self.btn_toggle.setText(
            i18n.tr("ext.btn_toggle_off") if ext.enabled
            else i18n.tr("ext.btn_toggle_on")
        )
        self.btn_toggle.setEnabled(True)

    def _update_values(self):
        # mantém os detalhes vivos sem recarregar a lista inteira
        if self.details and self.list.currentItem() is not None:
            self._update_details()

    def _toggle(self):
        mgr = extmgr.get_manager()
        ext_id = self._selected_id()
        ext = mgr.extensions.get(ext_id or "")
        if ext is None:
            return
        mgr.set_enabled(ext.id, not ext.enabled)

    def _reload(self):
        extmgr.get_manager().load()
        self.main.console.append_output(i18n.tr("ext.log_reloaded"))

    def _open_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(extmgr.EXTENSIONS_DIR)))
