import re
from typing import List

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette
from PyQt6.QtWidgets import (
    QGroupBox,
    QHeaderView,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.formatters import format_score


RESULT_PANEL_TITLE = "Eredm\u00e9ny"
INITIAL_SCORE_TEXT = "\u2014 / 10"
INITIAL_TIER_TEXT = "\u2014"
COPY_RESULT_IMAGE_TEXT = "Eredm\u00e9ny k\u00e9pk\u00e9nt m\u00e1sol\u00e1sa"
TABLE_HEADERS = [
    "Dimenzi\u00f3",
    "Pont",
    "Relevancia",
    "Hozz\u00e1j\u00e1rul\u00e1s",
]
COPY_DETAILS_TEXT = "R\u00e9szletes adatok m\u00e1sol\u00e1sa v\u00e1g\u00f3lapra"


class ResultPanelWidget(QGroupBox):
    copy_result_image_requested = pyqtSignal()
    copy_details_requested = pyqtSignal()

    def __init__(self):
        super().__init__(RESULT_PANEL_TITLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self._build_result_card(layout)
        self._build_result_copy_button(layout)
        self._build_results_table(layout)
        self._build_details_copy_button(layout)

    def _build_result_card(self, parent_layout: QVBoxLayout):
        self.score_label = QLabel(INITIAL_SCORE_TEXT)
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_font = QFont()
        score_font.setPointSize(28)
        score_font.setBold(True)
        self.score_label.setFont(score_font)

        self.tier_label = QLabel(INITIAL_TIER_TEXT)
        self.tier_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tier_font = QFont()
        tier_font.setPointSize(28)
        tier_font.setBold(True)
        self.tier_label.setFont(tier_font)

        self.summary_label = QLabel("")
        self.summary_label.setWordWrap(True)
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.summary_label.setTextFormat(Qt.TextFormat.RichText)
        summary_font = QFont()
        summary_font.setPointSize(10)
        summary_font.setBold(True)
        self.summary_label.setFont(summary_font)
        self.apply_summary_theme_style()

        self.result_card = QWidget()
        card_layout = QVBoxLayout(self.result_card)
        self.result_card.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(10)
        card_layout.setContentsMargins(0, 0, 0, 0)

        card_layout.addWidget(self.score_label)
        card_layout.addWidget(self.tier_label)
        card_layout.addWidget(self.summary_label)

        parent_layout.addWidget(self.result_card, alignment=Qt.AlignmentFlag.AlignCenter)

    def _build_result_copy_button(self, parent_layout: QVBoxLayout):
        self.copy_img_btn = QPushButton(COPY_RESULT_IMAGE_TEXT)
        self.copy_img_btn.setFixedHeight(32)
        self.copy_img_btn.clicked.connect(self.copy_result_image_requested)

        style = self.style()
        self.copy_img_btn.setIcon(
            style.standardIcon(style.StandardPixmap.SP_FileDialogListView)
        )
        self.copy_img_btn.setIconSize(QSize(16, 16))

        parent_layout.addWidget(self.copy_img_btn)

    def _build_results_table(self, parent_layout: QVBoxLayout):
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(TABLE_HEADERS)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        for column in (1, 2, 3):
            self.table.horizontalHeader().setSectionResizeMode(
                column, QHeaderView.ResizeMode.ResizeToContents
            )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        parent_layout.addWidget(self.table, 1)

    def _build_details_copy_button(self, parent_layout: QVBoxLayout):
        self.copy_btn = QPushButton(COPY_DETAILS_TEXT)
        self.copy_btn.clicked.connect(self.copy_details_requested)
        self.copy_btn.setFixedHeight(32)

        style = self.style()
        self.copy_btn.setIcon(style.standardIcon(style.StandardPixmap.SP_FileIcon))
        self.copy_btn.setIconSize(QSize(16, 16))

        parent_layout.addWidget(self.copy_btn)

    def update_result(self, result: dict, states):
        self.score_label.setText(f"{format_score(result['display_score'])} / 10")
        self.tier_label.setText(f"Tier: {result['tier']}")
        self.summary_label.setText(self.sanitize_summary_html(result["summary_html"]))
        self.apply_summary_theme_style()

        self.summary_label.setMinimumHeight(self.summary_label.sizeHint().height())
        self.summary_label.updateGeometry()
        self._sync_result_card_height()
        self.update_table(states, result["relevances"], result["contributions"])

    def update_table(self, states, rel: List[float], contrib: List[float]):
        self.table.setRowCount(len(states))
        for row, state in enumerate(states):
            name = state.name
            val = state.value
            weight = rel[row]
            contribution = contrib[row]

            items = [
                QTableWidgetItem(name),
                QTableWidgetItem(format_score(val)),
                QTableWidgetItem(f"{weight:.2f}"),
                QTableWidgetItem(f"{contribution:.2f}"),
            ]
            items[0].setToolTip(name)

            for column, item in enumerate(items):
                if column in (1, 2, 3):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                else:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                    )
                self.table.setItem(row, column, item)

        self._sync_table_minimum_height()

    def _sync_result_card_height(self):
        self.result_card.layout().activate()
        height = self.result_card.sizeHint().height()
        self.result_card.setMinimumHeight(height)
        self.result_card.setMaximumHeight(height)
        self.result_card.updateGeometry()

    def _sync_table_minimum_height(self):
        header_height = (
            self.table.horizontalHeader().height()
            or self.table.horizontalHeader().sizeHint().height()
        )
        rows_height = sum(
            self.table.rowHeight(row)
            for row in range(self.table.rowCount())
        )
        frame_height = self.table.frameWidth() * 2
        self.table.setMinimumHeight(header_height + rows_height + frame_height + 2)
        self.table.updateGeometry()

    def apply_summary_theme_style(self):
        text_color = self.summary_label.palette().color(
            QPalette.ColorRole.WindowText
        ).name()
        self.summary_label.setStyleSheet(f"QLabel {{ color: {text_color}; }}")

    @staticmethod
    def sanitize_summary_html(html: str) -> str:
        if not html:
            return ""

        sanitized = html
        sanitized = re.sub(
            r'\sstyle\s*=\s*(["\'])(.*?)\1',
            lambda m: ResultPanelWidget.strip_color_from_style_attr(m.group(2)),
            sanitized,
            flags=re.IGNORECASE | re.DOTALL,
        )
        sanitized = re.sub(
            r'<\s*font\b([^>]*?)\scolor\s*=\s*(["\']).*?\2([^>]*)>',
            r"<font\1\3>",
            sanitized,
            flags=re.IGNORECASE | re.DOTALL,
        )
        sanitized = re.sub(
            r"<\s*font\b([^>]*?)\scolor\s*=\s*[^\s>]+([^>]*)>",
            r"<font\1\2>",
            sanitized,
            flags=re.IGNORECASE | re.DOTALL,
        )
        return sanitized

    @staticmethod
    def strip_color_from_style_attr(style_value: str) -> str:
        parts = [part.strip() for part in style_value.split(";") if part.strip()]
        filtered = [
            part for part in parts
            if not re.match(r"^(color|background-color)\s*:", part, flags=re.IGNORECASE)
        ]

        if not filtered:
            return ""

        return ' style="' + "; ".join(filtered) + '"'
