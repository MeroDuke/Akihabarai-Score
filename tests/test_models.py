# tests/test_models.py
from app.core.models import DimState


def test_dim_state_uses_default_value():
    state = DimState("Történet")

    assert state.name == "Történet"
    assert state.value == 5.0


def test_dim_state_accepts_explicit_value():
    state = DimState("Karakterek", 8.5)

    assert state.name == "Karakterek"
    assert state.value == 8.5


def test_dim_state_instances_are_independent():
    state1 = DimState("Történet")
    state2 = DimState("Karakterek")

    state1.value = 9.0

    assert state1.value == 9.0
    assert state2.value == 5.0