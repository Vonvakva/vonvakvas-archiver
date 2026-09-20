"""Página Editor: edita os arquivos de config direto na GUI.

O arquivo carregado segue a regra do config_path do backend (perfil ->
HDD -> projeto). Ao salvar con un perfil ativo, grava no PERFIL (criando
o arquivo se non existir aínda) — así o perfil pasa a ser a fonte da
verdade dese arquivo.
"""

from __future__ import annotations

import shutil

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

import backend
from widgets import Card, chip
from i18n import tr


class EditorPage(QWidget):
    def __init__(self, runner, main):
        super().__init__()
        self.runner = runner
        self.main = main
        self.current_file: str | None = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 0, 4, 16)
        lay.setSpacing(16)

        splitter = QSplitter(Qt.Horizontal)

        # ---------------- lista de arquivos ----------------
        files_widget = QWidget()
        fv = QVBoxLayout(files_widget)
        fv.setContentsMargins(0, 0, 0, 0)
        fv.setSpacing(8)
        self.files_list = QListWidget()
        self.files_list.setMaximumWidth(330)
        self.files_list.itemClicked.connect(self._on_file_clicked)
        for entry in backend.EDITOR_FILES:
            self.files_list.addItem(entry["name"])
        fv.addWidget(self.files_list, 1)
        splitter.addWidget(files_widget)

        # ---------------- editor ----------------
        edit_widget = QWidget()
        ev = QVBoxLayout(edit_widget)
        ev.setContentsMargins(0, 0, 0, 0)
        ev.setSpacing(8)

        info_row = QHBoxLayout()
        self.source_chip = chip("", "muted")
        self.desc_lbl = QLabel("")
        self.desc_lbl.setObjectName("muted")
        self.desc_lbl.setWordWrap(True)
        info_row.addWidget(self.source_chip)
        info_row.addWidget(self.desc_lbl, 1)
        ev.addLayout(info_row)

        self.edit = QPlainTextEdit()
        self.edit.setObjectName("fileEdit")
        self.edit.setPlaceholderText(tr("editor.placeholder"))
        ev.addWidget(self.edit, 1)

        btns = QHBoxLayout()
        self.btn_save = QPushButton(tr("btn.save"))
        self.btn_save.setObjectName("accent")
        self.btn_save.clicked.connect(self._save)
        self.btn_reload = QPushButton(tr("btn.reload"))
        self.btn_reload.clicked.connect(self._load_current)
        self.btn_to_profile = QPushButton(tr("editor.btn_to_profile"))
        self.btn_to_profile.setToolTip(tr("editor.btn_to_profile_tip"))
        self.btn_to_profile.clicked.connect(self._copy_to_profile)
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_reload)
        btns.addWidget(self.btn_to_profile)
        btns.addStretch()
        ev.addLayout(btns)
        splitter.addWidget(edit_widget)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        lay.addWidget(splitter, 1)

        self.refresh()

    # ------------------------------------------------------------------

    def retranslate(self):
        """Actualiza os textos da interfaz (chamado por main.retranslate_all)."""
        self.setWindowTitle(tr("editor.title"))
        self.btn_save.setText(tr("btn.save"))
        self.btn_reload.setText(tr("btn.reload"))
        self.btn_to_profile.setText(tr("editor.btn_to_profile"))
        self.btn_to_profile.setToolTip(tr("editor.btn_to_profile_tip"))
        self.edit.setPlaceholderText(tr("editor.placeholder"))
        self._update_source_chip()

    # ------------------------------------------------------------------

    def refresh(self):
        self._update_source_chip()
        if self.current_file:
            self._load_current()

    def select_file(self, name: str):
        matches = self.files_list.findItems(name, Qt.MatchExactly)
        if matches:
            self.files_list.setCurrentItem(matches[0])
        self.current_file = name
        self._load_current()

    def set_busy(self, busy: bool):
        self.btn_save.setEnabled(not busy)
        self.btn_reload.setEnabled(not busy)
        self.btn_to_profile.setEnabled(not busy)

    # ------------------------------------------------------------------

    def _on_file_clicked(self, item):
        self.current_file = item.text()
        self._load_current()

    def _load_current(self):
        if not self.current_file:
            return
        entry = backend.editor_entry(self.current_file) or {}
        self.desc_lbl.setText(entry.get("desc", ""))
        try:
            self.edit.setPlainText(backend.read_editor_file(self.current_file))
        except OSError as exc:
            QMessageBox.warning(
                self, tr("editor.title"), tr("editor.warn_read", exc=str(exc))
            )
        self._update_source_chip()

    def _update_source_chip(self):
        if not self.current_file:
            self.source_chip.setText(tr("editor.source_none"))
            self.source_chip.setObjectName("chipMuted")
        else:
            path = backend.editor_read_path(self.current_file)
            scope = backend.editor_entry(self.current_file)["scope"]
            exists = path.exists()
            if scope == "auto":
                perfil = backend.active_profile()
                self.source_chip.setText(
                    f"{tr('editor.perfil_label')}: {perfil or tr('editor.default')}"
                )
            elif scope == "global":
                self.source_chip.setText(tr("editor.source_global"))
            else:
                self.source_chip.setText(tr("editor.source_root"))
            self.source_chip.setToolTip(
                str(path) + ("" if exists else tr("editor.will_be_created"))
            )
        self.source_chip.style().unpolish(self.source_chip)
        self.source_chip.style().polish(self.source_chip)

    def _save(self):
        if not self.current_file:
            return
        path = backend.write_editor_file(self.current_file, self.edit.toPlainText())
        self.main.console.append_output(tr("editor.saved_log", path=path))
        self.main.console.set_status(tr("editor.saved_status", name=path.name))
        self._update_source_chip()
        self.main.refresh_all()

    def _copy_to_profile(self):
        perfil = backend.active_profile()
        if not perfil:
            QMessageBox.information(
                self, tr("editor.title"), tr("editor.no_perfil")
            )
            return
        if not self.current_file:
            return
        src = backend.editor_read_path(self.current_file)
        dst = backend.editor_save_path(self.current_file)
        if src == dst:
            QMessageBox.information(
                self, tr("editor.title"),
                tr("editor.already_profile", name=self.current_file)
            )
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        self.main.console.append_output(
            tr("editor.copied_to_profile", perfil=perfil, dst=dst)
        )
        self._update_source_chip()
