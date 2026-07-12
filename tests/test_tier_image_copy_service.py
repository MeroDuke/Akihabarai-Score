import app.services.tier_image_copy_service as copy_service
from app.services.tier_image_export_service import (
    TierImageExportOutcome,
    TierImageExportStatus,
)


class FakeTierBoard:
    def __init__(self, saved_entry_count):
        self._saved_entry_count = saved_entry_count

    def saved_entry_count(self):
        return self._saved_entry_count


def test_copy_tier_image_with_feedback_skips_empty_board(monkeypatch):
    board = FakeTierBoard(saved_entry_count=0)
    copy_btn = object()
    parent = object()
    update_calls = []
    log_messages = []
    copy_calls = []
    outcome_calls = []
    monkeypatch.setattr(
        copy_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )
    monkeypatch.setattr(
        copy_service,
        "copy_tier_board_image_to_clipboard",
        lambda tier_board: copy_calls.append(tier_board),
    )
    monkeypatch.setattr(
        copy_service,
        "handle_tier_image_export_outcome",
        lambda **kwargs: outcome_calls.append(kwargs),
    )

    copy_service.copy_tier_image_with_feedback(
        parent=parent,
        tier_board=board,
        copy_tier_btn=copy_btn,
        update_tier_buttons_state=lambda: update_calls.append(True),
    )

    assert update_calls == [True]
    assert copy_calls == []
    assert outcome_calls == []
    assert log_messages == [("tier_board", "export_skipped: count=0")]


def test_copy_tier_image_with_feedback_copies_board_and_handles_outcome(
    monkeypatch,
):
    board = FakeTierBoard(saved_entry_count=1)
    copy_btn = object()
    parent = object()
    outcome = TierImageExportOutcome(status=TierImageExportStatus.COPIED)
    update_tier_buttons_state = object()
    copy_calls = []
    outcome_calls = []
    log_messages = []
    monkeypatch.setattr(
        copy_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )
    monkeypatch.setattr(
        copy_service,
        "copy_tier_board_image_to_clipboard",
        lambda tier_board: copy_calls.append(tier_board) or outcome,
    )
    monkeypatch.setattr(
        copy_service,
        "handle_tier_image_export_outcome",
        lambda **kwargs: outcome_calls.append(kwargs),
    )

    copy_service.copy_tier_image_with_feedback(
        parent=parent,
        tier_board=board,
        copy_tier_btn=copy_btn,
        update_tier_buttons_state=update_tier_buttons_state,
    )

    assert copy_calls == [board]
    assert outcome_calls == [
        {
            "parent": parent,
            "copy_tier_btn": copy_btn,
            "update_tier_buttons_state": update_tier_buttons_state,
            "outcome": outcome,
        },
    ]
    assert log_messages == [
        ("tier_board", "export_started: copy_tier_board_as_image"),
    ]
