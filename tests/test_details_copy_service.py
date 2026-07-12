import app.services.details_copy_service as copy_service


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
        "show_temporary_copy_feedback",
        lambda button, success_text, default_text: feedback_calls.append(
            (button, success_text, default_text)
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
            copy_service.COPY_DETAILS_SUCCESS_TEXT,
            copy_service.COPY_DETAILS_DEFAULT_TEXT,
        ),
    ]
