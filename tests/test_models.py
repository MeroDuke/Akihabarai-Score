# tests/test_models.py
from dataclasses import asdict

from app.core.models import DimState, TierCardData


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


def test_tier_card_data_keeps_serializable_metadata_without_cover_data():
    card = TierCardData.create(
        title="Frieren",
        current_tier="C",
        card_type=TierCardData.TYPE_MANUAL,
        anilist_id=52991,
    )

    payload = asdict(card)

    assert card.card_id
    assert payload == {
        "card_id": card.card_id,
        "title": "Frieren",
        "current_tier": "C",
        "card_type": "manual",
        "score": None,
        "score_tier": None,
        "anilist_id": 52991,
        "input_snapshot": None,
    }
    assert "cover" not in " ".join(payload).casefold()
