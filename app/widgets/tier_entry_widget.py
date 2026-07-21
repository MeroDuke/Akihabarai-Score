from PyQt6.QtCore import QEvent, QMimeData, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QDrag, QFont, QFontMetrics, QPixmap
from app.logger import log_debug
from app.core.formatters import format_score
from app.core.models import TierCardData

from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)


class TierEntryWidget(QFrame):
    remove_requested = pyqtSignal(object)
    edit_requested = pyqtSignal(object)

    TITLE_MAX_WIDTH = 110

    TEXT_CARD_HEIGHT = 52
    COVER_CARD_WIDTH = 125
    COVER_CARD_HEIGHT = 154

    COVER_WIDTH = 104
    COVER_HEIGHT = 132

    SIDE_COVER = 0
    SIDE_DETAILS = 1

    BUTTON_SIZE = 16
    DROP_SUCCESS_FEEDBACK_MS = 400
    DROP_REJECTED_FEEDBACK_MS = 400

    def __init__(
        self,
        title: str,
        score: float | None,
        is_preview: bool = False,
        cover_pixmap: QPixmap | None = None,
        show_cover_placeholder: bool = False,
        is_manual: bool = False,
        card_data: TierCardData | None = None,
    ):
        super().__init__()

        self.is_preview = is_preview
        normalized_title = title or "(nincs cím)"
        self.card_data = card_data or TierCardData.create(
            title=normalized_title,
            current_tier="",
            card_type=(
                TierCardData.TYPE_MANUAL
                if is_manual
                else TierCardData.TYPE_SCORED
            ),
            score=score,
        )
        self.cover_pixmap = (
            cover_pixmap
            if cover_pixmap is not None and not cover_pixmap.isNull()
            else None
        )
        self.has_cover = self.cover_pixmap is not None
        self.has_cover_placeholder = bool(show_cover_placeholder and not self.has_cover)
        self.has_cover_front = self.has_cover or self.has_cover_placeholder
        self.card_side = self.SIDE_COVER if self.has_cover_front else self.SIDE_DETAILS
        self.drag_enabled = False
        self.drag_active = False
        self.drop_success_active = False
        self.drop_rejected_active = False
        self.insertion_target_active = False
        self._drop_success_pending = False
        self._drag_press_global_position = None
        self._drop_success_timer = QTimer(self)
        self._drop_success_timer.setSingleShot(True)
        self._drop_success_timer.timeout.connect(self._clear_drop_success_feedback)
        self._drop_rejected_timer = QTimer(self)
        self._drop_rejected_timer.setSingleShot(True)
        self._drop_rejected_timer.timeout.connect(self._clear_drop_rejected_feedback)

        self.setObjectName("tierEntryPreview" if is_preview else "tierEntry")
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(
            self.COVER_CARD_HEIGHT if self.has_cover_front else self.TEXT_CARD_HEIGHT
        )

        self.setStyleSheet(
            """
            QFrame#tierEntry {
                background-color: #f5f5f5;
                border: 1px solid #777777;
                border-radius: 6px;
            }

            QFrame#tierEntryPreview {
                background-color: #ffffff;
                border: 2px dashed #777777;
                border-radius: 6px;
            }

            QFrame#tierEntryDragging {
                background-color: #ffffff;
                border: 2px dashed #555555;
                border-radius: 6px;
            }

            QFrame#tierEntryDropSuccess {
                background-color: #eef9ee;
                border: 2px solid #4f9f5f;
                border-radius: 6px;
            }

            QFrame#tierEntryDropRejected {
                background-color: #fff0f0;
                border: 2px solid #b85555;
                border-radius: 6px;
            }

            QFrame[insertionTarget="true"] {
                border: 3px solid #3f7fbf;
            }

            QFrame#tierEntry[selectedForEdit="true"] {
                border: 4px solid #147dcc;
                background-color: #dceeff;
            }

            QLabel#editBadge {
                color: #ffffff;
                background-color: #147dcc;
                border: 1px solid #07558f;
                border-radius: 3px;
                font-size: 8px;
                font-weight: bold;
                padding: 1px 3px;
            }

            QWidget#cardPage {
                background: transparent;
                border: none;
            }

            QLabel {
                color: #111111;
                border: none;
                background: transparent;
            }

            QLabel#coverLabel {
                background-color: #111111;
                border: 1px solid #555555;
                border-radius: 4px;
            }

            QLabel#coverFallbackLabel {
                background-color: #f0f0f0;
                color: #444444;
                border: 1px solid #777777;
                border-radius: 4px;
                font-weight: bold;
            }

            QLabel#detailsTitleLabel {
                font-weight: bold;
            }

            QLabel#detailsScoreLabel {
                font-weight: bold;
                color: #111111;
            }

            QLabel#detailsSeparator {
                color: #bbbbbb;
            }

            QPushButton#flipButton,
            QPushButton#removeButton,
            QPushButton#previewCornerButton {
                background-color: #ffffff;
                color: #222222;
                border: 1px solid #777777;
                border-radius: 8px;
                font-weight: bold;
                padding: 0px;
            }

            QPushButton#flipButton:hover {
                background-color: #eeeeee;
                border: 1px solid #444444;
            }

            QPushButton#removeButton:hover {
                background-color: #ffdddd;
                border: 1px solid #aa3333;
            }
            """
        )

        self.details_score_labels = []
        self.details_separators = []
        self.score_display_enabled = True

        self.stack = QStackedLayout(self)
        self.stack.setContentsMargins(6, 5, 6, 5)
        self.stack.setSpacing(0)

        if self.is_manual and not self.has_cover_front:
            self.stack.addWidget(self._build_manual_title_side())
        elif self.has_cover_front:
            self.stack.addWidget(self._build_cover_side())
        else:
            # Keep indexes stable: page 0 is also a details page without cover.
            self.stack.addWidget(self._build_details_side(compact=True))

        if self.is_manual:
            self.stack.addWidget(self._build_manual_title_side())
        else:
            self.stack.addWidget(
                self._build_details_side(compact=not self.has_cover_front)
            )
        self.stack.setCurrentIndex(self.card_side)

        self.flip_button = QPushButton("↺", self)
        self.flip_button.setObjectName("flipButton")
        self.flip_button.setFixedSize(self.BUTTON_SIZE, self.BUTTON_SIZE)
        self.flip_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.flip_button.clicked.connect(self.on_flip_button_clicked)
        self.flip_button.setVisible(self.has_cover_front)
        self.flip_enabled = True
        self.export_mode = False

        self.remove_button = QPushButton("×", self)
        self.remove_button.setObjectName("removeButton")
        self.remove_button.setFixedSize(self.BUTTON_SIZE, self.BUTTON_SIZE)
        self.remove_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.remove_button.clicked.connect(self.on_remove_button_clicked)
        self.remove_button.setVisible(not is_preview)

        self.preview_corner_button = QPushButton("", self)
        self.preview_corner_button.setObjectName("previewCornerButton")
        self.preview_corner_button.setFixedSize(self.BUTTON_SIZE, self.BUTTON_SIZE)
        self.preview_corner_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.preview_corner_button.setVisible(is_preview)

        self.edit_badge = QLabel("SZERK.", self)
        self.edit_badge.setObjectName("editBadge")
        self.edit_badge.adjustSize()
        self.edit_badge.setVisible(False)
        self._install_drag_event_filters(self)
        self.setProperty("selectedForEdit", False)

    @property
    def raw_title(self) -> str:
        return self.card_data.title

    @property
    def score(self) -> float | None:
        return self.card_data.score

    @property
    def is_manual(self) -> bool:
        return self.card_data.card_type == TierCardData.TYPE_MANUAL

    def _build_cover_side(self) -> QWidget:
        page = QWidget(self)
        page.setObjectName("cardPage")
        page.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self.has_cover:
            self.cover_label = QLabel()
            self.cover_label.setObjectName("coverLabel")
            self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cover_label.setFixedSize(self.COVER_WIDTH, self.COVER_HEIGHT)
            self.cover_label.setPixmap(
                self.cover_pixmap.scaled(
                    self.COVER_WIDTH,
                    self.COVER_HEIGHT,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            self.cover_label = QLabel("NINCS\nKÉP")
            self.cover_label.setObjectName("coverFallbackLabel")
            self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cover_label.setFixedSize(self.COVER_WIDTH, self.COVER_HEIGHT)

            fallback_font = QFont()
            fallback_font.setBold(True)
            fallback_font.setPointSize(12)
            self.cover_label.setFont(fallback_font)

        layout.addWidget(self.cover_label, alignment=Qt.AlignmentFlag.AlignCenter)
        return page

    def _build_details_side(self, *, compact: bool = False) -> QWidget:
        page = QWidget(self)
        page.setObjectName("cardPage")
        page.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(9 if compact else 10)

        title_label = QLabel(self._elide_title(self.raw_title, title_font))
        title_label.setObjectName("detailsTitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(False)
        title_label.setFont(title_font)

        score_label = QLabel(f"{format_score(self.score)} / 10")
        score_label.setObjectName("detailsScoreLabel")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        score_font = QFont()
        score_font.setPointSize(8 if compact else 18)
        score_font.setBold(True)
        score_label.setFont(score_font)
        self.details_score_labels.append(score_label)

        layout.addStretch(1)
        layout.addWidget(title_label)

        if not compact:
            separator = QLabel("─" * 10)
            separator.setObjectName("detailsSeparator")
            separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.details_separators.append(separator)
            layout.addWidget(separator)

        layout.addWidget(score_label)
        layout.addStretch(1)

        return page

    def _build_manual_title_side(self) -> QWidget:
        page = QWidget(self)
        page.setObjectName("cardPage")
        page.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(9)
        title_label = QLabel(self._elide_title(self.raw_title, title_font))
        title_label.setObjectName("manualTitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(title_font)
        title_label.setToolTip(self.raw_title)
        layout.addWidget(title_label)
        return page

    def on_flip_button_clicked(self):
        log_debug(
            "tier_board",
            "card_flip_requested: "
            f"title='{self.raw_title}' side='{self._card_side_name()}' "
            f"is_preview={self.is_preview}",
        )
        self.toggle_card_side()

    def on_remove_button_clicked(self):
        log_debug(
            "tier_board",
            "card_remove_requested: "
            f"title='{self.raw_title}' is_preview={self.is_preview}",
        )
        self.remove_requested.emit(self)

    @property
    def is_flippable(self) -> bool:
        return self.has_cover_front and not self.is_manual

    def _card_side_name(self) -> str:
        return "cover" if self.card_side == self.SIDE_COVER else "details"

    def toggle_card_side(self):
        if not self.is_flippable or not self.flip_enabled:
            return

        self.set_flipped(self.card_side == self.SIDE_COVER)

    def set_flipped(self, flipped: bool):
        if not self.is_flippable:
            return

        target_side = self.SIDE_DETAILS if flipped else self.SIDE_COVER
        if self.card_side == target_side:
            return

        self.card_side = target_side
        self.stack.setCurrentIndex(self.card_side)
        log_debug(
            "tier_board",
            "card_flip_completed: "
            f"title='{self.raw_title}' side='{self._card_side_name()}' "
            f"is_preview={self.is_preview}",
        )
        self._raise_corner_buttons()

    def _raise_corner_buttons(self):
        if self.flip_button is not None:
            self.flip_button.move(-3, -3)
            self.flip_button.raise_()

        if self.remove_button is not None:
            self.remove_button.move(
                self.width() - self.remove_button.width() + 3,
                -3,
            )
            self.remove_button.raise_()

        if self.preview_corner_button is not None:
            self.preview_corner_button.move(
                self.width() - self.preview_corner_button.width() + 3,
                -3,
            )
            self.preview_corner_button.raise_()

        if self.edit_badge is not None:
            self.edit_badge.move(
                max(2, (self.width() - self.edit_badge.width()) // 2),
                2,
            )
            self.edit_badge.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._raise_corner_buttons()

    def set_export_mode(self, enabled: bool):
        self.export_mode = enabled
        if self.flip_button is not None:
            self.flip_button.setVisible(
                not enabled and self.is_flippable and self.flip_enabled
            )

        if self.remove_button is not None:
            self.remove_button.setVisible(not enabled and not self.is_preview)

        if self.preview_corner_button is not None:
            self.preview_corner_button.setVisible(not enabled and self.is_preview)

        if self.edit_badge is not None:
            self.edit_badge.setVisible(
                not enabled and bool(self.property("selectedForEdit"))
            )

        self._raise_corner_buttons()

    def _install_drag_event_filters(self, widget: QWidget) -> None:
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self)

    def eventFilter(self, watched, event):
        if self.drag_enabled and not isinstance(watched, QPushButton):
            if event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self._drag_press_global_position = event.globalPosition().toPoint()
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
            elif event.type() == QEvent.Type.MouseMove:
                if (
                    self._drag_press_global_position is not None
                    and event.buttons() & Qt.MouseButton.LeftButton
                    and (
                        event.globalPosition().toPoint()
                        - self._drag_press_global_position
                    ).manhattanLength()
                    >= QApplication.startDragDistance()
                ):
                    self._start_internal_drag()
                    return True
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self._drag_press_global_position = None
                self.setCursor(Qt.CursorShape.OpenHandCursor)

        if (
            not self.is_preview
            and not self.is_manual
            and not isinstance(watched, QPushButton)
            and event.type() == QEvent.Type.MouseButtonRelease
            and event.button() == Qt.MouseButton.LeftButton
            and not self.drag_active
        ):
            self.edit_requested.emit(self)

        return super().eventFilter(watched, event)

    def set_edit_selected(self, selected: bool) -> None:
        self.setProperty("selectedForEdit", bool(selected))
        self.edit_badge.setVisible(bool(selected) and not self.export_mode)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        self._raise_corner_buttons()

    def set_drag_enabled(self, enabled: bool) -> None:
        self.drag_enabled = bool(enabled and not self.is_preview)
        self._drag_press_global_position = None
        if not self.drag_enabled:
            self._set_drag_active(False)
            self._clear_drop_success_feedback()
            self._clear_drop_rejected_feedback()
        self.setCursor(
            Qt.CursorShape.OpenHandCursor
            if self.drag_enabled
            else Qt.CursorShape.ArrowCursor
        )

    def _set_drag_active(self, active: bool) -> None:
        if self.drag_active == active:
            return
        self.drag_active = active
        self._apply_visual_state()

    def _apply_visual_state(self) -> None:
        if self.drag_active:
            object_name = "tierEntryDragging"
        elif self.drop_success_active:
            object_name = "tierEntryDropSuccess"
        elif self.drop_rejected_active:
            object_name = "tierEntryDropRejected"
        else:
            object_name = "tierEntryPreview" if self.is_preview else "tierEntry"
        self.setObjectName(object_name)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def show_drop_success_feedback(self) -> None:
        if self.is_preview:
            return
        if self.drag_active:
            self._drop_success_pending = True
            return
        self._drop_success_pending = False
        self._clear_drop_rejected_feedback()
        self.drop_success_active = True
        self._apply_visual_state()
        self._drop_success_timer.start(self.DROP_SUCCESS_FEEDBACK_MS)

    def _clear_drop_success_feedback(self) -> None:
        self._drop_success_pending = False
        self._drop_success_timer.stop()
        if not self.drop_success_active:
            return
        self.drop_success_active = False
        self._apply_visual_state()

    def show_drop_rejected_feedback(self) -> None:
        if self.is_preview or not self.drag_enabled:
            return
        self._clear_drop_success_feedback()
        self.drop_rejected_active = True
        self._apply_visual_state()
        self._drop_rejected_timer.start(self.DROP_REJECTED_FEEDBACK_MS)

    def _clear_drop_rejected_feedback(self) -> None:
        self._drop_rejected_timer.stop()
        if not self.drop_rejected_active:
            return
        self.drop_rejected_active = False
        self._apply_visual_state()

    def set_insertion_target(self, active: bool) -> None:
        if self.insertion_target_active == active:
            return
        self.insertion_target_active = active
        self.setProperty("insertionTarget", active)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _start_internal_drag(self) -> None:
        if not self.drag_enabled or self.drag_active:
            return

        self._drag_press_global_position = None
        self._set_drag_active(True)
        log_debug(
            "tier_board",
            f"card_drag_started: title='{self.raw_title}' "
            f"tier='{self.card_data.current_tier}'",
        )

        mime_data = QMimeData()
        mime_data.setData(
            "application/x-akihabarai-tier-card",
            self.card_data.card_id.encode("utf-8"),
        )
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(self.grab())
        drop_action = drag.exec(Qt.DropAction.MoveAction)

        self._set_drag_active(False)
        if self._drop_success_pending:
            self.show_drop_success_feedback()
        elif drop_action != Qt.DropAction.MoveAction:
            self.show_drop_rejected_feedback()
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        log_debug(
            "tier_board",
            f"card_drag_finished: title='{self.raw_title}' "
            f"tier='{self.card_data.current_tier}' "
            f"moved={drop_action == Qt.DropAction.MoveAction}",
        )

    def set_flip_enabled(self, enabled: bool) -> None:
        self.flip_enabled = enabled
        self.flip_button.setEnabled(enabled)
        self.flip_button.setVisible(
            not self.export_mode and self.is_flippable and enabled
        )
        self._raise_corner_buttons()

    def set_score_display_enabled(self, enabled: bool) -> None:
        self.score_display_enabled = enabled
        if self.is_manual:
            return

        for label in self.details_score_labels:
            label.setVisible(enabled)
        for separator in self.details_separators:
            separator.setVisible(enabled)

    @classmethod
    def _elide_title(cls, title: str, font: QFont) -> str:
        """Return a compact, max-two-line title that fits inside the tier card."""
        clean_title = (title or "(nincs cím)").strip()
        metrics = QFontMetrics(font)

        if metrics.horizontalAdvance(clean_title) <= cls.TITLE_MAX_WIDTH:
            return clean_title

        words = clean_title.split()

        if len(words) <= 1:
            return metrics.elidedText(
                clean_title,
                Qt.TextElideMode.ElideRight,
                cls.TITLE_MAX_WIDTH,
            )

        lines = []
        current = ""

        for word in words:
            candidate = word if not current else f"{current} {word}"

            if metrics.horizontalAdvance(candidate) <= cls.TITLE_MAX_WIDTH:
                current = candidate
                continue

            if current:
                lines.append(current)
                current = word
            else:
                lines.append(
                    metrics.elidedText(
                        word,
                        Qt.TextElideMode.ElideRight,
                        cls.TITLE_MAX_WIDTH,
                    )
                )
                current = ""

            if len(lines) == 2:
                break

        if len(lines) < 2 and current:
            lines.append(current)

        if not lines:
            return metrics.elidedText(
                clean_title,
                Qt.TextElideMode.ElideRight,
                cls.TITLE_MAX_WIDTH,
            )

        if len(lines) == 1:
            lines[0] = metrics.elidedText(
                lines[0],
                Qt.TextElideMode.ElideRight,
                cls.TITLE_MAX_WIDTH,
            )
            return lines[0]

        second_line = lines[1]
        joined_prefix = " ".join(lines)
        if len(joined_prefix) < len(clean_title):
            second_line = metrics.elidedText(
                second_line + " …",
                Qt.TextElideMode.ElideRight,
                cls.TITLE_MAX_WIDTH,
            )

        return f"{lines[0]}\n{second_line}"
