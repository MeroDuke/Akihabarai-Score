from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QSizePolicy, QVBoxLayout


class TierEntryWidget(QFrame):
    remove_requested = pyqtSignal(object)

    TITLE_MAX_WIDTH = 110

    def __init__(self, title: str, score: float, is_preview: bool = False):
        super().__init__()

        self.is_preview = is_preview
        self.setObjectName("tierEntryPreview" if is_preview else "tierEntry")
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(52)

        self.setStyleSheet(
            """
            QFrame#tierEntry {
                background-color: #f5f5f5;
                border: 1px solid #777;
                border-radius: 6px;
            }

            QFrame#tierEntryPreview {
                background-color: #ffffff;
                border: 2px dashed #777;
                border-radius: 6px;
            }

            QLabel {
                color: #111111;
                border: none;
                background: transparent;
            }

            QPushButton#removeButton {
                background-color: #ffffff;
                color: #222222;
                border: 1px solid #777777;
                border-radius: 8px;
                font-weight: bold;
                padding: 0px;
            }

            QPushButton#removeButton:hover {
                background-color: #ffdddd;
                border: 1px solid #aa3333;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(2)

        raw_title = title or "(nincs cím)"

        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(9)

        self.title_label = QLabel(self._elide_title(raw_title, title_font))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(False)
        self.title_label.setToolTip(raw_title)
        self.title_label.setFont(title_font)

        self.score_label = QLabel(f"{score:.1f} / 10")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        score_font = QFont()
        score_font.setPointSize(8)
        self.score_label.setFont(score_font)

        layout.addWidget(self.title_label)
        layout.addWidget(self.score_label)

        self.remove_button = QPushButton("×", self)
        self.remove_button.setObjectName("removeButton")
        self.remove_button.setFixedSize(18, 18)
        self.remove_button.setToolTip("Eltávolítás a Tier listából")
        self.remove_button.clicked.connect(lambda: self.remove_requested.emit(self))
        self.remove_button.setVisible(not is_preview)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if self.remove_button is not None:
            self.remove_button.move(self.width() - self.remove_button.width() + 6, -6)

    def set_export_mode(self, enabled: bool):
        if self.remove_button is not None:
            self.remove_button.setVisible(not enabled and not self.is_preview)

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
