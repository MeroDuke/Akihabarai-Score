# tests/test_result_render_service.py
from PyQt6.QtGui import QColor, QPixmap, QPainter

from app.services.result_render_service import trim_pixmap


def test_trim_pixmap_returns_qpixmap_for_uniform_background():
    pm = QPixmap(40, 30)
    bg = QColor("#ffffff")
    pm.fill(bg)

    out = trim_pixmap(pm, bg, pad=12)

    assert isinstance(out, QPixmap)
    assert out.width() == 40 + 24
    assert out.height() == 30 + 24


def test_trim_pixmap_returns_qpixmap_when_content_exists():
    pm = QPixmap(40, 30)
    bg = QColor("#ffffff")
    pm.fill(bg)

    painter = QPainter(pm)
    painter.fillRect(10, 8, 5, 4, QColor("#000000"))
    painter.end()

    out = trim_pixmap(pm, bg, pad=12)

    assert isinstance(out, QPixmap)
    assert out.width() > 0
    assert out.height() > 0


def test_trim_pixmap_with_content_is_not_larger_than_full_background_case():
    pm = QPixmap(40, 30)
    bg = QColor("#ffffff")
    pm.fill(bg)

    painter = QPainter(pm)
    painter.fillRect(10, 8, 5, 4, QColor("#000000"))
    painter.end()

    out = trim_pixmap(pm, bg, pad=12)

    assert out.width() <= 40 + 24
    assert out.height() <= 30 + 24


def test_trim_pixmap_respects_padding_for_small_content():
    pm = QPixmap(20, 20)
    bg = QColor("#ffffff")
    pm.fill(bg)

    painter = QPainter(pm)
    painter.fillRect(5, 5, 1, 1, QColor("#000000"))
    painter.end()

    out = trim_pixmap(pm, bg, pad=10)

    # 1x1 content köré legalább padding kerüljön
    assert out.width() >= 1 + 20
    assert out.height() >= 1 + 20