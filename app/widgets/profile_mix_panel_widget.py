from PyQt6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSizePolicy,
    QSpinBox,
)


class ProfileMixPanelWidget(QGroupBox):
    def __init__(self, profile_names: list[str], total_weight: int):
        super().__init__("Profil konfiguráció")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        self.profile_combos: list[QComboBox] = []
        self.weight_spins: list[QSpinBox] = []

        layout = QGridLayout(self)
        layout.setColumnMinimumWidth(0, 130)
        layout.setColumnMinimumWidth(1, 220)
        layout.setColumnMinimumWidth(3, 80)
        layout.setColumnStretch(1, 1)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(6)

        header_profile = QLabel("Profil")
        header_weight = QLabel("Súly (0-100)")
        header_profile.setStyleSheet("font-weight: 600;")
        header_weight.setStyleSheet("font-weight: 600;")

        layout.addWidget(QLabel(""), 0, 0)
        layout.addWidget(header_profile, 0, 1, 1, 2)
        layout.addWidget(header_weight, 0, 3)

        self.profile_labels: list[QLabel] = []
        for index in range(3):
            label = QLabel(f"Profil {index + 1}:")
            combo = QComboBox()
            combo.addItems(profile_names)

            weight_spin = QSpinBox()
            weight_spin.setMinimum(0)
            weight_spin.setMaximum(total_weight)
            weight_spin.setSingleStep(1)
            weight_spin.setValue(0)

            self.profile_labels.append(label)
            self.profile_combos.append(combo)
            self.weight_spins.append(weight_spin)

            row = index + 1
            layout.addWidget(label, row, 0)
            layout.addWidget(combo, row, 1, 1, 2)
            layout.addWidget(weight_spin, row, 3)

        for row in range(4):
            layout.setRowStretch(row, 0)
