"""Página Ajustes: idioma + pasta dos canais (ex: HDD externo) por escopo.

Escreve CHANNELS_ROOT em settings.env — no PERFIL ativo (se houver) ou
no config/ do projeto. O backend (common.sh) carrega os dois: o do
perfil sobrescreve o do projeto. Além disso, se <pasta>/config/ existir,
seus arquivos têm prioridade como fallback por arquivo.

Também alberga o seletor de idioma (Português/Español/English), que se
aplica em vivo via i18n.set_language() + main.retranslate_all().
"""

from __future__ import annotations

import pathlib

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
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


class SettingsPage(QWidget):
    def __init__(self, runner, main):
        super().__init__()
        self.runner = runner
        self.main = main

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 0, 4, 16)
        lay.setSpacing(16)

        # ---------------- idioma ----------------
        self.lang_card = Card(i18n.tr("settings.lang_title"))
        lang_row = QHBoxLayout()
        self.lang_label = QLabel(i18n.tr("settings.lang_label"))
        self.lang_combo = QComboBox()
        self.lang_combo.setMinimumWidth(220)
        for code in i18n.languages():
            self.lang_combo.addItem(i18n.LANGUAGES[code], code)
        idx = self.lang_combo.findData(i18n.current_lang())
        self.lang_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        lang_row.addWidget(self.lang_label)
        lang_row.addWidget(self.lang_combo, 1)
        self.lang_card.body().addLayout(lang_row)
        self.lang_note = QLabel(i18n.tr("settings.lang_note"))
        self.lang_note.setObjectName("muted")
        self.lang_note.setWordWrap(True)
        self.lang_card.body().addWidget(self.lang_note)
        lay.addWidget(self.lang_card)

        # ---------------- pasta dos canais ----------------
        self.path_card = Card(i18n.tr("settings.channels_title"))
        row = QHBoxLayout()
        self.path_edit = PathEdit(i18n.tr("settings.path_placeholder"))
        row.addWidget(self.path_edit, 1)
        btn_browse = QPushButton(i18n.tr("btn.browse"))
        btn_browse.clicked.connect(self._browse)
        row.addWidget(btn_browse)
        self.path_card.body().addLayout(row)

        btns = QHBoxLayout()
        self.btn_save = QPushButton(i18n.tr("btn.save"))
        self.btn_save.setObjectName("accent")
        self.btn_save.clicked.connect(self._save)
        self.btn_reset = QPushButton(i18n.tr("settings.btn_reset"))
        self.btn_reset.clicked.connect(self._reset)
        self.btn_open = QPushButton(i18n.tr("settings.btn_open"))
        self.btn_open.clicked.connect(self._open)
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_reset)
        btns.addWidget(self.btn_open)
        btns.addStretch()
        self.path_card.body().addLayout(btns)

        chips = QHBoxLayout()
        self.chip_scope = chip("", "muted")
        self.chip_active = chip("", "muted")
        chips.addWidget(self.chip_scope)
        chips.addWidget(self.chip_active)
        chips.addStretch()
        self.path_card.body().addLayout(chips)

        self.note = QLabel(i18n.tr("settings.note"))
        self.note.setObjectName("muted")
        self.note.setWordWrap(True)
        self.path_card.body().addWidget(self.note)
        lay.addWidget(self.path_card)

        # ---------------- origem da config ----------------
        self.cfg_card = Card(i18n.tr("settings.origins_title"))
        self.list = QListWidget()
        self.list.setMaximumHeight(190)
        self.cfg_card.body().addWidget(self.list)

        acts = QHBoxLayout()
        self.btn_create = QPushButton(i18n.tr("settings.btn_create_cfg"))
        self.btn_create.clicked.connect(self._create_config)
        self.btn_copy = QPushButton(i18n.tr("settings.btn_copy_cfg"))
        self.btn_copy.setObjectName("accent")
        self.btn_copy.clicked.connect(self._copy_configs)
        acts.addWidget(self.btn_create)
        acts.addWidget(self.btn_copy)
        acts.addStretch()
        self.cfg_card.body().addLayout(acts)
        lay.addWidget(self.cfg_card)

        self.refresh()

    def retranslate(self):
        """Re-aplica todos os textos ao idioma ativo."""
        self._set_card_title(self.lang_card, i18n.tr("settings.lang_title"))
        self._set_card_title(self.path_card, i18n.tr("settings.channels_title"))
        self._set_card_title(self.cfg_card, i18n.tr("settings.origins_title"))
        self.lang_label.setText(i18n.tr("settings.lang_label"))
        self.lang_note.setText(i18n.tr("settings.lang_note"))
        self.path_edit.set_placeholder(i18n.tr("settings.path_placeholder"))
        self.btn_save.setText(i18n.tr("btn.save"))
        self.btn_reset.setText(i18n.tr("settings.btn_reset"))
        self.btn_open.setText(i18n.tr("settings.btn_open"))
        self.note.setText(i18n.tr("settings.note"))
        self.btn_create.setText(i18n.tr("settings.btn_create_cfg"))
        self.btn_copy.setText(i18n.tr("settings.btn_copy_cfg"))
        self.refresh()

    @staticmethod
    def _set_card_title(card, title: str):
        for w in card.findChildren(QLabel):
            if w.objectName() == "cardTitle":
                w.setText(title.upper())
                break

    def refresh(self):
        root = backend.load_channels_root()
        self.path_edit.set_text(str(root) if root else "")
        scope = backend.channels_root_scope()
        scope_key = {
            "profile": "settings.scope_profile",
            "project": "settings.scope_project",
            "default": "settings.scope_default",
        }.get(scope)
        scope_txt = i18n.tr(scope_key) if scope_key else scope
        self.chip_scope.setText(i18n.tr("settings.scope", scope=scope_txt))
        self.chip_scope.setToolTip(i18n.tr("settings.scope_tip", scope=scope_txt))
        self.chip_active.setText(
            i18n.tr("settings.active_profile",
                    name=backend.active_profile() or i18n.tr("settings.default_profile"))
        )

        # origem de cada arquivo (mesmo criterio do config_path)
        self.list.clear()
        pdir = backend.profile_dir()
        for name in sorted(backend.CONFIG_FILES):
            path = backend.effective_config_path(name)
            if pdir is not None and path.parent == pdir:
                origin = i18n.tr("settings.origin.profile")
            elif root is not None and path.parent == root / "config":
                origin = i18n.tr("settings.origin.root")
            else:
                origin = i18n.tr("settings.origin.project")
            exists = i18n.tr("settings.exists") if path.is_file() else i18n.tr("settings.missing")
            self.list.addItem(f"{name}  [{origin}]  {exists}")

        has_root = root is not None and root.is_dir()
        self.btn_create.setEnabled(has_root)
        self.btn_copy.setEnabled(has_root)
        self.btn_open.setEnabled(True)

    def set_busy(self, busy: bool):
        self.btn_save.setEnabled(not busy)
        self.btn_reset.setEnabled(not busy)

    # ------------------------------------------------------------------

    def _on_lang_changed(self, index: int):
        code = self.lang_combo.itemData(index) or ""
        if code == i18n.current_lang():
            return
        i18n.set_language(code)
        self.main.retranslate_all()
        self.main.console.set_status(
            i18n.tr("settings.lang_changed", lang=i18n.LANGUAGES[code])
        )

    def _browse(self):
        start = self.path_edit.text() or str(pathlib.Path.home())
        chosen = QFileDialog.getExistingDirectory(
            self, i18n.tr("settings.pick_folder"), start
        )
        if chosen:
            self.path_edit.set_text(chosen)

    def _save(self):
        path = self.path_edit.text().strip()
        if path:
            p = pathlib.Path(path).expanduser()
            if not p.is_dir():
                answer = QMessageBox.question(
                    self,
                    i18n.tr("settings.folder_missing_title"),
                    i18n.tr("settings.folder_missing_text", path=p),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if answer != QMessageBox.Yes:
                    return
                path = str(p)
        backend.write_channels_root(path or None)
        scope = i18n.tr("settings.scope_profile") if backend.profile_dir() \
            else i18n.tr("settings.scope_project")
        self.main.console.set_status(i18n.tr("settings.saved", scope=scope))
        self.refresh()
        self.main.refresh_all()

    def _reset(self):
        backend.write_channels_root(None)
        self.main.console.set_status(i18n.tr("settings.cleared"))
        self.refresh()
        self.main.refresh_all()

    def _open(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(backend.channels_dir())))

    def _create_config(self):
        root = backend.load_channels_root()
        if root is None or not root.is_dir():
            QMessageBox.warning(self, i18n.tr("settings.title"),
                                i18n.tr("settings.warn_valid_dir"))
            return
        (root / "config").mkdir(parents=True, exist_ok=True)
        self.refresh()

    def _copy_configs(self):
        root = backend.load_channels_root()
        if root is None or not root.is_dir():
            QMessageBox.warning(self, i18n.tr("settings.title"),
                                i18n.tr("settings.warn_valid_dir"))
            return
        copied = backend.copy_project_configs(root)
        if copied:
            QMessageBox.information(
                self, i18n.tr("settings.title"),
                i18n.tr("settings.copied") + "\n• ".join(copied)
            )
        else:
            QMessageBox.information(
                self, i18n.tr("settings.title"), i18n.tr("settings.copied_none")
            )
        self.refresh()
