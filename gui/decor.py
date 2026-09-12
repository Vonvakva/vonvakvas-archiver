"""Widgets de decoração da GUI: GIFs/imagens e textos custom dos temas.

Fontes aceitas (definidas no JSON do tema, seções "gif" e "extras"):
  • URL http(s) — baixada para config/gui_cache/ (nome por hash da URL,
    então baixa uma vez só) e tocada a partir dali.
  • Arquivo local — resolvido por theme.resolve_asset() para
    gui/themes/<id>/, a pasta com o MESMO NOME do json do tema.

Falhas (URL fora do ar, arquivo inexistente, formato inválido) fazem o
widget sumir em silêncio — decoração nunca pode derrubar a GUI.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from PySide6.QtCore import QSize, QUrl, Qt
from PySide6.QtGui import QMovie, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

import theme

CACHE_DIR = theme.PROJECT_ROOT / "config" / "gui_cache"

_ANIMATED_EXTS = (".gif",)
_STATIC_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp")


def _cache_file(url: str) -> Path:
    """Caminho no cache para uma URL (hash sha1 + extensão se conhecida)."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ext = ".gif"
    lower = url.lower().split("?", 1)[0].split("#", 1)[0]
    for e in _ANIMATED_EXTS + _STATIC_EXTS:
        if lower.endswith(e):
            ext = e
            break
    return CACHE_DIR / (hashlib.sha1(url.encode("utf-8")).hexdigest() + ext)


class AnimatedImage(QWidget):
    """GIF animado (ou imagem estática) de URL ou arquivo local.

    A altura é limitada a max_height; a largura segue a proporção.
    Se a fonte falhar, o widget se esconde sozinho.
    """

    def __init__(self, source: str, max_height: int = 64, parent=None):
        super().__init__(parent)
        self._max_height = max_height
        self._movie: QMovie | None = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self._label = QLabel()
        self._label.setAlignment(Qt.AlignCenter)
        lay.addWidget(self._label)

        if source.startswith(("http://", "https://")):
            self._download(source)
        else:
            self._load(source)

    # ---------------- fontes ----------------

    def _download(self, url: str) -> None:
        self._nam = QNetworkAccessManager(self)
        reply = self._nam.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(lambda: self._on_downloaded(reply, url))

    def _on_downloaded(self, reply: QNetworkReply, url: str) -> None:
        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                self._give_up()
                return
            data = bytes(reply.readAll())
        finally:
            reply.deleteLater()
        if not data:
            self._give_up()
            return
        dest = _cache_file(url)
        try:
            dest.write_bytes(data)
        except OSError:
            self._give_up()
            return
        self._load(str(dest))

    def _load(self, path: str) -> None:
        lower = path.lower()
        if lower.endswith(_ANIMATED_EXTS):
            movie = QMovie(path)
            if not movie.isValid():
                self._give_up()
                return
            movie.resized.connect(
                lambda size, m=movie: self._scale_movie(m, size)
            )
            self._movie = movie
            self._label.setMovie(movie)
            movie.start()
        else:
            pm = QPixmap(path)
            if pm.isNull():
                self._give_up()
                return
            self._label.setPixmap(self._scaled(pm))

    # ---------------- helpers ----------------

    def _scale_movie(self, movie: QMovie, size: QSize) -> None:
        if size.height() <= 0:
            return
        if size.height() > self._max_height:
            ratio = self._max_height / size.height()
            movie.setScaledSize(
                QSize(int(size.width() * ratio), self._max_height)
            )

    def _scaled(self, pm: QPixmap) -> QPixmap:
        if pm.height() > self._max_height:
            return pm.scaledToHeight(self._max_height, Qt.SmoothTransformation)
        return pm

    def _give_up(self) -> None:
        self.hide()


class DecorText(QLabel):
    """Texto custom do tema (extras.header_text / sidebar_text)."""

    def __init__(self, text: str, color: str | None = None, parent=None):
        super().__init__(text, parent)
        self.setWordWrap(False)
        if color and color.strip().startswith("#"):
            self.setStyleSheet(f"color: {color.strip()};")


def make_gif(theme_id: str | None, value: str, max_height: int) -> AnimatedImage | None:
    """Fábrica: cria um AnimatedImage para um slot de gif, ou None se falhar."""
    try:
        resolved = theme.resolve_asset(theme_id, value)
    except Exception:
        return None
    if not resolved.startswith(("http://", "https://")) and not Path(resolved).is_file():
        return None
    return AnimatedImage(resolved, max_height=max_height)