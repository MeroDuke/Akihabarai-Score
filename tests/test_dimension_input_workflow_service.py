from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDoubleSpinBox, QSlider

from app.core.models import DimState
from app.services.dimension_input_workflow_service import (
    apply_dimension_slider_change,
    apply_dimension_spin_change,
)


def _make_slider(value: int = 50) -> QSlider:
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setMinimum(10)
    slider.setMaximum(100)
    slider.setValue(value)
    return slider


def _make_spin(value: float = 5.0) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setMinimum(1.0)
    spin.setMaximum(10.0)
    spin.setDecimals(1)
    spin.setValue(value)
    return spin


def test_apply_dimension_slider_change_updates_state_and_spin(qtbot):
    state = DimState("Story", 5.0)
    spin = _make_spin()
    qtbot.addWidget(spin)
    building_values = []

    handled = apply_dimension_slider_change(
        is_building=False,
        set_building=lambda value: building_values.append(value),
        state=state,
        spin_widget=spin,
        slider_value=73,
    )

    assert handled is True
    assert building_values == [True, False]
    assert state.value == 7.3
    assert spin.value() == 7.3


def test_apply_dimension_spin_change_updates_state_and_slider(qtbot):
    state = DimState("Story", 5.0)
    slider = _make_slider()
    qtbot.addWidget(slider)
    building_values = []

    handled = apply_dimension_spin_change(
        is_building=False,
        set_building=lambda value: building_values.append(value),
        state=state,
        slider_widget=slider,
        spin_value=8.2,
    )

    assert handled is True
    assert building_values == [True, False]
    assert state.value == 8.2
    assert slider.value() == 82


def test_dimension_changes_are_skipped_while_building(qtbot):
    state = DimState("Story", 5.0)
    spin = _make_spin()
    qtbot.addWidget(spin)
    building_values = []

    handled = apply_dimension_slider_change(
        is_building=True,
        set_building=lambda value: building_values.append(value),
        state=state,
        spin_widget=spin,
        slider_value=73,
    )

    assert handled is False
    assert building_values == []
    assert state.value == 5.0
    assert spin.value() == 5.0
