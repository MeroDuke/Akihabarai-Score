from app.widgets.title_input_mode_presenter import (
    TITLE_INPUT_MODE_OFFLINE,
    TITLE_INPUT_MODE_ONLINE,
    TITLE_MODE_BUTTON_OFFLINE_TEXT,
    TITLE_MODE_BUTTON_ONLINE_TEXT,
    build_title_input_mode_presentation,
)


def test_online_title_input_mode_presentation_uses_online_text_and_placeholder():
    presentation = build_title_input_mode_presentation(
        TITLE_INPUT_MODE_ONLINE,
        offline_placeholder="pl. Re:Zero S3",
        online_placeholder="AniList keresés...",
    )

    assert presentation.mode == TITLE_INPUT_MODE_ONLINE
    assert presentation.placeholder == "AniList keresés..."
    assert presentation.button_text == TITLE_MODE_BUTTON_ONLINE_TEXT
    assert presentation.button_text == "🌐 Online"
    assert presentation.autocomplete_enabled is True


def test_offline_title_input_mode_presentation_uses_offline_text_and_placeholder():
    presentation = build_title_input_mode_presentation(
        TITLE_INPUT_MODE_OFFLINE,
        offline_placeholder="pl. Re:Zero S3",
        online_placeholder="AniList keresés...",
    )

    assert presentation.mode == TITLE_INPUT_MODE_OFFLINE
    assert presentation.placeholder == "pl. Re:Zero S3"
    assert presentation.button_text == TITLE_MODE_BUTTON_OFFLINE_TEXT
    assert presentation.button_text == "✏ Offline"
    assert presentation.autocomplete_enabled is False


def test_unknown_title_input_mode_falls_back_to_offline_presentation():
    presentation = build_title_input_mode_presentation(
        "unexpected",
        offline_placeholder="pl. Re:Zero S3",
        online_placeholder="AniList keresés...",
    )

    assert presentation.mode == TITLE_INPUT_MODE_OFFLINE
    assert presentation.placeholder == "pl. Re:Zero S3"
    assert presentation.autocomplete_enabled is False
