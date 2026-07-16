from PyQt6.QtCore import QPoint, QSize, QTimer, Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QStyle,
    QVBoxLayout,
)

from app.widgets.tier_board_widget import TierBoardWidget
from app.logger import log_debug


class TierPanelWidget(QGroupBox):
    DRAG_SCROLL_EDGE_SIZE = 56
    DRAG_SCROLL_STEP = 18
    DRAG_SCROLL_INTERVAL_MS = 30

    def __init__(self):
        super().__init__("Tier lista")
        self.flip_enabled = True
        self.setMinimumWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 10, 8, 10)
        layout.setSpacing(8)

        self.tier_board = TierBoardWidget()

        self.tier_scroll_area = QScrollArea()
        self.tier_scroll_area.setWidgetResizable(True)
        self.tier_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.tier_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.tier_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.tier_scroll_area.setWidget(self.tier_board)
        self.tier_scroll_area.verticalScrollBar().rangeChanged.connect(
            self._sync_vertical_scrollbar_safe_area
        )
        self._drag_scroll_direction = 0
        self._drag_scroll_timer = QTimer(self)
        self._drag_scroll_timer.setInterval(self.DRAG_SCROLL_INTERVAL_MS)
        self._drag_scroll_timer.timeout.connect(self._perform_drag_auto_scroll)
        self.tier_board.drag_position_changed.connect(
            self._update_drag_auto_scroll
        )
        self.tier_board.drag_scrolling_stopped.connect(
            self._stop_drag_auto_scroll
        )

        layout.addWidget(self.tier_scroll_area, 1)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)

        self.flip_all_tier_cards_btn = QPushButton("Összes kártya megfordítása")
        self.flip_all_tier_cards_btn.setFixedHeight(32)
        self.flip_all_tier_cards_btn.setEnabled(False)
        button_row.addWidget(self.flip_all_tier_cards_btn)

        self.clear_all_tier_cards_btn = QPushButton("Minden kártya törlése")
        self.clear_all_tier_cards_btn.setFixedHeight(32)
        self.clear_all_tier_cards_btn.setEnabled(False)
        button_row.addWidget(self.clear_all_tier_cards_btn)

        self.copy_tier_btn = QPushButton("Tier lista képként másolása")
        self.copy_tier_btn.setFixedHeight(32)
        self.copy_tier_btn.setEnabled(False)

        style = self.style()
        self.copy_tier_btn.setIcon(
            style.standardIcon(style.StandardPixmap.SP_FileDialogListView)
        )
        self.copy_tier_btn.setIconSize(QSize(16, 16))
        button_row.addWidget(self.copy_tier_btn)

        layout.addLayout(button_row)

    def update_buttons_state(self):
        has_saved_entries = self.tier_board.saved_entry_count() > 0
        has_flippable_entries = self.tier_board.has_flippable_entries()

        self.flip_all_tier_cards_btn.setEnabled(
            self.flip_enabled and has_flippable_entries
        )
        self.clear_all_tier_cards_btn.setEnabled(has_saved_entries)
        self.copy_tier_btn.setEnabled(has_saved_entries)

    def set_flip_enabled(self, enabled: bool) -> None:
        self.flip_enabled = enabled
        self.tier_board.set_flip_enabled(enabled)
        self.update_buttons_state()

    def _sync_vertical_scrollbar_safe_area(
        self,
        minimum: int,
        maximum: int,
    ) -> None:
        scrollbar_needed = maximum > minimum
        safe_width = 0
        if scrollbar_needed:
            safe_width = (
                self.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent)
                + 4
            )

        if not self.tier_board.set_scrollbar_safe_width(safe_width):
            return
        log_debug(
            "tier_board",
            "scrollbar_safe_area_changed: "
            f"enabled={scrollbar_needed} right_margin={safe_width}",
        )

    def _update_drag_auto_scroll(self, global_position: QPoint) -> None:
        viewport = self.tier_scroll_area.viewport()
        local_position = viewport.mapFromGlobal(global_position)
        edge_size = min(self.DRAG_SCROLL_EDGE_SIZE, viewport.height() // 3)

        direction = 0
        if 0 <= local_position.y() < edge_size:
            direction = -1
        elif (
            viewport.height() - edge_size
            < local_position.y()
            <= viewport.height()
        ):
            direction = 1

        self._drag_scroll_direction = direction
        if direction == 0:
            self._drag_scroll_timer.stop()
        elif not self._drag_scroll_timer.isActive():
            self._drag_scroll_timer.start()

    def _perform_drag_auto_scroll(self) -> None:
        if self._drag_scroll_direction == 0:
            self._drag_scroll_timer.stop()
            return

        scrollbar = self.tier_scroll_area.verticalScrollBar()
        previous_value = scrollbar.value()
        scrollbar.setValue(
            previous_value + self._drag_scroll_direction * self.DRAG_SCROLL_STEP
        )
        if scrollbar.value() == previous_value:
            self._stop_drag_auto_scroll()

    def _stop_drag_auto_scroll(self) -> None:
        self._drag_scroll_direction = 0
        self._drag_scroll_timer.stop()
