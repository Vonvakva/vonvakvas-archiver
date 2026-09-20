"""Widgets reutilizaveis da GUI do Vonvakva's Archive."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import i18n


class Card(QFrame):
    """Painel arredondado com titulo opcional. Use .body() para o layout."""

    def __init__(self, title: str | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(18, 16, 18, 16)
        self._lay.setSpacing(10)
        self._title_lbl: QLabel | None = None
        if title:
            t = QLabel(title.upper())
            t.setObjectName("cardTitle")
            self._lay.addWidget(t)
            self._title_lbl = t

    def body(self) -> QVBoxLayout:
        return self._lay

    def set_title(self, title: str) -> None:
        """Actualiza o título do card (para retranslate)."""
        if self._title_lbl is not None:
            self._title_lbl.setText(title.upper())


class StatCard(QFrame):
    """Cartao de numero grande para o Dashboard."""

    def __init__(self, title: str, value="—", subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(4)

        self._title_lbl = QLabel(title.upper())
        self._title_lbl.setObjectName("cardTitle")
        self.value_lbl = QLabel(str(value))
        self.value_lbl.setObjectName("statValue")
        self.sub_lbl = QLabel(subtitle)
        self.sub_lbl.setObjectName("muted")
        self.sub_lbl.setWordWrap(True)

        lay.addWidget(self._title_lbl)
        lay.addWidget(self.value_lbl)
        lay.addWidget(self.sub_lbl)

    def set_title(self, title: str) -> None:
        """Actualiza o título do card (para retranslate)."""
        self._title_lbl.setText(title.upper())

    def set_value(self, value) -> None:
        self.value_lbl.setText(str(value))

    def set_subtitle(self, text: str) -> None:
        self.sub_lbl.setText(text)


def chip(text: str, state: str = "muted") -> QLabel:
    """Etiqueta colorida: state em {ok, bad, warn, muted, accent}."""
    lbl = QLabel(text)
    lbl.setObjectName(f"chip{state.capitalize()}")
    return lbl


class MetricChip(QLabel):
    """Chip de métrica viva (extensões): "Nome: valor", colorido por estado.

    Estados: ok / warn / bad / muted — as cores vêm do tema ativo.
    """

    _STATES = {"ok": "chipOk", "warn": "chipWarn", "bad": "chipBad",
               "muted": "chipMuted"}

    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self._name = name
        self.setObjectName("chipMuted")
        self.setText(name)
        self.setToolTip(i18n.tr("widget.ext_tip", name=name))

    def retranslate(self) -> None:
        self.setToolTip(i18n.tr("widget.ext_tip", name=self._name))

    def update_value(self, text: str, state: str = "ok") -> None:
        self.setText(f"{self._name}: {text}")
        new = self._STATES.get(state, "chipMuted")
        if new != self.objectName():
            self.setObjectName(new)
            self.style().unpolish(self)
            self.style().polish(self)


class PathEdit(QWidget):
    """QLineEdit embalado, com placeholder e callback opcional."""

    def __init__(self, placeholder: str = "", parent=None):
        self._le = QLineEdit(parent)
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._le)
        if placeholder:
            self._le.setPlaceholderText(placeholder)
        self.on_change = None
        self._le.textChanged.connect(self._emit)

    def _emit(self, _text) -> None:
        if self.on_change:
            self.on_change()

    def set_text(self, text: str) -> None:
        self._le.setText(text)

    def set_placeholder(self, text: str) -> None:
        self._le.setPlaceholderText(text)

    def text(self) -> str:
        return self._le.text()


class ConsolePanel(QWidget):
    """Console compartilhado: mostra a saida ao vivo dos scripts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        import i18n
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        head = QHBoxLayout()
        head.setSpacing(8)
        title = QLabel(i18n.tr("console.title"))
        title.setObjectName("cardTitle")
        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("consoleStatus")
        self.btn_clear = QPushButton(i18n.tr("console.clear"))
        self.btn_clear.setObjectName("ghost")
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_stop = QPushButton(i18n.tr("console.stop"))
        self.btn_stop.setObjectName("danger")
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setToolTip(i18n.tr("console.stop_tip"))
        self.btn_stop.setEnabled(False)
        self.btn_toggle = QPushButton(i18n.tr("console.hide"))
        self.btn_toggle.setObjectName("ghost")
        self.btn_toggle.setCursor(Qt.PointingHandCursor)

        head.addWidget(title)
        head.addWidget(self.status_lbl)
        head.addStretch()
        head.addWidget(self.btn_clear)
        head.addWidget(self.btn_stop)
        head.addWidget(self.btn_toggle)

        self.view = QPlainTextEdit()
        self.view.setObjectName("console")
        self.view.setReadOnly(True)
        self.view.setMaximumBlockCount(5000)
        self.view.setPlaceholderText(i18n.tr("console.placeholder"))

        lay.addLayout(head)
        lay.addWidget(self.view)

        self.btn_clear.clicked.connect(self.view.clear)
        self.btn_toggle.clicked.connect(self.toggle)
        self._collapsed = False

    def retranslate(self) -> None:
        import i18n
        for w in self.findChildren(QLabel):
            if w.objectName() == "cardTitle":
                w.setText(i18n.tr("console.title"))
        self.btn_clear.setText(i18n.tr("console.clear"))
        self.btn_stop.setText(i18n.tr("console.stop"))
        self.btn_stop.setToolTip(i18n.tr("console.stop_tip"))
        self.btn_toggle.setText(self._text_for_state())
        self.view.setPlaceholderText(i18n.tr("console.placeholder"))

    def _text_for_state(self) -> str:
        import i18n
        return i18n.tr("console.show" if self._collapsed else "console.hide")

    def append_output(self, text: str) -> None:
        self.view.moveCursor(QTextCursor.End)
        self.view.insertPlainText(text)
        self.view.ensureCursorVisible()

    def set_status(self, text: str) -> None:
        self.status_lbl.setText(text)

    def toggle(self) -> None:
        self._collapsed = not self._collapsed
        self.view.setVisible(not self._collapsed)
        self.btn_toggle.setText(self._text_for_state())

class InteractiveCard(QWidget):
    """Card interativo para extensões com botões de ação.

    Mostra o nome da extensão, valor atual e botões definidos em INTERACTIONS.
    O sinal action_clicked é emitido com (ext_id, action_id) quando um botão é clicado.
    """

    action_clicked = Signal(str, str)  # ext_id, action_id

    def __init__(self, ext, parent=None):
        super().__init__(parent)
        self._ext_id = ext.id
        self._ext_name = ext.name
        self._interactions = ext.interactions

        self.setObjectName("interactiveCard")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(10)

        # ---- Nome da extensão ----
        name_lbl = QLabel(ext.name.upper())
        name_lbl.setObjectName("cardTitle")
        lay.addWidget(name_lbl)

        # ---- Valor atual ----
        self._value_lbl = QLabel(ext.last_text)
        self._value_lbl.setObjectName("muted")
        lay.addWidget(self._value_lbl)

        lay.addStretch()

        # ---- Botões de interação ----
        self._buttons: dict[str, QPushButton] = {}
        for interaction in ext.interactions:
            btn = QPushButton(interaction.get("label", "?"))
            btn.setObjectName("extBtn")
            btn.setCursor(Qt.PointingHandCursor)
            if interaction.get("tooltip"):
                btn.setToolTip(interaction["tooltip"])
            btn.clicked.connect(
                lambda _=False, aid=interaction["id"]: self._on_clicked(aid)
            )
            lay.addWidget(btn)
            self._buttons[interaction["id"]] = btn

    def _on_clicked(self, action_id: str) -> None:
        self.action_clicked.emit(self._ext_id, action_id)

    def update_value(self, text: str, state: str = "ok") -> None:
        self._value_lbl.setText(text)
        # Atualiza estilo baseado no estado
        state_styles = {
            "ok": "color: @success;",
            "warn": "color: @warning;",
            "bad": "color: @danger;",
            "muted": "color: @muted;",
        }
        self._value_lbl.setStyleSheet(state_styles.get(state, ""))

    def set_busy(self, busy: bool) -> None:
        """Desabilita/habilita todos os botões."""
        for btn in self._buttons.values():
            btn.setEnabled(not busy)

    def retranslate(self) -> None:
        """As labels das interações vêm da extensão (não traduzíveis aqui);
        apenas refrescamos o tooltip do valor."""
        pass