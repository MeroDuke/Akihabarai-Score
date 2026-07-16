from math import ceil

from PyQt6.QtCore import QTimer, Qt, pyqtSignal
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
from app.core.models import TierCardData
from app.scoring import tier_from_score
from app.widgets.tier_entry_widget import TierEntryWidget


class TierBoardWidget(QFrame):
    entries_changed = pyqtSignal()
    drag_position_changed = pyqtSignal(object)
    drag_scrolling_stopped = pyqtSignal()

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
        self.score_display_enabled = True
        self.drag_enabled = False
        self._drag_hover_tier = None
        self._drag_insertion_entry = None
        self._rendered_cards_per_row = {}
        self._reflow_timer = QTimer(self)
        self._reflow_timer.setSingleShot(True)
        self._reflow_timer.timeout.connect(self._reflow_rows_for_current_width)

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setAcceptDrops(True)
        self.setSizePolicy(
            # The board lives in a widget-resizable scroll area. Ignoring the
            # grid's horizontal size hint lets the viewport shrink the board
            # again after leaving the wider Freehand layout, so cards can
            # reflow instead of being clipped off-screen.
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Expanding,
        )

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        for tier in self.TIERS:
            row = self._build_tier_row(tier)
            self.root_layout.addWidget(row, 1)

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
        content.setObjectName("tierDropTarget")
        content.setProperty("dragHover", False)
        content.setStyleSheet(
            """
            QWidget#tierDropTarget {
                border: 1px solid #333;
                background-color: transparent;
            }
            QWidget#tierDropTarget[dragHover="true"] {
                border: 2px dashed #555555;
                background-color: rgba(120, 170, 220, 35);
            }
            """
        )
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
            card_data=TierCardData.create(
                title=title or "(nincs cím)",
                current_tier=tier,
                card_type=TierCardData.TYPE_SCORED,
                score=score,
                score_tier=tier,
            ),
        )
        entry.setFixedWidth(self.CARD_WIDTH)
        entry.set_flip_enabled(self.flip_enabled)
        entry.set_score_display_enabled(self.score_display_enabled)
        entry.set_drag_enabled(False)
        if keep_preview_flipped:
            entry.set_flipped(True)

        self.current_entry = entry
        if not self.preview_visible:
            self.current_entry.hide()

        if old_tier in self.rows and old_tier != tier:
            self._refresh_tier_row(old_tier)
        self._refresh_tier_row(tier)

    def update_manual_preview(
        self,
        title: str,
        tier: str = "C",
        cover_pixmap: QPixmap | None = None,
    ) -> None:
        cleaned_title = title.strip()
        old_tier = self.current_tier

        if self.current_entry is not None:
            old_parent = self.current_entry.parentWidget()
            if old_parent is not None and old_parent.layout() is not None:
                old_parent.layout().removeWidget(self.current_entry)
            self.current_entry.deleteLater()
            self.current_entry = None
            self.current_tier = None

        if not cleaned_title or tier not in self.rows:
            if old_tier in self.rows:
                self._refresh_tier_row(old_tier)
            log_debug(
                "tier_board",
                "manual_preview_cleared: "
                f"reason='{'empty_title' if not cleaned_title else 'invalid_tier'}'",
            )
            return

        entry = TierEntryWidget(
            cleaned_title,
            None,
            is_preview=True,
            cover_pixmap=cover_pixmap,
            is_manual=True,
            card_data=TierCardData.create(
                title=cleaned_title,
                current_tier=tier,
                card_type=TierCardData.TYPE_MANUAL,
            ),
        )
        entry.setFixedWidth(self.CARD_WIDTH)
        entry.set_flip_enabled(self.flip_enabled)
        entry.set_score_display_enabled(self.score_display_enabled)

        self.current_entry = entry
        self.current_tier = tier
        if not self.preview_visible:
            self.current_entry.hide()

        if old_tier in self.rows and old_tier != tier:
            self._refresh_tier_row(old_tier)
        self._refresh_tier_row(tier)
        log_debug(
            "tier_board",
            f"manual_preview_updated: title='{cleaned_title}' tier={tier} "
            f"has_cover={entry.has_cover}",
        )

    def add_saved_entry(
        self,
        title: str,
        score: float | None,
        tier: str,
        cover_pixmap: QPixmap | None = None,
        show_cover_placeholder: bool = False,
        is_manual: bool = False,
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
            is_manual=is_manual,
            card_data=TierCardData.create(
                title=title,
                current_tier=tier,
                card_type=(
                    TierCardData.TYPE_MANUAL
                    if is_manual
                    else TierCardData.TYPE_SCORED
                ),
                score=score,
                score_tier=None if is_manual else tier,
            ),
        )
        entry.setFixedWidth(self.CARD_WIDTH)
        entry.set_flip_enabled(self.flip_enabled)
        entry.set_score_display_enabled(self.score_display_enabled)
        entry.set_drag_enabled(self.drag_enabled)
        entry.remove_requested.connect(lambda widget: self._remove_saved_entry(widget))

        self.saved_entries_by_tier[tier].append(entry)
        self.saved_titles.add(normalized_title)
        self.saved_title_by_entry[entry] = normalized_title

        self._refresh_tier_row(tier)
        self.entries_changed.emit()
        score_text = "none" if score is None else f"{score:.1f}"
        log_info(
            "tier_board",
            f"entry_added: title='{title}' score={score_text} "
            f"tier={tier} manual={is_manual}",
        )
        return True

    def add_manual_entry(
        self,
        title: str,
        tier: str,
        cover_pixmap: QPixmap | None = None,
    ) -> bool:
        return self.add_saved_entry(
            title=title,
            score=None,
            tier=tier,
            cover_pixmap=cover_pixmap,
            is_manual=True,
        )

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
        self.schedule_reflow()

    def schedule_reflow(self) -> None:
        """Reflow cards after Qt has applied the pending parent layout resize."""
        self._reflow_timer.start(0)

    def _reflow_rows_for_current_width(self) -> None:
        for tier in self.TIERS:
            cards_per_row = self._cards_per_row(tier)
            if self._rendered_cards_per_row.get(tier) != cards_per_row:
                self._refresh_tier_row(tier)

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
        self._rendered_cards_per_row[tier] = cards_per_row
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
        root_margins = self.root_layout.contentsMargins()
        available_width = max(
            self.width()
            - self.TIER_LABEL_WIDTH
            - root_margins.left()
            - root_margins.right(),
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

    def set_drag_enabled(self, enabled: bool) -> None:
        self.drag_enabled = enabled
        self.setAcceptDrops(enabled)
        if not enabled:
            self._set_drag_hover_tier(None)
            self._set_drag_insertion_target(None, None, None)
            self.drag_scrolling_stopped.emit()
        for entries in self.saved_entries_by_tier.values():
            for entry in entries:
                entry.set_drag_enabled(enabled)

        if self.current_entry is not None:
            self.current_entry.set_drag_enabled(False)

    def dragEnterEvent(self, event) -> None:
        if self._is_supported_card_drag(event.mimeData()):
            event.acceptProposedAction()
            return
        event.ignore()

    def dragMoveEvent(self, event) -> None:
        if not self._is_supported_card_drag(event.mimeData()):
            self._set_drag_hover_tier(None)
            event.ignore()
            return

        target_tier = self._tier_at_position(event.position().toPoint())
        card_id = self._card_id_from_mime(event.mimeData())
        target_index = self._insertion_index_at_position(
            target_tier,
            event.position().toPoint(),
            card_id,
        )
        self.drag_position_changed.emit(
            self.mapToGlobal(event.position().toPoint())
        )
        self._set_drag_hover_tier(target_tier)
        self._set_drag_insertion_target(target_tier, target_index, card_id)
        if target_tier is None:
            event.ignore()
            return
        event.acceptProposedAction()

    def dragLeaveEvent(self, event) -> None:
        self._set_drag_hover_tier(None)
        self._set_drag_insertion_target(None, None, None)
        self.drag_scrolling_stopped.emit()
        super().dragLeaveEvent(event)

    def dropEvent(self, event) -> None:
        target_tier = self._tier_at_position(event.position().toPoint())
        card_id = self._card_id_from_mime(event.mimeData())
        target_index = self._insertion_index_at_position(
            target_tier,
            event.position().toPoint(),
            card_id,
        )
        self._set_drag_hover_tier(None)
        self._set_drag_insertion_target(None, None, None)
        self.drag_scrolling_stopped.emit()

        if target_tier and self.move_saved_entry_to_tier(
            card_id, target_tier, target_index
        ):
            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
            return
        log_debug(
            "tier_board",
            f"card_drop_rejected: card_id='{card_id}' "
            f"target='{target_tier or 'none'}'",
        )
        event.ignore()

    def move_saved_entry_to_tier(
        self,
        card_id: str,
        target_tier: str,
        target_index: int | None = None,
    ) -> bool:
        if not self.drag_enabled or target_tier not in self.TIERS:
            return False

        for source_tier, entries in self.saved_entries_by_tier.items():
            for entry in entries:
                if entry.card_data.card_id != card_id:
                    continue
                old_index = entries.index(entry)
                target_entries = self.saved_entries_by_tier[target_tier]
                if source_tier == target_tier and target_index is None:
                    log_debug(
                        "tier_board",
                        f"card_drop_unchanged: title='{entry.raw_title}' tier='{source_tier}'",
                    )
                    return False
                insertion_index = (
                    len(target_entries)
                    if target_index is None
                    else max(0, min(target_index, len(target_entries)))
                )
                if source_tier == target_tier and insertion_index == old_index:
                    log_debug(
                        "tier_board",
                        f"card_drop_unchanged: title='{entry.raw_title}' tier='{source_tier}'",
                    )
                    return False

                entries.remove(entry)
                insertion_index = min(insertion_index, len(target_entries))
                target_entries.insert(insertion_index, entry)
                entry.card_data.current_tier = target_tier
                self._refresh_tier_row(source_tier)
                self._refresh_tier_row(target_tier)
                entry.show_drop_success_feedback()
                self.entries_changed.emit()
                action = "card_reordered" if source_tier == target_tier else "card_moved"
                log_info(
                    "tier_board",
                    f"{action}: title='{entry.raw_title}' "
                    f"from='{source_tier}' to='{target_tier}' "
                    f"index={insertion_index}",
                )
                return True
        return False

    def restore_scored_order(self, tier_thresholds: dict) -> dict[str, int]:
        """Restore scored cards from their score; keep manual cards in place.

        Scored cards are sorted descending within their calculated tier. Manual
        cards have no score-derived destination, so they remain in their
        current tier and follow its scored cards.
        """
        scored_entries = []
        manual_entries_by_tier = {tier: [] for tier in self.TIERS}
        moved_count = 0

        for current_tier, entries in self.saved_entries_by_tier.items():
            for entry in entries:
                if entry.card_data.score is None:
                    manual_entries_by_tier[current_tier].append(entry)
                    continue

                restored_tier = tier_from_score(
                    round(entry.card_data.score, 3),
                    tier_thresholds,
                )
                if restored_tier != current_tier:
                    moved_count += 1
                entry.card_data.current_tier = restored_tier
                entry.card_data.score_tier = restored_tier
                scored_entries.append(entry)

        scored_entries.sort(
            key=lambda entry: entry.card_data.score,
            reverse=True,
        )
        restored_by_tier = {tier: [] for tier in self.TIERS}
        for entry in scored_entries:
            restored_by_tier[entry.card_data.current_tier].append(entry)
        for tier in self.TIERS:
            restored_by_tier[tier].extend(manual_entries_by_tier[tier])

        self.saved_entries_by_tier = restored_by_tier
        self._refresh_all_rows()
        if scored_entries:
            self.entries_changed.emit()
        summary = {
            "scored_count": len(scored_entries),
            "manual_count": sum(map(len, manual_entries_by_tier.values())),
            "moved_count": moved_count,
        }
        log_info(
            "tier_board",
            "scored_order_restored: "
            f"scored_count={summary['scored_count']} "
            f"manual_count={summary['manual_count']} "
            f"moved_count={summary['moved_count']}",
        )
        return summary

    def _is_supported_card_drag(self, mime_data) -> bool:
        return self.drag_enabled and mime_data.hasFormat(
            "application/x-akihabarai-tier-card"
        )

    @staticmethod
    def _card_id_from_mime(mime_data) -> str:
        return bytes(
            mime_data.data("application/x-akihabarai-tier-card")
        ).decode("utf-8", errors="ignore")

    def _insertion_index_at_position(
        self,
        tier: str | None,
        board_position,
        dragged_card_id: str,
    ) -> int | None:
        if tier not in self.content_widgets:
            return None
        entries = [
            entry
            for entry in self.saved_entries_by_tier[tier]
            if entry.card_data.card_id != dragged_card_id
        ]
        if not entries:
            return 0

        content = self.content_widgets[tier]
        position = content.mapFrom(self, board_position)
        cards_per_row = self._cards_per_row(tier)
        slot_width = self.CARD_WIDTH + self.CARD_SPACING
        row_height = self._row_base_height_for_entries(entries)
        x = max(0, position.x() - self.ROW_MARGIN + slot_width // 2)
        y = max(0, position.y() - self.ROW_MARGIN + row_height // 2)
        column = min(x // slot_width, cards_per_row - 1)
        row = y // row_height
        return min(row * cards_per_row + column, len(entries))

    def _set_drag_insertion_target(
        self,
        tier: str | None,
        target_index: int | None,
        dragged_card_id: str | None,
    ) -> None:
        new_entry = None
        if tier in self.saved_entries_by_tier and target_index is not None:
            candidates = [
                entry
                for entry in self.saved_entries_by_tier[tier]
                if entry.card_data.card_id != dragged_card_id
            ]
            if candidates:
                new_entry = candidates[min(target_index, len(candidates) - 1)]
        if new_entry is self._drag_insertion_entry:
            return
        if self._drag_insertion_entry is not None:
            self._drag_insertion_entry.set_insertion_target(False)
        self._drag_insertion_entry = new_entry
        if new_entry is not None:
            new_entry.set_insertion_target(True)

    def _tier_at_position(self, position) -> str | None:
        for tier, row_frame in self.row_frames.items():
            if row_frame.geometry().contains(position):
                return tier
        return None

    def _set_drag_hover_tier(self, tier: str | None) -> None:
        if tier == self._drag_hover_tier:
            return
        old_tier = self._drag_hover_tier
        self._drag_hover_tier = tier
        for changed_tier in (old_tier, tier):
            if changed_tier not in self.content_widgets:
                continue
            content = self.content_widgets[changed_tier]
            content.setProperty("dragHover", changed_tier == tier)
            content.style().unpolish(content)
            content.style().polish(content)
            content.update()

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

    def has_visible_preview(self) -> bool:
        return (
            self.current_entry is not None
            and self.preview_visible
            and not self.current_entry.isHidden()
        )

    def set_score_display_enabled(self, enabled: bool) -> None:
        self.score_display_enabled = enabled

        for entries in self.saved_entries_by_tier.values():
            for entry in entries:
                entry.set_score_display_enabled(enabled)

        if self.current_entry is not None:
            self.current_entry.set_score_display_enabled(enabled)

    def set_scrollbar_safe_width(self, width: int) -> bool:
        safe_width = max(0, width)
        margins = self.root_layout.contentsMargins()
        if margins.right() == safe_width:
            return False

        self.root_layout.setContentsMargins(0, 0, safe_width, 0)
        self._refresh_all_rows()
        self.updateGeometry()
        return True

    def prepare_export_mode(self, enabled: bool):
        log_debug("tier_board", f"export_mode_changed: enabled={enabled}")

        for entries in self.saved_entries_by_tier.values():
            for entry in entries:
                entry.set_export_mode(enabled)

        if self.current_entry is not None:
            self.current_entry.setVisible(not enabled and self.preview_visible)

        self.updateGeometry()
