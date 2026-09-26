"""Página Perfis: instâncias isoladas de configuração.

Cada perfil vive em config/profiles/<nome>/ e pode ter a própria
channel_list.txt, cookies, telegram.env, archive.txt e settings.env
(CHANNELS_ROOT próprio). O backend (common.sh) usa o perfil ativo via
variável de ambiente VONVAKVAS_PROFILE — os mesmos comandos vonvakvas
continuam funcionando no terminal com:

    VONVAKVAS_PROFILE=nome ./vonvakvas.sh mass-archive

A mesma lista é gerenciável pela CLI, com a mesma persistência
(config/gui_state.env -> GUI_PROFILE), então nada se perde entre os dois:

    vonvakvas profile list
    vonvakvas profile use nome
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import backend
import i18n
from widgets import Card, chip


class ProfilesPage(QWidget):
    def __init__(self, runner, main):
        super().__init__()
        self.runner = runner
        self.main = main

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 0, 4, 16)
        lay.setSpacing(16)

        # ---------------- lista + ações ----------------
        self.card = Card(i18n.tr("profiles.title"))
        row = QHBoxLayout()
        self.chip_active = chip("", "accent")
        row.addWidget(self.chip_active)
        row.addStretch()
        self.card.body().addLayout(row)

        self.list = QListWidget()
        self.list.setMinimumHeight(200)
        self.list.itemDoubleClicked.connect(lambda _item: self._activate())
        self.card.body().addWidget(self.list)

        btns = QHBoxLayout()
        self.btn_activate = QPushButton(i18n.tr("profiles.btn_activate"))
        self.btn_activate.setObjectName("accent")
        self.btn_activate.clicked.connect(self._activate)
        self.btn_create = QPushButton(i18n.tr("profiles.btn_create"))
        self.btn_create.clicked.connect(self._create)
        self.btn_files = QPushButton(i18n.tr("profiles.btn_files"))
        self.btn_files.clicked.connect(self._show_files)
        self.btn_delete = QPushButton(i18n.tr("profiles.btn_delete"))
        self.btn_delete.setObjectName("danger")
        self.btn_delete.clicked.connect(self._delete)
        btns.addWidget(self.btn_activate)
        btns.addWidget(self.btn_create)
        btns.addWidget(self.btn_files)
        btns.addWidget(self.btn_delete)
        btns.addStretch()
        self.card.body().addLayout(btns)
        lay.addWidget(self.card)

        # ---------------- explicação ----------------
        self.help_card = Card(i18n.tr("profiles.help_title"))
        self.note = QLabel(i18n.tr("profiles.help_note"))
        self.note.setObjectName("muted")
        self.note.setWordWrap(True)
        self.help_card.body().addWidget(self.note)
        lay.addWidget(self.help_card)
        lay.addStretch()

        self.refresh()

    # ------------------------------------------------------------------

    def retranslate(self):
        """Re-aplica todos os textos ao idioma ativo."""
        self.card.set_title(i18n.tr("profiles.title"))
        self.help_card.set_title(i18n.tr("profiles.help_title"))
        self.btn_activate.setText(i18n.tr("profiles.btn_activate"))
        self.btn_create.setText(i18n.tr("profiles.btn_create"))
        self.btn_files.setText(i18n.tr("profiles.btn_files"))
        self.btn_delete.setText(i18n.tr("profiles.btn_delete"))
        self.note.setText(i18n.tr("profiles.help_note"))
        self.refresh()

    # ------------------------------------------------------------------

    def refresh(self):
        self.list.clear()
        perfis = backend.list_profiles()
        self.list.addItems(perfis) if perfis else self.list.addItem(
            i18n.tr("profiles.empty")
        )
        self.chip_active.setText(i18n.tr(
            "profiles.active_chip",
            name=backend.active_profile() or i18n.tr("settings.default_profile"),
        ))

    def set_busy(self, busy: bool):
        self.btn_activate.setEnabled(not busy)
        self.btn_create.setEnabled(not busy)
        self.btn_delete.setEnabled(not busy)
        self.btn_files.setEnabled(not busy)

    def _selected_profile(self) -> str | None:
        item = self.list.currentItem()
        if item is None:
            return None
        name = item.text()
        if name.startswith("("):
            return None
        return name

    # ------------------------------------------------------------------

    def _activate(self):
        name = self._selected_profile()
        if not name:
            QMessageBox.information(self, i18n.tr("profiles.title"),
                                    i18n.tr("profiles.sel_first"))
            return
        if name == backend.active_profile():
            return
        if self.runner.is_running():
            QMessageBox.warning(self, i18n.tr("profiles.title"),
                                i18n.tr("profiles.warn_running"))
            return
        backend.set_active_profile(name)
        self.main.header.refresh_profiles()
        self.main.refresh_all()
        self.main.console.append_output(i18n.tr("profiles.log_active", name=name))

    def _create(self):
        name, ok = QInputDialog.getText(
            self, i18n.tr("profiles.create_title"), i18n.tr("profiles.create_label")
        )
        if not ok:
            return
        error = backend.validate_profile_name(name)
        if error:
            QMessageBox.warning(self, i18n.tr("profiles.create_title"), error)
            return
        copy_base = QMessageBox.question(
            self,
            i18n.tr("profiles.create_title"),
            i18n.tr("profiles.create_q"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        ) == QMessageBox.Yes
        pdir = backend.create_profile(name, copy_base=copy_base)
        self.main.console.append_output(i18n.tr("profiles.log_created", path=pdir))
        self.refresh()

    def _show_files(self):
        name = self._selected_profile()
        if not name:
            QMessageBox.information(self, i18n.tr("profiles.title"),
                                    i18n.tr("profiles.sel_first"))
            return
        files = backend.profile_files(name)
        title = f"{i18n.tr('profiles.title')}: {name}"
        if files:
            QMessageBox.information(
                self, title, i18n.tr("profiles.files_of") + "\n• ".join(files)
            )
        else:
            QMessageBox.information(self, title, i18n.tr("profiles.no_files"))

    def _delete(self):
        name = self._selected_profile()
        if not name:
            QMessageBox.information(self, i18n.tr("profiles.title"),
                                    i18n.tr("profiles.sel_first"))
            return
        if name == backend.active_profile():
            QMessageBox.warning(self, i18n.tr("profiles.title"),
                                i18n.tr("profiles.del_active"))
            return
        answer = QMessageBox.question(
            self,
            i18n.tr("profiles.del_title"),
            i18n.tr("profiles.del_q", name=name),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        try:
            backend.delete_profile(name)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, i18n.tr("profiles.title"),
                                i18n.tr("profiles.del_fail", exc=exc))
            return
        self.main.console.append_output(i18n.tr("profiles.log_deleted", name=name))
        self.refresh()
        self.main.header.refresh_profiles()
