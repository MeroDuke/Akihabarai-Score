import pytest
from PyQt6.QtCore import QEvent
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

from app.widgets.symbol_icon_button import SymbolIconButton


@pytest.mark.parametrize("caption,expected", [
    ("✏ Offline", "Offline"), ("🌐 Online", "Online"),
    ("🌐 HU → EN", "HU → EN"), ("🌐 EN → HU", "EN → HU"),
])
def test_symbol_is_icon_not_text_for_native_size_calculation(qtbot, caption, expected):
    button = SymbolIconButton(caption)
    qtbot.addWidget(button)
    assert button.text() == expected
    assert not button.icon().isNull()
    assert button.iconSize().width() == 16
    assert button.sizeHint().isValid()


def test_runtime_mode_palette_and_dpi_changes_keep_button_usable(qtbot):
    button = SymbolIconButton("✏ Offline")
    qtbot.addWidget(button)
    button.show()
    first = button.icon().cacheKey()
    button.setText("🌐 Online")
    assert button.icon().cacheKey() != first
    palette = button.palette()
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#eeeeee"))
    button.setPalette(palette)
    QApplication.sendEvent(button, QEvent(QEvent.Type.DevicePixelRatioChange))
    assert button.text() == "Online"
    assert not button.icon().isNull()
    button.setText("Plain action")
    assert button.text() == "Plain action"
    assert button.icon().isNull()
