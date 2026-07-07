from app.services.update_check_service import UpdateCheckResult
from app.widgets.version_button_presenter import (
    build_update_check_version_button_presentation,
    build_version_button_text,
)


def test_build_version_button_text_uses_hungarian_label_and_v_prefix():
    assert build_version_button_text("0.18.0") == "Verzió: v0.18.0"


def test_build_version_button_text_keeps_existing_v_prefix():
    assert build_version_button_text("v0.18.0") == "Verzió: v0.18.0"


def test_update_available_presentation_uses_hungarian_label_and_warning_style():
    presentation = build_update_check_version_button_presentation(
        UpdateCheckResult(
            ok=True,
            update_available=True,
            latest_version="v0.19.0",
        ),
        default_text="Verzió: v0.18.0",
    )

    assert presentation is not None
    assert presentation.text == "Frissítés elérhető: v0.19.0"
    assert "background-color" in presentation.style_sheet
    assert "font-weight" in presentation.style_sheet


def test_no_update_presentation_keeps_default_hungarian_version_label():
    presentation = build_update_check_version_button_presentation(
        UpdateCheckResult(
            ok=True,
            update_available=False,
            latest_version="v0.18.0",
        ),
        default_text="Verzió: v0.18.0",
    )

    assert presentation is not None
    assert presentation.text == "Verzió: v0.18.0"
    assert presentation.style_sheet == ""


def test_update_check_error_does_not_request_button_change():
    presentation = build_update_check_version_button_presentation(
        UpdateCheckResult(ok=False, error="network timeout"),
        default_text="Verzió: v0.18.0",
    )

    assert presentation is None
