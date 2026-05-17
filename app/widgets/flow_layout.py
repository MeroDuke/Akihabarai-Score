from PyQt6.QtCore import QPoint, QRect, QSize, Qt
from PyQt6.QtWidgets import QLayout, QSizePolicy


class FlowLayout(QLayout):
    """Simple wrapping layout for card-like widgets.

    Qt does not provide a native wrapping HBox layout, so the Tier Board uses
    this layout to place cards left-to-right and continue on the next line when
    there is not enough horizontal space.
    """

    def __init__(self, parent=None, margin=0, horizontal_spacing=8, vertical_spacing=8):
        super().__init__(parent)
        self._items = []
        self._horizontal_spacing = horizontal_spacing
        self._vertical_spacing = vertical_spacing

        self.setContentsMargins(margin, margin, margin, margin)
        self.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

    def __del__(self):
        while self.count():
            self.takeAt(0)

    def addItem(self, item):
        self._items.append(item)

    def addWidget(self, widget):
        super().addWidget(widget)

    def insertWidget(self, index, widget):
        self.addChildWidget(widget)
        item = self._create_item(widget)
        index = max(0, min(index, len(self._items)))
        self._items.insert(index, item)
        self.invalidate()

    def _create_item(self, widget):
        # QWidgetItem is created internally by addItem when using QLayout.addWidget,
        # but insertWidget needs an item object. Import locally to keep imports tidy.
        from PyQt6.QtWidgets import QWidgetItem

        return QWidgetItem(widget)

    def removeWidget(self, widget):
        for index, item in enumerate(self._items):
            if item.widget() is widget:
                removed = self._items.pop(index)
                removed.widget().setParent(None)
                self.invalidate()
                return

        super().removeWidget(widget)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            item = self._items.pop(index)
            self.invalidate()
            return item
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self._items:
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        size += QSize(
            margins.left() + margins.right(),
            margins.top() + margins.bottom(),
        )
        return size

    def _do_layout(self, rect, test_only):
        margins = self.contentsMargins()
        effective_rect = rect.adjusted(
            margins.left(),
            margins.top(),
            -margins.right(),
            -margins.bottom(),
        )

        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        for item in self._items:
            widget = item.widget()
            if widget is not None and not widget.isVisible():
                continue

            item_size = item.sizeHint()
            space_x = self._horizontal_spacing
            space_y = self._vertical_spacing

            next_x = x + item_size.width() + space_x
            if (
                next_x - space_x > effective_rect.right()
                and line_height > 0
            ):
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item_size.width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item_size))

            x = next_x
            line_height = max(line_height, item_size.height())

        return y + line_height - rect.y() + margins.bottom()
