"""PyQt desktop operations kept outside application/domain services."""

from __future__ import annotations

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices, QGuiApplication, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QMessageBox


def set_clipboard_text(text: str) -> None:
    QApplication.clipboard().setText(text)


def set_clipboard_pixmap(pixmap: QPixmap) -> None:
    QGuiApplication.clipboard().setPixmap(pixmap)


def render_widget_to_clipboard_pixmap(widget, pad: int = 12) -> QPixmap:
    widget.layout().activate()
    widget.adjustSize()
    size = widget.sizeHint()
    if size.width() < 1 or size.height() < 1:
        size = widget.size()

    output = QPixmap(size.width() + pad * 2, size.height() + pad * 2)
    output.fill(widget.palette().window().color())
    painter = QPainter(output)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.translate(pad, pad)
    widget.render(painter)
    painter.end()
    set_clipboard_pixmap(output)
    return output


def trim_pixmap_background(pm: QPixmap, bg_color, pad: int = 12) -> QPixmap:
    image = pm.toImage().convertToFormat(pm.toImage().Format.Format_ARGB32)
    width, height = image.width(), image.height()
    bg_red, bg_green, bg_blue = bg_color.red(), bg_color.green(), bg_color.blue()
    left, right, top, bottom = width, -1, height, -1
    tolerance = 8
    for y in range(height):
        for x in range(width):
            color = image.pixelColor(x, y)
            if (
                abs(color.red() - bg_red) > tolerance
                or abs(color.green() - bg_green) > tolerance
                or abs(color.blue() - bg_blue) > tolerance
            ):
                left, right = min(left, x), max(right, x)
                top, bottom = min(top, y), max(bottom, y)

    if right < left or bottom < top:
        cropped = pm
    else:
        cropped = pm.copy(left, top, right - left + 1, bottom - top + 1)
    output = QPixmap(cropped.width() + pad * 2, cropped.height() + pad * 2)
    output.fill(bg_color)
    painter = QPainter(output)
    painter.drawPixmap(pad, pad, cropped)
    painter.end()
    return output


def process_desktop_events() -> None:
    QApplication.processEvents()


def desktop_clipboard():
    return QApplication.clipboard()


def open_native_url(url: str | QUrl) -> object:
    return QDesktopServices.openUrl(url if isinstance(url, QUrl) else QUrl(url))


def build_native_url(url: str) -> QUrl:
    return QUrl(url)


def show_warning(
    parent,
    title: str,
    message: str,
    *,
    message_box=QMessageBox,
) -> None:
    message_box.warning(parent, title, message)


def show_information(
    parent,
    title: str,
    message: str,
    *,
    message_box=QMessageBox,
) -> None:
    message_box.information(parent, title, message)


def show_critical(
    parent,
    title: str,
    message: str,
    *,
    message_box=QMessageBox,
) -> None:
    message_box.critical(parent, title, message)


def execute_modal_dialog(dialog) -> object:
    return dialog.exec()
