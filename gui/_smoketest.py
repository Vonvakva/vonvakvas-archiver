"""GUI smoke test (runs offscreen, no visible window).

Usage: QT_QPA_PLATFORM=offscreen python gui/_smoketest.py
Validates: imports, theme, backend, creation of every page and the header.
"""

import os
import json
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication  # noqa: E402

import backend  # noqa: E402
import theme  # noqa: E402


def main() -> int:
    app = QApplication([])
    qss = theme.build_qss()
    assert "QPushButton" in qss and "#0d1017" in qss, "QSS sem tokens aplicados"
    print("[ok] theme.build_qss")

    print("[ok] backend.PROJECT_ROOT =", backend.PROJECT_ROOT)
    print("[ok] channels_dir =", backend.channels_dir())
    print("[ok] disk_usage =", backend.disk_usage())
    print("[ok] hostname/os =", backend.hostname(), "/", backend.os_name())
    print("[ok] profiles =", backend.list_profiles())

    from main import MainWindow

    win = MainWindow()
    win.show()
    app.processEvents()

    # visit every page
    for key in ("dash", "archive", "organize", "upload", "monitor",
                "mass", "editor", "profiles", "themes", "settings"):
        win.show_page(key)
        app.processEvents()
    print("[ok] all 10 pages visited without error")

    # theme system
    ids = [t["id"] for t in theme.list_themes()]
    print("[ok] themes found:", ids)
    assert "default" in ids, "tema padrao ausente"
    for tid in ids:
        qss = theme.build_qss() if tid == theme.get_active_theme_id() else ""
        colors = theme.load_theme_colors(tid)
        assert colors["accent"].startswith("#"), f"tema {tid} sem accent"
    print("[ok] all themes load valid colors")

    theme.set_active_theme_id("light")
    assert theme.get_active_theme_id() == "light"
    qss_light = theme.build_qss()
    assert "#f5f6fa" in qss_light, "tokens do tema light nao aplicados"
    assert "rgba(22, 163, 74, 0.1)" in qss_light, "chip derivado ausente"
    theme.set_active_theme_id("default")
    assert "#0d1017" in theme.build_qss()
    print("[ok] theme switch + derived chips")

    # decorations (optional theme gifs/texts)
    for t in theme.list_themes():
        assert "gif" in t and "extras" in t, f"tema {t['id']} sem secoes de decoracao"
    assert theme.load_theme_meta("default")["gif"] == {}, "campos vazios deveriam ser ignorados"

    from PySide6.QtGui import QPixmap

    test_id = "smoketest-decor"
    (theme.THEMES_DIR / test_id).mkdir(exist_ok=True)
    test_png = theme.THEMES_DIR / test_id / "teste.png"
    QPixmap(12, 12).save(str(test_png))
    (theme.THEMES_DIR / f"{test_id}.json").write_text(
        json.dumps({
            "name": "smoketest",
            "gif": {"sidebar": "teste.png", "header": "nao_existe.gif"},
            "extras": {"header_text": "teste decor", "header_text_color": "#fff",
                       "sidebar_text": "", "chave_desconhecida": "x"},
        }),
        encoding="utf-8",
    )
    meta = theme.load_theme_meta(test_id)
    assert meta["gif"] == {
        "sidebar": str(test_png),
        "header": str(theme.THEMES_DIR / test_id / "nao_existe.gif"),
    }, "gif: valores deveriam vir resolvidos para caminho absoluto"
    assert meta["extras"] == {
        "header_text": "teste decor", "header_text_color": "#fff",
    }, "extras: chaves desconhecidas/vazias deveriam ser filtradas"
    from decor import make_gif

    ok_widget = make_gif(test_id, meta["gif"]["sidebar"], max_height=40)
    assert ok_widget is not None, "gif local existente deveria virar widget"
    missing = make_gif(test_id, meta["gif"]["header"], max_height=40)
    assert missing is None, "arquivo inexistente deveria virar None"
    (theme.THEMES_DIR / f"{test_id}.json").unlink()
    QPixmap(1, 1)
    import shutil as _sh

    _sh.rmtree(theme.THEMES_DIR / test_id)
    print("[ok] decorations: local file, missing and extras filtering")

    # programmatic profile switch
    backend.set_active_profile("smoketest-tmp")
    assert backend.active_profile() == "smoketest-tmp"
    backend.set_active_profile(None)
    assert backend.active_profile() is None
    print("[ok] set_active_profile")

    win.close()
    print("SMOKE TEST OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())