from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
)

from app.widgets.tier_entry_widget import TierEntryWidget


class TierBoardWidget(QFrame):
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
    def __init__(self):
        super().__init__()

        self.current_entry = None
        self.rows = {}

        self.setFrameShape(QFrame.Shape.StyledPanel)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        for tier in self.TIERS:
            row = self._build_tier_row(tier)
            root_layout.addWidget(row)

    def _build_tier_row(self, tier: str):
        row_frame = QFrame()
        row_frame.setMinimumHeight(90)

        row_layout = QHBoxLayout(row_frame)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)

        label = QLabel(tier)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedWidth(48)

        label.setStyleSheet(
            f"""
            background-color: {self.COLORS[tier]};
            font-weight: bold;
            font-size: 18px;
            border: 1px solid #333;
            """
        )

        content = QWidget()
        content.setStyleSheet(
            "border: 1px solid #333;"
        )

        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.rows[tier] = content_layout

        row_layout.addWidget(label)
        row_layout.addWidget(content, 1)

        return row_frame

    def update_current_entry(self, title: str, score: float, tier: str):
        if self.current_entry is not None:
            self.current_entry.setParent(None)
            self.current_entry.deleteLater()
            self.current_entry = None

        if tier not in self.rows:
            return

        entry = TierEntryWidget(title, score)
        entry.setFixedWidth(160)

        self.rows[tier].addWidget(entry)
        self.current_entry = entry