from PyQt6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QWidget,
)


class TopInputsPanelWidget(QWidget):
    def __init__(
        self,
        title_placeholder: str,
        title_max_length: int,
        mix_mode_names: list[str],
        show_title_mode_button: bool,
    ):
        super().__init__()

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(8)
        layout.setColumnMinimumWidth(0, 140)
        layout.setColumnStretch(1, 1)
        layout.setColumnMinimumWidth(2, 80)

        self.title_label = QLabel("Anime / szezon cím:")
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText(title_placeholder)
        self.title_edit.setMaxLength(title_max_length)

        self.title_mode_btn = QPushButton()
        self.title_mode_btn.setMinimumWidth(80)
        self.title_mode_btn.setMaximumWidth(80)
        self.title_mode_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.title_mode_btn.setVisible(show_title_mode_button)

        layout.addWidget(self.title_label, 0, 0)
        layout.addWidget(self.title_edit, 0, 1, 1, 2)
        layout.addWidget(self.title_mode_btn, 0, 3, 2, 1)

        self.mix_label = QLabel("Profil-mix mód:")
        self.mix_combo = QComboBox()
        self.mix_combo.addItems(mix_mode_names)

        layout.addWidget(self.mix_label, 1, 0)
        layout.addWidget(self.mix_combo, 1, 1, 1, 2)
