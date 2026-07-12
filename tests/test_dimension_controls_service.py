from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDoubleSpinBox, QSlider

from app.core.models import DimState
from app.services.dimension_controls_service import (
    apply_slider_value,
    apply_spin_value,
    reset_dimension_controls,
    score_to_slider_value,
    slider_value_to_score,
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
    spin.setSingleStep(0.1)
    spin.setDecimals(1)
    spin.setValue(value)
    return spin


def test_score_to_slider_value_uses_tenths_scale():
    assert score_to_slider_value(6.4) == 64
    assert score_to_slider_value(6.45) == 64
    assert score_to_slider_value(6.46) == 65


def test_slider_value_to_score_uses_tenths_scale():
    assert slider_value_to_score(64) == 6.4


def test_apply_slider_value_updates_state_and_spin(qtbot):
    state = DimState("Story", 5.0)
    spin = _make_spin()
    qtbot.addWidget(spin)

    apply_slider_value(state, spin, 73)

    assert state.value == 7.3
    assert spin.value() == 7.3


def test_apply_spin_value_updates_state_and_slider(qtbot):
    state = DimState("Story", 5.0)
    slider = _make_slider()
    qtbot.addWidget(slider)

    apply_spin_value(state, slider, 8.2)

    assert state.value == 8.2
    assert slider.value() == 82


def test_reset_dimension_controls_restores_default_score(qtbot):
    states = [DimState("Story", 9.1), DimState("Characters", 3.2)]
    sliders = [_make_slider(91), _make_slider(32)]
    spins = [_make_spin(9.1), _make_spin(3.2)]
    for widget in sliders + spins:
        qtbot.addWidget(widget)

    reset_dimension_controls(states, sliders, spins)

    assert [state.value for state in states] == [5.0, 5.0]
    assert [slider.value() for slider in sliders] == [50, 50]
    assert [spin.value() for spin in spins] == [5.0, 5.0]
