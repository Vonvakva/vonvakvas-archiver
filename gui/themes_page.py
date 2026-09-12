"""Página Temas: escolhe o tema visual e cria os seus (gui/themes/*.json)."""

from __future__ import annotations

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import i18n
import theme
from widgets import Card, chip

# Tokens mostrados na pré-visualização, na ordem.
# As labels resolvem-se com i18n.tr() em construção e em retranslate().
SWATCH_TOKENS = [
    ("bg", "themes.tok_bg"),
    ("bg_alt", "themes.tok_sidebar"),
    ("panel", "themes.tok_card"),
    ("panel_alt", "themes.tok_button"),
    ("border", "themes.tok_border"),
    ("text", "themes.tok_text"),
    ("muted", "themes.tok_secondary"),
    ("accent", "themes.tok_accent"),
    ("success", "themes.tok_ok"),
    ("danger", "themes.tok_error"),
    ("warning", "themes.tok_warning"),
    ("console_bg", "themes.tok_console"),
]


class ThemesPage(QWidget):
    def __init__(self, runner, main):
        super().__init__()
        self.runner = runner
        self.main = main

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 0, 4, 16)
        lay.setSpacing(16)

        self.card = Card(i18n.tr("themes.title"))
        top = QHBoxLayout()

        # ---------------- lista ----------------
        self.list = QListWidget()
        self.list.setMaximumWidth(340)
        self.list.itemClicked.connect(self._on_selected)
        self.list.itemDoubleClicked.connect(lambda _item: self._apply())
        top.addWidget(self.list, 1)

        # ---------------- pré-visualização ----------------
        preview = QVBoxLayout()
        preview.setSpacing(10)
        self.name_lbl = QLabel("—")
        self.name_lbl.setObjectName("h2")
        self.desc_lbl = QLabel("")
        self.desc_lbl.setObjectName("muted")
        self.desc_lbl.setWordWrap(True)
        preview.addWidget(self.name_lbl)
        preview.addWidget(self.desc_lbl)

        # decorações configuradas no tema (gifs/textos)
        decor_row = QHBoxLayout()
        decor_row.setSpacing(6)
        self.decor_chips_row = decor_row
        preview.addLayout(decor_row)

        swatches_row = QHBoxLayout()
        swatches_row.setSpacing(8)
        self._swatches: list[tuple[QFrame, str, QLabel]] = []
        for token, label_key in SWATCH_TOKENS:
            cell = QVBoxLayout()
            cell.setSpacing(3)
            sw = QFrame()
            sw.setFixedSize(34, 26)
            sw.setObjectName("swatch")
            lbl = QLabel(i18n.tr(label_key))
            lbl.setObjectName("muted")
            lbl.setStyleSheet("font-size: 10px;")
            cell.addWidget(sw, 0, Qt.AlignHCenter)
            cell.addWidget(lbl, 0, Qt.AlignHCenter)
            self._swatches.append((sw, token, lbl))
            wrap = QWidget()
            wrap.setLayout(cell)
            swatches_row.addWidget(wrap)
        preview.addLayout(swatches_row)

        self.chip_active = chip("", "accent")
        preview.addWidget(self.chip_active)
        preview.addStretch()
        top.addLayout(preview, 1)
        self.card.body().addLayout(top)

        btns = QHBoxLayout()
        self.btn_apply = QPushButton(i18n.tr("themes.btn_apply"))
        self.btn_apply.setObjectName("accent")
        self.btn_apply.clicked.connect(self._apply)
        self.btn_reload = QPushButton(i18n.tr("btn.reload"))
        self.btn_reload.setToolTip(i18n.tr("themes.btn_reload_tip"))
        self.btn_reload.clicked.connect(self.refresh)
        self.btn_open = QPushButton(i18n.tr("themes.btn_open"))
        self.btn_open.clicked.connect(self._open_folder)
        btns.addWidget(self.btn_apply)
        btns.addWidget(self.btn_reload)
        btns.addWidget(self.btn_open)
        btns.addStretch()
        self.card.body().addLayout(btns)
        lay.addWidget(self.card)

        # ---------------- como criar ----------------
        self.help_card = Card(i18n.tr("themes.help_title"))
        self.note = QLabel(i18n.tr("themes.help_note"))
        self.note.setObjectName("muted")
        self.note.setWordWrap(True)
        self.help_card.body().addWidget(self.note)
        lay.addWidget(self.help_card)
        lay.addStretch()

        self.refresh()

    # ------------------------------------------------------------------

    def retranslate(self):
        """Re-aplica todos os textos ao idioma ativo."""
        self.card.set_title(i18n.tr("themes.title"))
        self.help_card.set_title(i18n.tr("themes.help_title"))
        self.btn_apply.setText(i18n.tr("themes.btn_apply"))
        self.btn_reload.setText(i18n.tr("btn.reload"))
        self.btn_reload.setToolTip(i18n.tr("themes.btn_reload_tip"))
        self.btn_open.setText(i18n.tr("themes.btn_open"))
        self.note.setText(i18n.tr("themes.help_note"))
        for _sw, _token, lbl in self._swatches:
            lbl.setText(i18n.tr("themes.tok_" + _token))
        self.refresh()

    # ------------------------------------------------------------------

    def refresh(self):
        active = theme.get_active_theme_id()
        themes = theme.list_themes()
        self.list.blockSignals(True)
        self.list.clear()
        for t in themes:
            self.list.addItem(t["id"])
        self.list.blockSignals(False)
        self.chip_active.setText(i18n.tr("themes.active_chip", theme=active))

        # seleciona o tema ativo e mostra a preview dele
        matches = self.list.findItems(active, Qt.MatchExactly)
        if matches:
            self.list.setCurrentItem(matches[0])
        self._show_preview(active)

    def set_busy(self, busy: bool):
        self.btn_apply.setEnabled(not busy)
        self.btn_reload.setEnabled(not busy)

    # ------------------------------------------------------------------

    def _selected_theme_id(self) -> str | None:
        item = self.list.currentItem()
        return item.text() if item else None

    def _show_preview(self, theme_id: str | None):
        if not theme_id:
            return
        meta = next(
            (t for t in theme.list_themes() if t["id"] == theme_id), None
        )
        if meta is None:
            return
        self.name_lbl.setText(meta["name"])
        self.desc_lbl.setText(meta["description"] or i18n.tr("themes.no_desc"))
        colors = meta["colors"]
        for sw, _token, _lbl in self._swatches:
            sw.setStyleSheet(
                f"background-color: {colors[_token]};"
                "border: 1px solid rgba(128,128,128,0.4); border-radius: 5px;"
            )
        self._show_decorations(meta)

    def _show_decorations(self, meta: dict):
        """Chips com os slots gif/extras configurados no tema."""
        while self.decor_chips_row.count():
            item = self.decor_chips_row.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        gifs = meta.get("gif", {})
        extras = meta.get("extras", {})
        for slot, value in gifs.items():
            kind = (i18n.tr("themes.kind_url")
                    if value.startswith(("http://", "https://"))
                    else i18n.tr("themes.kind_file"))
            c = chip(f"gif.{slot} ({kind})", "ok")
            c.setToolTip(value)
            self.decor_chips_row.addWidget(c)
        for key, value in extras.items():
            if key == "header_text_color":
                continue  # cor do header_text: já está implícita no chip dele
            c = chip(f"extras.{key}", "accent")
            c.setToolTip(value)
            self.decor_chips_row.addWidget(c)
        if not gifs and not extras:
            self.decor_chips_row.addWidget(
                chip(i18n.tr("themes.no_decor"), "muted")
            )
        self.decor_chips_row.addStretch()

    def _on_selected(self, item):
        self._show_preview(item.text())

    def _apply(self):
        theme_id = self._selected_theme_id()
        if not theme_id:
            return
        theme.set_active_theme_id(theme_id)
        # Reaplica o QSS global — toda a interface muda na hora
        QApplication.instance().setStyleSheet(theme.build_qss())
        # Recria os gifs/textos de decoração do novo tema
        self.main.rebuild_decorations()
        self.chip_active.setText(i18n.tr("themes.active_chip", theme=theme_id))
        self.main.console.append_output(i18n.tr("themes.log_applied", id=theme_id))
        self.main.console.set_status(i18n.tr("themes.applied", id=theme_id))

    def _open_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(theme.THEMES_DIR)))

