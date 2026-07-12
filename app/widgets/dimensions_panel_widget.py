from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSlider,
    QVBoxLayout,
)


class DimensionsPanelWidget(QGroupBox):
    def __init__(self, states):
        super().__init__("Dimenziók")

        self.dimension_labels: list[QLabel] = []
        self.slider_widgets: list[QSlider] = []
        self.spin_widgets: list[QDoubleSpinBox] = []

        grid = QGridLayout()
        grid.setColumnMinimumWidth(0, 130)
        grid.setColumnMinimumWidth(2, 80)
        grid.setColumnStretch(1, 1)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.header_name = QLabel("Dimenzió")
        self.header_value = QLabel("Pont (1-10)")
        self.header_name.setStyleSheet("font-weight: 600;")
        self.header_value.setStyleSheet("font-weight: 600;")

        grid.addWidget(self.header_name, 0, 0)
        grid.addWidget(QLabel(""), 0, 1)
        grid.addWidget(self.header_value, 0, 2)

        for index, state in enumerate(states):
            row = index + 1
            name = QLabel(state.name)
            name.setWordWrap(True)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(10)
            slider.setMaximum(100)
            slider.setValue(int(state.value * 10))

            spin = QDoubleSpinBox()
            spin.setMinimum(1.0)
            spin.setMaximum(10.0)
            spin.setSingleStep(0.1)
            spin.setDecimals(1)
            spin.setValue(state.value)

            self.dimension_labels.append(name)
            self.slider_widgets.append(slider)
            self.spin_widgets.append(spin)

            grid.addWidget(name, row, 0)
            grid.addWidget(slider, row, 1)
            grid.addWidget(spin, row, 2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(grid)
        layout.addStretch(1)
