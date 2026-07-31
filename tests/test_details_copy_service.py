import app.services.details_copy_service as copy_service
import pytest


def test_copy_details_with_feedback_exports_details_and_updates_button(
    monkeypatch,
):
    profiles = object()
    profile_combos = object()
    weight_spins = object()
    mix_modes = object()
    states = object()
    tier_thresholds = object()
    copy_btn = object()
    export_calls = []
    feedback_calls = []

    monkeypatch.setattr(
        copy_service,
        "copy_details_to_clipboard",
        lambda **kwargs: export_calls.append(kwargs),
    )
    monkeypatch.setattr(
        copy_service,
        "show_localized_copy_feedback",
        lambda button, success_key, default_key: feedback_calls.append(
            (button, success_key, default_key)
        ),
    )

    copy_service.copy_details_with_feedback(
        profiles=profiles,
        profile_combos=profile_combos,
        weight_spins=weight_spins,
        mix_mode="1 profil",
        mix_modes=mix_modes,
        states=states,
        tier_thresholds=tier_thresholds,
        title="Teszt cím",
        copy_btn=copy_btn,
    )

    assert export_calls == [
        {
            "profiles": profiles,
            "profile_combos": profile_combos,
            "weight_spins": weight_spins,
            "mix_mode": "1 profil",
            "mix_modes": mix_modes,
            "states": states,
            "tier_thresholds": tier_thresholds,
            "title": "Teszt cím",
        },
    ]
    assert feedback_calls == [
        (
            copy_btn,
            "copy.details.success",
            "copy.details.action",
        ),
    ]


def test_copy_details_logs_failure_and_reraises(monkeypatch):
    events = []
    monkeypatch.setattr(
        copy_service,
        "copy_details_to_clipboard",
        lambda **kwargs: (_ for _ in ()).throw(OSError("clipboard unavailable")),
    )
    monkeypatch.setattr(
        copy_service,
        "log_info",
        lambda component, message: events.append(("info", component, message)),
    )
    monkeypatch.setattr(
        copy_service,
        "log_error",
        lambda component, message: events.append(("error", component, message)),
    )

    with pytest.raises(OSError, match="clipboard unavailable"):
        copy_service.copy_details_with_feedback(
            profiles=None,
            profile_combos=None,
            weight_spins=None,
            mix_mode="1 profil",
            mix_modes=None,
            states=None,
            tier_thresholds=None,
            title="Teszt",
            copy_btn=None,
        )

    assert events == [
        ("info", "clipboard", "copy_details_started"),
        ("error", "clipboard", "copy_details_failed: OSError"),
    ]
