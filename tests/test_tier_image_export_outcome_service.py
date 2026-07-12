import app.services.tier_image_export_outcome_service as outcome_service
from app.services.tier_image_export_service import (
    TierImageExportOutcome,
    TierImageExportStatus,
)


def test_handle_tier_image_export_outcome_updates_buttons_on_empty(monkeypatch):
    log_messages = []
    update_calls = []
    monkeypatch.setattr(
        outcome_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )

    outcome_service.handle_tier_image_export_outcome(
        parent=None,
        copy_tier_btn="button",
        update_tier_buttons_state=lambda: update_calls.append(True),
        outcome=TierImageExportOutcome(status=TierImageExportStatus.EMPTY),
    )

    assert log_messages == [("tier_board", "export_skipped: count=0")]
    assert update_calls == [True]


def test_handle_tier_image_export_outcome_shows_error_on_failure(monkeypatch):
    log_messages = []
    error_calls = []
    monkeypatch.setattr(
        outcome_service,
        "log_error",
        lambda component, message: log_messages.append((component, message)),
    )
    monkeypatch.setattr(
        outcome_service,
        "show_tier_image_copy_error",
        lambda parent: error_calls.append(parent),
    )
    error = RuntimeError("clipboard unavailable")

    outcome_service.handle_tier_image_export_outcome(
        parent="parent",
        copy_tier_btn="button",
        update_tier_buttons_state=lambda: None,
        outcome=TierImageExportOutcome(
            status=TierImageExportStatus.FAILED,
            error=error,
        ),
    )

    assert log_messages == [
        ("tier_board", "export_failed: clipboard unavailable"),
    ]
    assert error_calls == ["parent"]


def test_handle_tier_image_export_outcome_shows_feedback_on_success(monkeypatch):
    log_messages = []
    feedback_calls = []
    monkeypatch.setattr(
        outcome_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )
    monkeypatch.setattr(
        outcome_service,
        "show_temporary_copy_feedback",
        lambda button, success_text, default_text: feedback_calls.append(
            (button, success_text, default_text)
        ),
    )

    outcome_service.handle_tier_image_export_outcome(
        parent=None,
        copy_tier_btn="button",
        update_tier_buttons_state=lambda: None,
        outcome=TierImageExportOutcome(status=TierImageExportStatus.COPIED),
    )

    assert log_messages == [
        ("tier_board", "export_completed: copied_tier_board_to_clipboard"),
    ]
    assert feedback_calls == [
        (
            "button",
            outcome_service.COPY_SUCCESS_TEXT,
            outcome_service.COPY_TIER_IMAGE_DEFAULT_TEXT,
        )
    ]
