import app.services.tier_add_workflow_service as workflow_service
from app.services.tier_add_service import TierAddOutcome, TierAddStatus


def test_add_current_result_to_tier_board_uses_existing_latest_result(monkeypatch):
    latest_result = {"display_score": 8.5, "tier": "A"}
    tier_board = object()
    cover_pixmap = object()
    add_calls = []
    outcome_calls = []
    recompute_calls = []

    monkeypatch.setattr(
        workflow_service,
        "add_result_to_tier_board",
        lambda **kwargs: add_calls.append(kwargs)
        or TierAddOutcome(status=TierAddStatus.ADDED, title="Cowboy Bebop"),
    )
    monkeypatch.setattr(
        workflow_service,
        "handle_tier_add_outcome",
        lambda parent, outcome: outcome_calls.append((parent, outcome)),
    )

    workflow_service.add_current_result_to_tier_board(
        parent="parent",
        tier_board=tier_board,
        title="Cowboy Bebop",
        latest_result=latest_result,
        recompute=lambda: recompute_calls.append(True),
        get_latest_result=lambda: None,
        cover_pixmap=cover_pixmap,
    )

    assert recompute_calls == []
    assert add_calls == [
        {
            "tier_board": tier_board,
            "title": "Cowboy Bebop",
            "result": latest_result,
            "cover_pixmap": cover_pixmap,
        },
    ]
    assert outcome_calls == [
        (
            "parent",
            TierAddOutcome(status=TierAddStatus.ADDED, title="Cowboy Bebop"),
        ),
    ]


def test_add_current_result_to_tier_board_recomputes_missing_latest_result(
    monkeypatch,
):
    recomputed_result = {"display_score": 7.0, "tier": "B"}
    tier_board = object()
    add_calls = []
    outcome_calls = []
    recompute_calls = []

    monkeypatch.setattr(
        workflow_service,
        "add_result_to_tier_board",
        lambda **kwargs: add_calls.append(kwargs)
        or TierAddOutcome(status=TierAddStatus.ADDED, title="Trigun"),
    )
    monkeypatch.setattr(
        workflow_service,
        "handle_tier_add_outcome",
        lambda parent, outcome: outcome_calls.append((parent, outcome)),
    )

    workflow_service.add_current_result_to_tier_board(
        parent="parent",
        tier_board=tier_board,
        title="Trigun",
        latest_result=None,
        recompute=lambda: recompute_calls.append(True),
        get_latest_result=lambda: recomputed_result,
    )

    assert recompute_calls == [True]
    assert add_calls == [
        {
            "tier_board": tier_board,
            "title": "Trigun",
            "result": recomputed_result,
            "cover_pixmap": None,
        },
    ]
    assert outcome_calls == [
        (
            "parent",
            TierAddOutcome(status=TierAddStatus.ADDED, title="Trigun"),
        ),
    ]


def test_add_current_result_to_tier_board_handles_still_missing_result(
    monkeypatch,
):
    add_calls = []
    outcome_calls = []

    monkeypatch.setattr(
        workflow_service,
        "add_result_to_tier_board",
        lambda **kwargs: add_calls.append(kwargs)
        or TierAddOutcome(status=TierAddStatus.MISSING_RESULT),
    )
    monkeypatch.setattr(
        workflow_service,
        "handle_tier_add_outcome",
        lambda parent, outcome: outcome_calls.append((parent, outcome)),
    )

    workflow_service.add_current_result_to_tier_board(
        parent="parent",
        tier_board="board",
        title="",
        latest_result=None,
        recompute=lambda: None,
        get_latest_result=lambda: None,
    )

    assert add_calls == [
        {
            "tier_board": "board",
            "title": "",
            "result": None,
            "cover_pixmap": None,
        },
    ]
    assert outcome_calls == [
        ("parent", TierAddOutcome(status=TierAddStatus.MISSING_RESULT)),
    ]
