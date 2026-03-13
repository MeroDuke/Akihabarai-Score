from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QGuiApplication, QPainter, QPixmap


def copy_text_to_clipboard(text: str):
    QApplication.clipboard().setText(text)


def copy_widget_as_pixmap(widget, pad: int = 12) -> QPixmap:
    widget.layout().activate()
    widget.adjustSize()

    size = widget.sizeHint()
    if size.width() < 1 or size.height() < 1:
        size = widget.size()

    out = QPixmap(size.width() + pad * 2, size.height() + pad * 2)
    out.fill(widget.palette().window().color())

    p = QPainter(out)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.translate(pad, pad)
    widget.render(p)
    p.end()

    QGuiApplication.clipboard().setPixmap(out)

    return out