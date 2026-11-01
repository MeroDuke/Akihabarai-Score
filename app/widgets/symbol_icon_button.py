"""Render static UI symbols as icons, not expensive fallback-font text."""

from PyQt6.QtCore import QEvent, QPointF, QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPalette, QPen, QPixmap, QPolygonF
from PyQt6.QtWidgets import QPushButton


class SymbolIconButton(QPushButton):
    """Keep existing translated captions, splitting their known symbol prefix."""

    PREFIXES = {"✏ ": "pencil", "🌐 ": "globe"}

    def __init__(self, text="", parent=None):
        self._symbol = None
        super().__init__(parent)
        self.setIconSize(QSize(16, 16))
        self.setText(text)

    def setText(self, text):
        self._symbol = None
        for prefix, symbol in self.PREFIXES.items():
            if text.startswith(prefix):
                self._symbol = symbol
                text = text[len(prefix):]
                break
        super().setText(text)
        self._refresh_symbol_icon()

    def _refresh_symbol_icon(self):
        if self._symbol is None:
            self.setIcon(QIcon())
            return
        ratio = self.devicePixelRatioF()
        pixmap = QPixmap(round(16 * ratio), round(16 * ratio))
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._symbol == "globe":
            painter.setPen(QPen(QColor("#007da3"), 1.2))
            painter.setBrush(QColor("#38bddd"))
            painter.drawEllipse(QRectF(1, 1, 14, 14))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor("#ffffff"), 1))
            painter.drawEllipse(QRectF(5, 1, 6, 14))
            painter.drawLine(QPointF(1, 8), QPointF(15, 8))
        else:
            color = self.palette().color(QPalette.ColorRole.ButtonText)
            painter.setPen(QPen(color, 1.2))
            painter.setBrush(color)
            painter.drawPolygon(QPolygonF([
                QPointF(3, 13), QPointF(4, 9), QPointF(11, 2),
                QPointF(14, 5), QPointF(7, 12),
            ]))
            painter.setPen(QPen(self.palette().color(QPalette.ColorRole.Button), 1))
            painter.drawLine(QPointF(10, 3), QPointF(13, 6))
        painter.end()
        self.setIcon(QIcon(pixmap))

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.Type.PaletteChange, QEvent.Type.ApplicationPaletteChange):
            self._refresh_symbol_icon()

    def event(self, event):
        result = super().event(event)
        if event.type() == QEvent.Type.DevicePixelRatioChange:
            self._refresh_symbol_icon()
        return result
