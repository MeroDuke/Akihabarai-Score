from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
)

from app.widgets.tier_board_widget import TierBoardWidget


class TierPanelWidget(QGroupBox):
    def __init__(self):
        super().__init__("Tier lista")
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

        self.flip_all_tier_cards_btn.setEnabled(has_flippable_entries)
        self.clear_all_tier_cards_btn.setEnabled(has_saved_entries)
        self.copy_tier_btn.setEnabled(has_saved_entries)
