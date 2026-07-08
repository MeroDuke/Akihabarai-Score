import app.services.tier_add_outcome_service as outcome_service
from app.services.tier_add_service import TierAddOutcome, TierAddStatus


def test_handle_tier_add_outcome_logs_missing_result(monkeypatch):
    log_messages = []
    monkeypatch.setattr(
        outcome_service,
        "log_warning",
        lambda component, message: log_messages.append((component, message)),
    )

    outcome_service.handle_tier_add_outcome(
        None,
        TierAddOutcome(status=TierAddStatus.MISSING_RESULT),
    )

    assert log_messages == [
        ("tier_board", "add_entry_aborted: missing latest_result"),
    ]


def test_handle_tier_add_outcome_shows_missing_title_warning(monkeypatch):
    log_messages = []
    missing_title_calls = []
    monkeypatch.setattr(
        outcome_service,
        "log_warning",
        lambda component, message: log_messages.append((component, message)),
    )
    monkeypatch.setattr(
        outcome_service,
        "show_missing_tier_title_warning",
        lambda parent: missing_title_calls.append(parent),
    )

    outcome_service.handle_tier_add_outcome(
        "parent",
        TierAddOutcome(status=TierAddStatus.EMPTY_TITLE),
    )

    assert log_messages == [("tier_board", "add_entry_rejected: empty_title")]
    assert missing_title_calls == ["parent"]


def test_handle_tier_add_outcome_shows_duplicate_title_information(monkeypatch):
    log_messages = []
    duplicate_title_calls = []
    monkeypatch.setattr(
        outcome_service,
        "log_warning",
        lambda component, message: log_messages.append((component, message)),
    )
    monkeypatch.setattr(
        outcome_service,
        "show_duplicate_tier_title_information",
        lambda parent: duplicate_title_calls.append(parent),
    )

    outcome_service.handle_tier_add_outcome(
        "parent",
        TierAddOutcome(status=TierAddStatus.REJECTED, title="Cowboy Bebop"),
    )

    assert log_messages == [
        (
            "tier_board",
            "add_entry_rejected: duplicate_or_invalid title='Cowboy Bebop'",
        )
    ]
    assert duplicate_title_calls == ["parent"]


def test_handle_tier_add_outcome_does_nothing_for_added(monkeypatch):
    log_messages = []
    monkeypatch.setattr(
        outcome_service,
        "log_warning",
        lambda component, message: log_messages.append((component, message)),
    )

    outcome_service.handle_tier_add_outcome(
        None,
        TierAddOutcome(status=TierAddStatus.ADDED, title="Cowboy Bebop"),
    )

    assert log_messages == []
