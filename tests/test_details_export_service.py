from app.core.models import DimState
from app.services import details_export_service


class FakeCombo:
    def __init__(self, text):
        self._text = text

    def currentText(self):
        return self._text


class FakeSpin:
    def __init__(self, value):
        self._value = value

    def value(self):
        return self._value


def _states():
    return [
        DimState("Történet", 8.0),
        DimState("Vizuál", 6.0),
        DimState("Hang", 7.0),
        DimState("Karakterek", 8.0),
        DimState("Tempó", 6.0),
        DimState("Rendezés", 7.0),
        DimState("Animáció", 8.0),
        DimState("Hatás", 9.0),
    ]


def _profiles():
    return {
        "Story": [1.0, 0.5, 0.8, 1.0, 0.7, 0.8, 0.6, 1.0],
        "Visual": [0.5, 1.0, 0.7, 0.8, 0.8, 1.0, 1.0, 0.6],
    }


def test_copy_details_to_clipboard_builds_export_text_and_copies_it(monkeypatch):
    copied_texts = []
    monkeypatch.setattr(
        details_export_service,
        "copy_text_to_clipboard",
        lambda text: copied_texts.append(text),
    )

    text = details_export_service.copy_details_to_clipboard(
        profiles=_profiles(),
        profile_combos=[FakeCombo("Story"), FakeCombo("Visual")],
        weight_spins=[FakeSpin(70), FakeSpin(30)],
        mix_mode="2 profil",
        mix_modes={"2 profil": 2},
        states=_states(),
        tier_thresholds={
            "A": 8.0,
            "B": 6.0,
            "C": 0.0,
        },
        title="  Cowboy Bebop  ",
    )

    assert copied_texts == [text]
    assert "Cowboy Bebop" in text
    assert "Story (70%)" in text
    assert "Visual (30%)" in text
    assert "- Történet: 8" in text
    assert "- Vizuál: 6" in text


def test_copy_details_to_clipboard_uses_missing_title_fallback(monkeypatch):
    copied_texts = []
    monkeypatch.setattr(
        details_export_service,
        "copy_text_to_clipboard",
        lambda text: copied_texts.append(text),
    )

    text = details_export_service.copy_details_to_clipboard(
        profiles={"Story": [1.0] * 8},
        profile_combos=[FakeCombo("Story")],
        weight_spins=[FakeSpin(100)],
        mix_mode="1 profil",
        mix_modes={"1 profil": 1},
        states=_states(),
        tier_thresholds={"A": 8.0, "B": 0.0},
        title="   ",
    )

    assert copied_texts == [text]
    assert "(nincs cím)" in text
