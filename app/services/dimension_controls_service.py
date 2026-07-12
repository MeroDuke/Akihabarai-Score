from PyQt6.QtWidgets import QDoubleSpinBox, QSlider

from app.core.models import DimState

DEFAULT_DIMENSION_SCORE = 5.0
SLIDER_SCORE_SCALE = 10


def score_to_slider_value(score: float) -> int:
    return int(round(score * SLIDER_SCORE_SCALE))


def slider_value_to_score(value: int) -> float:
    return value / SLIDER_SCORE_SCALE


def apply_slider_value(
    state: DimState,
    spin_widget: QDoubleSpinBox,
    slider_value: int,
) -> None:
    score = slider_value_to_score(slider_value)
    state.value = score
    spin_widget.setValue(score)


def apply_spin_value(
    state: DimState,
    slider_widget: QSlider,
    spin_value: float,
) -> None:
    state.value = float(spin_value)
    slider_widget.setValue(score_to_slider_value(spin_value))


def reset_dimension_controls(
    states: list[DimState],
    slider_widgets: list[QSlider],
    spin_widgets: list[QDoubleSpinBox],
    default_score: float = DEFAULT_DIMENSION_SCORE,
) -> None:
    slider_value = score_to_slider_value(default_score)
    for state, slider, spin in zip(states, slider_widgets, spin_widgets):
        state.value = default_score
        slider.setValue(slider_value)
        spin.setValue(default_score)
