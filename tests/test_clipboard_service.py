from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication

from app.services.clipboard_service import (
    copy_text_to_clipboard,
    copy_widget_as_pixmap,
)


def test_copy_text_to_clipboard_sets_text(qtbot):
    copy_text_to_clipboard("hello world")

    clipboard = QApplication.clipboard()
    assert clipboard.text() == "hello world"


def test_copy_widget_as_pixmap_returns_qpixmap(qtbot):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Akihabarai Score"))
    widget.resize(200, 100)
    widget.show()
    qtbot.addWidget(widget)

    pixmap = copy_widget_as_pixmap(widget)

    assert isinstance(pixmap, QPixmap)
    assert pixmap.width() > 0
    assert pixmap.height() > 0


def test_copy_widget_as_pixmap_writes_to_clipboard(qtbot):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Clipboard test"))
    widget.resize(180, 80)
    widget.show()
    qtbot.addWidget(widget)

    pixmap = copy_widget_as_pixmap(widget)

    clipboard = QApplication.clipboard()
    clip_pm = clipboard.pixmap()

    assert isinstance(pixmap, QPixmap)
    assert not clip_pm.isNull()


def test_copy_widget_as_pixmap_handles_small_widget(qtbot):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("X"))
    widget.resize(20, 20)
    widget.show()
    qtbot.addWidget(widget)

    pixmap = copy_widget_as_pixmap(widget)

    assert isinstance(pixmap, QPixmap)
    assert pixmap.width() > 0
    assert pixmap.height() > 0