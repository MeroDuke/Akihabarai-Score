from collections.abc import Callable

from app.services.dimension_controls_service import (
    apply_slider_value,
    apply_spin_value,
)


def apply_dimension_slider_change(
    *,
    is_building: bool,
    set_building: Callable[[bool], None],
    state,
    spin_widget,
    slider_value: int,
) -> bool:
    if is_building:
        return False

    set_building(True)
    try:
        apply_slider_value(state, spin_widget, slider_value)
    finally:
        set_building(False)

    return True


def apply_dimension_spin_change(
    *,
    is_building: bool,
    set_building: Callable[[bool], None],
    state,
    slider_widget,
    spin_value: float,
) -> bool:
    if is_building:
        return False

    set_building(True)
    try:
        apply_spin_value(state, slider_widget, spin_value)
    finally:
        set_building(False)

    return True
