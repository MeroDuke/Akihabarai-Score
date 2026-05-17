from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class TierEntryWidget(QFrame):
    def __init__(self, title: str, score: float):
        super().__init__()

        self.setObjectName("tierEntry")

        self.setStyleSheet(
            """
            QFrame#tierEntry {
                background-color: #f5f5f5;
                border: 1px solid #777;
                border-radius: 6px;
            }

            QLabel {
                color: #111111;
                border: none;
                background: transparent;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        self.title_label = QLabel(title or "(nincs cím)")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        self.title_label.setFont(title_font)

        self.score_label = QLabel(f"{score:.1f} / 10")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        score_font = QFont()
        score_font.setPointSize(10)
        self.score_label.setFont(score_font)

        layout.addWidget(self.title_label)
        layout.addWidget(self.score_label)