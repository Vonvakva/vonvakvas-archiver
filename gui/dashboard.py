"""Página Dashboard: visão geral do arquivo (dados reais do backend)."""

from __future__ import annotations

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import backend
import extmgr
import i18n
from widgets import Card, StatCard, InteractiveCard, chip


class DashboardPage(QWidget):
    def __init__(self, runner, main):
        super().__init__()
        self.runner = runner
        self.main = main

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 0, 4, 16)
        lay.setSpacing(16)

        # ---- cartões de estatística (linha 1) ----
        grid = QGridLayout()
        grid.setSpacing(12)
        self.card_channels = StatCard(
            i18n.tr("dash.stats.channels"), subtitle=i18n.tr("dash.sub.channels"))
        self.card_videos = StatCard(
            i18n.tr("dash.stats.videos"), subtitle=i18n.tr("dash.sub.videos"))
        self.card_saved = StatCard(
            i18n.tr("dash.stats.saved"), subtitle=i18n.tr("dash.sub.saved"))
        self.card_dirs = StatCard(
            i18n.tr("dash.stats.dirs"), subtitle=i18n.tr("dash.sub.dirs"))
        for i, card in enumerate(
            [self.card_channels, self.card_videos, self.card_saved, self.card_dirs]
        ):
            grid.addWidget(card, 0, i)

        # ---- cartões de estatística (linha 2) ----
        self.card_disk = StatCard(
            i18n.tr("dash.stats.disk"), subtitle=i18n.tr("dash.sub.disk"))
        self.card_profile = StatCard(
            i18n.tr("dash.stats.profile"), subtitle=i18n.tr("dash.sub.profile"))
        grid.addWidget(self.card_disk, 1, 0)
        grid.addWidget(self.card_profile, 1, 1)
        lay.addLayout(grid)

        # slot de decoração do tema (gif.dashboard), alinhado à direita
        self._decor_theme_id: str | None = None
        self._decor_box = QHBoxLayout()
        self._decor_box.addStretch()
        lay.addLayout(self._decor_box)

        # card das extensões WHERE=dashboard (só aparece se houver alguma)
        self.ext_card = Card(i18n.tr("dash.ext_card"))
        self._ext_box = QHBoxLayout()
        self._ext_box.setSpacing(12)
        self.ext_card.body().addLayout(self._ext_box)
        self.ext_card.setVisible(False)
        lay.addWidget(self.ext_card)
        self._ext_cards: dict[str, StatCard] = {}
        _mgr = extmgr.get_manager()
        _mgr.reloaded.connect(self.rebuild_extensions)
        _mgr.updated.connect(self._update_ext_values)
        self.rebuild_extensions()

        # ---- ferramentas e config ----
        self.tools_card = Card(i18n.tr("dash.tools"))
        chips_row = QHBoxLayout()
        chips_row.setSpacing(8)
        self.chips_row = chips_row
        self.tools_card.body().addLayout(chips_row)
        self.btn_open = QPushButton(i18n.tr("dash.open_workdir"))
        self.btn_open.setToolTip(i18n.tr("dash.open_workdir_tip"))
        self.btn_open.clicked.connect(self._open_workdir)
        row = QHBoxLayout()
        row.addWidget(self.btn_open)
        row.addStretch()
        self.tools_card.body().addLayout(row)
        lay.addWidget(self.tools_card)

        # ---- pastas + ações ----
        bottom = QHBoxLayout()
        bottom.setSpacing(16)

        self.dirs_card = Card(i18n.tr("dash.dirs_card"))
        self.dirs_list = QListWidget()
        self.dirs_list.setMaximumHeight(170)
        self.dirs_list.itemDoubleClicked.connect(self._open_in_organize)
        self.dirs_card.body().addWidget(self.dirs_list)
        self.dirs_hint = QLabel()
        self.dirs_hint.setObjectName("muted")
        self.dirs_hint.setWordWrap(True)
        self.dirs_card.body().addWidget(self.dirs_hint)
        bottom.addWidget(self.dirs_card, 3)

        self.quick_card = Card(i18n.tr("dash.quick_card"))
        self.btn_check = QPushButton(i18n.tr("dash.btn_check"))
        self.btn_check.setObjectName("accent")
        self.btn_check.clicked.connect(self._run_check)
        self.btn_mass = QPushButton(i18n.tr("dash.btn_mass"))
        self.btn_mass.setToolTip(i18n.tr("dash.btn_mass_tip"))
        self.btn_mass.clicked.connect(self._run_mass)
        self.btn_mass_names = QPushButton(i18n.tr("dash.btn_mass_names"))
        self.btn_mass_names.setToolTip(i18n.tr("dash.btn_mass_names_tip"))
        self.btn_mass_names.clicked.connect(self._run_mass_names)
        self.btn_monitor = QPushButton(i18n.tr("dash.btn_monitor"))
        self.btn_monitor.clicked.connect(lambda: self.main.show_page("monitor"))
        self.quick_card.body().addWidget(self.btn_check)
        self.quick_card.body().addWidget(self.btn_mass)
        self.quick_card.body().addWidget(self.btn_mass_names)
        self.quick_card.body().addWidget(self.btn_monitor)
        self.quick_note = QLabel(i18n.tr("dash.quick_note"))
        self.quick_note.setObjectName("muted")
        self.quick_note.setWordWrap(True)
        self.quick_card.body().addWidget(self.quick_note)
        bottom.addWidget(self.quick_card, 2)

        lay.addLayout(bottom)
        lay.addStretch()

        self.refresh()

    # ------------------------------------------------------------------

    def retranslate(self):
        """Re-aplica todos os textos ao idioma ativo."""
        self.card_channels.set_title(i18n.tr("dash.stats.channels"))
        self.card_channels.set_subtitle(i18n.tr("dash.sub.channels"))
        self.card_videos.set_title(i18n.tr("dash.stats.videos"))
        self.card_videos.set_subtitle(i18n.tr("dash.sub.videos"))
        self.card_saved.set_title(i18n.tr("dash.stats.saved"))
        self.card_saved.set_subtitle(i18n.tr("dash.sub.saved"))
        self.card_dirs.set_title(i18n.tr("dash.stats.dirs"))
        self.card_dirs.set_subtitle(i18n.tr("dash.sub.dirs"))
        self.card_disk.set_title(i18n.tr("dash.stats.disk"))
        self.card_disk.set_subtitle(i18n.tr("dash.sub.disk"))
        self.card_profile.set_title(i18n.tr("dash.stats.profile"))
        self.card_profile.set_subtitle(i18n.tr("dash.sub.profile"))
        self.ext_card.set_title(i18n.tr("dash.ext_card"))
        self.tools_card.set_title(i18n.tr("dash.tools"))
        self.btn_open.setText(i18n.tr("dash.open_workdir"))
        self.btn_open.setToolTip(i18n.tr("dash.open_workdir_tip"))
        self.dirs_card.set_title(i18n.tr("dash.dirs_card"))
        self.quick_card.set_title(i18n.tr("dash.quick_card"))
        self.btn_check.setText(i18n.tr("dash.btn_check"))
        self.btn_mass.setText(i18n.tr("dash.btn_mass"))
        self.btn_mass.setToolTip(i18n.tr("dash.btn_mass_tip"))
        self.btn_mass_names.setText(i18n.tr("dash.btn_mass_names"))
        self.btn_mass_names.setToolTip(i18n.tr("dash.btn_mass_names_tip"))
        self.btn_monitor.setText(i18n.tr("dash.btn_monitor"))
        self.quick_note.setText(i18n.tr("dash.quick_note"))
        self.refresh()

    # ------------------------------------------------------------------

    def refresh(self):
        self.card_channels.set_value(len(backend.read_channel_list()))
        self.card_videos.set_value(backend.archive_history_count())
        self.card_saved.set_value(len(backend.successful_channels()))
        workdir = backend.channels_dir()
        self.card_dirs.set_value(len(backend.list_channel_dirs()))
        self.card_dirs.set_subtitle(i18n.tr("dash.dirs_em", dir=workdir))
        self.card_profile.set_value(
            backend.active_profile() or i18n.tr("dash.profile_default"))

        free, total = backend.disk_usage()
        if total > 0:
            self.card_disk.set_value(backend.fmt_bytes(free))
            pct = 100 * (total - free) / total
            self.card_disk.set_subtitle(i18n.tr(
                "dash.disk_total", total=backend.fmt_bytes(total), pct=f"{pct:.0f}"
            ))
        else:
            self.card_disk.set_value("—")
            self.card_disk.set_subtitle(i18n.tr("header.disk_na"))

        self.dirs_hint.setText(
            i18n.tr("dash.dirs_hint_full", dir=workdir)
        )

        # chips de ferramentas
        while self.chips_row.count():
            item = self.chips_row.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        for name, ok in backend.tool_status().items():
            c = chip(name, "ok" if ok else "bad")
            c.setToolTip(
                i18n.tr("dash.tool_ok", name=name) if ok
                else i18n.tr("dash.tool_missing", name=name)
            )
            self.chips_row.addWidget(c)
        self.chips_row.addStretch()

        # pastas
        dirs = backend.list_channel_dirs()
        self.dirs_list.clear()
        self.dirs_list.addItems(dirs) if dirs else self.dirs_list.addItem(
            i18n.tr("dash.dirs_empty")
        )

    def set_busy(self, busy: bool):
        self.btn_check.setEnabled(not busy)
        self.btn_mass.setEnabled(not busy)
        self.btn_mass_names.setEnabled(not busy)

    def rebuild_decorations(self):
        """Gif do tema no dashboard (slot gif.dashboard), se configurado."""
        import theme
        from decor import make_gif

        meta = theme.load_theme_meta()
        if meta["id"] == self._decor_theme_id:
            return
        self._decor_theme_id = meta["id"]

        while self._decor_box.count():
            item = self._decor_box.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._decor_box.addStretch()

        gif = meta.get("gif", {}).get("dashboard", "")
        if gif:
            widget = make_gif(meta["id"], gif, max_height=100)
            if widget is not None:
                self._decor_box.addWidget(widget)

    def rebuild_extensions(self):
        """StatCards/InteractiveCards das extensões WHERE=dashboard."""
        while self._ext_box.count():
            item = self._ext_box.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._ext_cards.clear()

        exts = extmgr.get_manager().by_where("dashboard")
        for ext in exts:
            if ext.has_interactions():
                card = InteractiveCard(ext)
                card.action_clicked.connect(self._on_ext_action)
            else:
                card = StatCard(ext.name, value=ext.last_text)
            self._ext_box.addWidget(card, 1)
            self._ext_cards[ext.id] = card
        self.ext_card.setVisible(bool(exts))

    def _on_ext_action(self, ext_id: str, action_id: str) -> None:
        """Callback quando um botão de extensão é clicado."""
        mgr = extmgr.get_manager()
        ext = mgr.extensions.get(ext_id)
        if ext is not None:
            ext.handle_action(action_id)

    def _update_ext_values(self):
        mgr = extmgr.get_manager()
        for ext_id, card in self._ext_cards.items():
            ext = mgr.extensions.get(ext_id)
            if ext is None:
                continue
            if isinstance(card, InteractiveCard):
                card.update_value(ext.last_text, ext.last_state)
            else:
                card.set_value(ext.last_text)
                sub = i18n.tr("dash.ext_refresh", refresh=ext.refresh)
                if ext.error:
                    sub += f" • {ext.error}"
                card.set_subtitle(sub)

    # ------------------------------------------------------------------

    def _open_workdir(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(backend.channels_dir())))

    def _open_in_organize(self, item):
        name = item.text()
        if name.startswith("("):
            return
        self.main.open_organize_with(str(backend.channels_dir() / name))

    def _run_check(self):
        self.runner.run(["check"])

    def _run_mass(self):
        # Reaproveita o diálogo da página Em massa (pergunta a mascara)
        self.main.pages["mass"]._run_archive()

    def _run_mass_names(self):
        # Reaproveita o diálogo da página Em massa, variante completa (ntsn)
        self.main.pages["mass"]._run_archive_names()
