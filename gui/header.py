"""Header da GUI: perfil ativo + informacoes do sistema em tempo real.

Mostra no topo, sempre visivel:
  • seletor do perfil ativo (None = configuracao padrao do projeto)
  • hostname da maquina
  • sistema operacional
  • data e hora (atualiza a cada segundo)
  • espaço livre/total no DISCO onde vive a pasta dos canais (psutil)
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QPoint

import backend
import extmgr
import i18n
import theme
from decor import DecorText, make_gif
from widgets import MetricChip


def _info_label(title: str) -> QLabel:
    lbl = QLabel()
    lbl.setObjectName("headerLbl")
    lbl.setTextFormat(Qt.RichText)
    lbl.setToolTip(title)
    return lbl


class HeaderBar(QWidget):
    """Barra superior fixa. Emite profile_changed(str) — "" = padrão."""

    profile_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("header")
        self.setFixedHeight(56)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 8, 18, 8)
        lay.setSpacing(14)

        # ---- seletor de perfil ----
        self.lbl_perfil = QLabel(i18n.tr("header.profile"))
        self.lbl_perfil.setObjectName("cardTitle")
        lay.addWidget(self.lbl_perfil)

        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(190)
        self.profile_combo.setToolTip(i18n.tr("header.profile_tooltip"))
        self.profile_combo.currentIndexChanged.connect(self._on_profile_selected)
        lay.addWidget(self.profile_combo)

        lay.addStretch()

        # ---- frufrus do sistema ----
        self.lbl_host = _info_label(i18n.tr("header.tip_host"))
        self.lbl_os = _info_label(i18n.tr("header.tip_os"))
        self.lbl_date = _info_label(i18n.tr("header.tip_date"))
        self.lbl_disk = _info_label(i18n.tr("header.tip_disk"))
        for lbl in (self.lbl_host, self.lbl_os, self.lbl_date, self.lbl_disk):
            lay.addWidget(lbl)

        # ---- decoração do tema (gif/texto opcional) ----
        # widgets criados por rebuild_decorations(); guardamos a lista para
        # poder reconstruir quando o tema ativo mudar.
        self._decor_widgets: list[QWidget] = []
        self.rebuild_decorations()

        # ---- widgets das extensões (gui/extensions/*.py) ----
        self._ext_chips: dict[str, MetricChip] = {}
        _mgr = extmgr.get_manager()
        _mgr.reloaded.connect(self.rebuild_extensions)
        _mgr.updated.connect(self._update_ext_values)
        self.rebuild_extensions()

        # ---- timers ----
        self._clock = QTimer(self)
        self._clock.setInterval(1000)
        self._clock.timeout.connect(self._tick_clock)
        self._clock.start()

        self._disk_timer = QTimer(self)
        self._disk_timer.setInterval(30_000)  # 30s é suficiente para disco
        self._disk_timer.timeout.connect(self.refresh_disk)
        self._disk_timer.start()

        self.refresh_profiles()
        self._tick_clock()
        self.refresh_disk()

    # ------------------------------------------------------------------

    def refresh_profiles(self) -> None:
        current = backend.active_profile() or ""
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        self.profile_combo.addItem(i18n.tr("header.default_profile"), "")
        for name in backend.list_profiles():
            self.profile_combo.addItem(name, name)
        idx = self.profile_combo.findData(current)
        self.profile_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.profile_combo.blockSignals(False)

    def refresh_disk(self) -> None:
        free, total = backend.disk_usage()
        target = backend.channels_dir()
        if total > 0:
            pct_used = 100 * (total - free) / total
            self.lbl_disk.setText(
                i18n.tr("header.free_of",
                        free=backend.fmt_bytes(free),
                        total=backend.fmt_bytes(total),
                        pct=pct_used)
            )
        else:
            self.lbl_disk.setText(i18n.tr("header.disk_na"))
        self.lbl_disk.setToolTip(i18n.tr("header.disk_of", target=target))

    def retranslate(self) -> None:
        """Re-aplica os textos do header ao idioma ativo."""
        self.lbl_perfil.setText(i18n.tr("header.profile"))
        self.profile_combo.setToolTip(i18n.tr("header.profile_tooltip"))
        self.lbl_host.setToolTip(i18n.tr("header.tip_host"))
        self.lbl_os.setToolTip(i18n.tr("header.tip_os"))
        self.lbl_date.setToolTip(i18n.tr("header.tip_date"))
        self.lbl_disk.setToolTip(i18n.tr("header.tip_disk"))
        self.refresh_profiles()
        self.refresh_disk()
        # chips de extensões (MetricChip tem retranslate próprio)
        for chip_w in self._ext_chips.values():
            if hasattr(chip_w, "retranslate"):
                chip_w.retranslate()

    def _tick_clock(self) -> None:
        self.lbl_date.setText(backend.date_now())

    def _on_profile_selected(self, index: int) -> None:
        name = self.profile_combo.itemData(index) or ""
        self.profile_changed.emit(name)

    # ------------------------------------------------------------------
    # Decoração do tema (gif.header / extras.header_text)
    # ------------------------------------------------------------------

    def rebuild_decorations(self) -> None:
        """Recria os widgets de decoração do tema ativo no header."""
        lay = self.layout()
        for w in self._decor_widgets:
            lay.removeWidget(w)
            w.setParent(None)
            w.deleteLater()
        self._decor_widgets.clear()

        try:
            meta = theme.load_theme_meta()
        except Exception:
            return
        theme_id = meta["id"]
        extras = meta.get("extras", {})

        text = extras.get("header_text", "")
        if text:
            lbl = DecorText(text, extras.get("header_text_color"))
            lay.addWidget(lbl)
            self._decor_widgets.append(lbl)

        gif = meta.get("gif", {}).get("header", "")
        if gif:
            widget = make_gif(theme_id, gif, max_height=40)
            if widget is not None:
                lay.addWidget(widget)
                self._decor_widgets.append(widget)

    # ------------------------------------------------------------------
    # Extensões (gui/extensions/*.py) — chips de métricas no header
    # ------------------------------------------------------------------

    def rebuild_extensions(self) -> None:
        """Recria os chips/widgets das extensões marcadas com WHERE=header."""
        lay = self.layout()
        for chip_w in self._ext_chips.values():
            lay.removeWidget(chip_w)
            chip_w.setParent(None)
            chip_w.deleteLater()
        self._ext_chips.clear()

        exts = extmgr.get_manager().by_where("header")[:extmgr.HEADER_LIMIT]
        for ext in exts:
            if ext.has_interactions():
                # Extensões interativas: botão que abre menu popup
                chip_w = InteractiveHeaderChip(ext)
                chip_w.action_clicked.connect(self._on_ext_action)
            else:
                chip_w = MetricChip(ext.name)
                chip_w.update_value(ext.last_text, ext.last_state)
                if ext.error:
                    chip_w.setToolTip(f"{ext.name}\n\n{ext.error}")
            lay.addWidget(chip_w)
            self._ext_chips[ext.id] = chip_w

    def _on_ext_action(self, ext_id: str, action_id: str) -> None:
        """Callback quando um botão de extensão é clicado no header."""
        mgr = extmgr.get_manager()
        ext = mgr.extensions.get(ext_id)
        if ext is not None:
            ext.handle_action(action_id)

    def _update_ext_values(self) -> None:
        """Atualiza só os textos/estados (sem recriar widgets)."""
        mgr = extmgr.get_manager()
        for ext_id, chip_w in self._ext_chips.items():
            ext = mgr.extensions.get(ext_id)
            if ext is None:
                continue
            if isinstance(chip_w, InteractiveHeaderChip):
                chip_w.update_value(ext.last_text, ext.last_state)
            else:
                chip_w.update_value(ext.last_text, ext.last_state)
                chip_w.setToolTip(
                    i18n.tr("widget.ext_error", name=ext.name, error=ext.error)
                    if ext.error
                    else i18n.tr("widget.ext_tip", name=ext.name)
                )

class InteractiveHeaderChip(QPushButton):
    """Botão no header para extensões com interações.

    Mostra o nome e valor da extensão. Ao clicar, abre um menu popup
    com os botões de ação definidos em INTERACTIONS.
    """

    action_clicked = Signal(str, str)  # ext_id, action_id

    def __init__(self, ext, parent=None):
        super().__init__(parent)
        self._ext_id = ext.id
        self._ext_name = ext.name
        self._interactions = ext.interactions
        self.setObjectName("headerExtBtn")
        self.setCursor(Qt.PointingHandCursor)
        self.setText(f"{ext.name}: {ext.last_text}")
        self.setToolTip(ext.name)
        self.clicked.connect(self._show_menu)

    def _show_menu(self):
        menu = QMenu(self)
        for interaction in self._interactions:
            action = menu.addAction(interaction.get("label", "?"))
            if interaction.get("tooltip"):
                action.setToolTip(interaction["tooltip"])
        action = menu.exec_(self.mapToGlobal(QPoint(0, self.height())))
        if action is not None:
            # Encontra o action_id baseado no texto
            for interaction in self._interactions:
                if interaction.get("label") == action.text():
                    self.action_clicked.emit(self._ext_id, interaction["id"])
                    break

    def update_value(self, text: str, state: str = "ok") -> None:
        self.setText(f"{self._ext_name}: {text}")
