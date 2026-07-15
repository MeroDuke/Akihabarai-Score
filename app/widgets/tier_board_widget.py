from math import ceil

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QSizePolicy,
)

from app.logger import log_debug, log_info, log_warning
from app.widgets.tier_entry_widget import TierEntryWidget


class TierBoardWidget(QFrame):
    entries_changed = pyqtSignal()

    TIERS = ["S", "A", "B", "C", "D", "E", "F"]

    COLORS = {
        "S": "#f26d6d",
        "A": "#f2b56d",
        "B": "#f2d96d",
        "C": "#dff26d",
        "D": "#a8f26d",
        "E": "#6df26d",
        "F": "#4cd964",
    }

    CARD_WIDTH = 125
    CARD_SPACING = 6
    ROW_BASE_HEIGHT = 72
    COVER_ROW_BASE_HEIGHT = 166
    ROW_MARGIN = 6
    TIER_LABEL_WIDTH = 48

    def __init__(self):
        super().__init__()

        self.current_entry = None
        self.current_tier = None
        self.preview_visible = True

        self.rows = {}
        self.row_frames = {}
        self.content_widgets = {}
        self.saved_entries_by_tier = {tier: [] for tier in self.TIERS}
        self.saved_titles = set()
        self.saved_title_by_entry = {}
        self.all_cards_flipped = False
        self.flip_enabled = True

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        for tier in self.TIERS:
            row = self._build_tier_row(tier)
            root_layout.addWidget(row, 1)

    def _build_tier_row(self, tier: str):
        row_frame = QFrame()
        row_frame.setMinimumHeight(self.ROW_BASE_HEIGHT)
        row_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.MinimumExpanding,
        )

        row_layout = QHBoxLayout(row_frame)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)

        label = QLabel(tier)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedWidth(self.TIER_LABEL_WIDTH)
        label.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )
        label.setStyleSheet(
            f"""
            background-color: {self.COLORS[tier]};
            font-weight: bold;
            font-size: 18px;
            border: 1px solid #333;
            """
        )

        content = QWidget()
        content.setStyleSheet("border: 1px solid #333;")
        content.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        content_layout = QGridLayout(content)
        content_layout.setContentsMargins(
            self.ROW_MARGIN,
            self.ROW_MARGIN,
            self.ROW_MARGIN,
            self.ROW_MARGIN,
        )
        content_layout.setHorizontalSpacing(self.CARD_SPACING)
        content_layout.setVerticalSpacing(self.CARD_SPACING)
        content_layout.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self.rows[tier] = content_layout
        self.row_frames[tier] = row_frame
        self.content_widgets[tier] = content

        row_layout.addWidget(label)
        row_layout.addWidget(content, 1)

        return row_frame

    def update_current_entry(
        self,
        title: str,
        score: float,
        tier: str,
        cover_pixmap: QPixmap | None = None,
        show_cover_placeholder: bool = False,
    ):
        old_tier = self.current_tier
        keep_preview_flipped = (
            self.current_entry is not None
            and self.current_entry.is_flippable
            and self.current_entry.card_side == self.current_entry.SIDE_DETAILS
        )

        if self.current_entry is not None:
            old_parent = self.current_entry.parentWidget()
            if old_parent is not None and old_parent.layout() is not None:
                old_parent.layout().removeWidget(self.current_entry)
            self.current_entry.deleteLater()
            self.current_entry = None

        self.current_tier = tier
        log_debug("tier_board", f"preview_updated: title='{title}' score={score:.1f} tier={tier}")

        if tier not in self.rows:
            if old_tier in self.rows:
                self._refresh_tier_row(old_tier)
            return

        entry = TierEntryWidget(
            title,
            score,
            is_preview=True,
            cover_pixmap=cover_pixmap,
            show_cover_placeholder=show_cover_placeholder,
        )
        entry.setFixedWidth(self.CARD_WIDTH)
        entry.set_flip_enabled(self.flip_enabled)
        if keep_preview_flipped:
            entry.set_flipped(True)

        self.current_entry = entry
        if not self.preview_visible:
            self.current_entry.hide()

        if old_tier in self.rows and old_tier != tier:
            self._refresh_tier_row(old_tier)
        self._refresh_tier_row(tier)

    def add_saved_entry(
        self,
        title: str,
        score: float,
        tier: str,
        cover_pixmap: QPixmap | None = None,
        show_cover_placeholder: bool = False,
    ) -> bool:
        title = title.strip()
        if not title or title == "(nincs cím)":
            log_warning("tier_board", "entry_add_rejected: empty_title")
            return False

        if tier not in self.rows:
            log_warning("tier_board", f"entry_add_rejected: invalid_tier title='{title}' tier='{tier}'")
            return False

        normalized_title = title.casefold()
        if normalized_title in self.saved_titles:
            log_warning("tier_board", f"entry_add_rejected: duplicate_title title='{title}'")
            return False

        entry = TierEntryWidget(
            title,
            score,
            is_preview=False,
            cover_pixmap=cover_pixmap,
            show_cover_placeholder=show_cover_placeholder,
        )
        entry.setFixedWidth(self.CARD_WIDTH)
        entry.set_flip_enabled(self.flip_enabled)
        entry.remove_requested.connect(lambda widget: self._remove_saved_entry(widget))

        self.saved_entries_by_tier[tier].append(entry)
        self.saved_titles.add(normalized_title)
        self.saved_title_by_entry[entry] = normalized_title

        self._refresh_tier_row(tier)
        self.entries_changed.emit()
        log_info("tier_board", f"entry_added: title='{title}' score={score:.1f} tier={tier}")
        return True

    def _remove_saved_entry(self, entry: TierEntryWidget):
        log_debug(
            "tier_board",
            "card_remove_handler_started: "
            f"title='{getattr(entry, 'raw_title', '')}'",
        )
        target_tier = None

        for tier, entries in self.saved_entries_by_tier.items():
            if entry in entries:
                entries.remove(entry)
                target_tier = tier
                break

        normalized_title = self.saved_title_by_entry.pop(entry, None)
        if normalized_title is not None:
            self.saved_titles.discard(normalized_title)

        old_parent = entry.parentWidget()
        if old_parent is not None and old_parent.layout() is not None:
            old_parent.layout().removeWidget(entry)

        entry.setParent(None)
        entry.deleteLater()

        if target_tier is not None:
            self._refresh_tier_row(target_tier)
            if self.saved_entry_count() == 0:
                self.all_cards_flipped = False
            self.entries_changed.emit()
            log_debug(
                "tier_board",
                "card_remove_completed: "
                f"title='{getattr(entry, 'raw_title', '')}' tier={target_tier}",
            )
            log_info("tier_board", f"entry_removed: tier={target_tier}")
        else:
            log_warning("tier_board", "entry_remove_requested_but_not_found")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Do not rebuild all rows during resize events. The tier rows contain
        # interactive card widgets, and repeatedly removing/re-parenting them
        # during Qt resize/layout cycles can interfere with button click events
        # on flip/delete controls. Rows are refreshed explicitly when entries
        # are added, removed, or the preview entry changes.

    def _refresh_all_rows(self):
        for tier in self.TIERS:
            self._refresh_tier_row(tier)

    def _refresh_tier_row(self, tier: str):
        layout = self.rows[tier]

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        entries = list(self.saved_entries_by_tier[tier])
        if self.current_entry is not None and self.current_tier == tier:
            entries.append(self.current_entry)

        cards_per_row = self._cards_per_row(tier)
        row_count = max(1, ceil(len(entries) / cards_per_row)) if entries else 1
        row_base_height = self._row_base_height_for_entries(entries)

        self.row_frames[tier].setMinimumHeight(row_base_height * row_count)

        for index, entry in enumerate(entries):
            grid_row = index // cards_per_row
            grid_col = index % cards_per_row
            layout.addWidget(entry, grid_row, grid_col)

        layout.setColumnStretch(cards_per_row, 1)

        self.row_frames[tier].updateGeometry()
        self.content_widgets[tier].updateGeometry()

    def _row_base_height_for_entries(self, entries) -> int:
        if any(getattr(entry, "has_cover_front", False) for entry in entries):
            return self.COVER_ROW_BASE_HEIGHT

        return self.ROW_BASE_HEIGHT

    def _cards_per_row(self, tier: str) -> int:
        content = self.content_widgets[tier]
        available_width = content.width()

        if available_width <= 0:
            available_width = max(
                self.width() - self.TIER_LABEL_WIDTH - (self.ROW_MARGIN * 2),
                self.CARD_WIDTH,
            )

        usable_width = max(0, available_width - (self.ROW_MARGIN * 2))
        card_slot_width = self.CARD_WIDTH + self.CARD_SPACING

        return max(1, (usable_width + self.CARD_SPACING) // card_slot_width)

    def saved_entry_count(self) -> int:
        return sum(len(entries) for entries in self.saved_entries_by_tier.values())

    def clear_all_saved_entries(self) -> int:
        removed_count = self.saved_entry_count()
        if removed_count <= 0:
            self.all_cards_flipped = False
            log_info("tier_board", "all_entries_remove_skipped: count=0")
            return 0

        for entries in self.saved_entries_by_tier.values():
            for entry in list(entries):
                old_parent = entry.parentWidget()
                if old_parent is not None and old_parent.layout() is not None:
                    old_parent.layout().removeWidget(entry)
                entry.setParent(None)
                entry.deleteLater()
            entries.clear()

        self.saved_titles.clear()
        self.saved_title_by_entry.clear()
        self.all_cards_flipped = False
        self._refresh_all_rows()
        self.entries_changed.emit()
        log_info("tier_board", f"all_entries_removed: count={removed_count}")
        return removed_count

    def has_saved_entries(self) -> bool:
        return self.saved_entry_count() > 0

    def flippable_entry_count(self) -> int:
        return sum(
            1
            for entries in self.saved_entries_by_tier.values()
            for entry in entries
            if entry.is_flippable
        )

    def has_flippable_entries(self) -> bool:
        return self.flippable_entry_count() > 0

    def toggle_all_saved_cards(self):
        if not self.flip_enabled:
            log_info("tier_board", "all_cards_flip_skipped: flip_disabled=True")
            return

        self.set_all_saved_cards_flipped(not self.all_cards_flipped)

    def set_all_saved_cards_flipped(self, flipped: bool):
        if flipped and not self.flip_enabled:
            log_info("tier_board", "all_cards_flip_skipped: flip_disabled=True")
            return

        flippable_count = self.flippable_entry_count()
        if flippable_count <= 0:
            self.all_cards_flipped = False
            log_info("tier_board", "all_cards_flip_skipped: flippable_count=0")
            return

        self.all_cards_flipped = flipped
        log_info(
            "tier_board",
            f"all_cards_flip_requested: flipped={flipped} flippable_count={flippable_count}",
        )

        for entries in self.saved_entries_by_tier.values():
            for entry in entries:
                if entry.is_flippable:
                    entry.set_flipped(flipped)

    def set_flip_enabled(self, enabled: bool) -> None:
        self.flip_enabled = enabled

        for entries in self.saved_entries_by_tier.values():
            for entry in entries:
                entry.set_flip_enabled(enabled)

        if self.current_entry is not None:
            self.current_entry.set_flip_enabled(enabled)

    def show_all_front_sides(self) -> int:
        changed_count = 0

        for entries in self.saved_entries_by_tier.values():
            for entry in entries:
                if (
                    entry.is_flippable
                    and entry.card_side == entry.SIDE_DETAILS
                ):
                    entry.set_flipped(False)
                    changed_count += 1

        if (
            self.current_entry is not None
            and self.current_entry.is_flippable
            and self.current_entry.card_side == self.current_entry.SIDE_DETAILS
        ):
            self.current_entry.set_flipped(False)
            changed_count += 1

        self.all_cards_flipped = False
        log_info(
            "tier_board",
            f"all_cards_front_side_applied: changed_count={changed_count}",
        )
        return changed_count

    def set_preview_visible(self, visible: bool) -> None:
        self.preview_visible = visible
        if self.current_entry is not None:
            self.current_entry.setVisible(visible)

    def prepare_export_mode(self, enabled: bool):
        log_debug("tier_board", f"export_mode_changed: enabled={enabled}")

        for entries in self.saved_entries_by_tier.values():
            for entry in entries:
                entry.set_export_mode(enabled)

        if self.current_entry is not None:
            self.current_entry.setVisible(not enabled and self.preview_visible)

        self.updateGeometry()
