from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget


class ActionButtonsPanelWidget(QWidget):
    def __init__(self, version_button_text: str):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.version_btn = QPushButton(version_button_text)
        self.version_btn.setFixedHeight(30)
        layout.addWidget(self.version_btn)

        self.reset_btn = QPushButton("Alaphelyzet (5,0)")
        self.reset_btn.setFixedHeight(30)
        layout.addWidget(self.reset_btn)

        self.add_tier_btn = QPushButton("Hozzáadás Tier listához")
        self.add_tier_btn.setFixedHeight(30)
        layout.addWidget(self.add_tier_btn)
