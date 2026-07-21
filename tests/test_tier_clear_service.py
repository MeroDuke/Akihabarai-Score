import app.services.tier_clear_service as clear_service


class FakeTierBoard:
    def __init__(self, saved_entry_count):
        self._saved_entry_count = saved_entry_count
        self.clear_calls = 0
        self.editing_entry = None

    def saved_entry_count(self):
        return self._saved_entry_count

    def clear_all_saved_entries(self):
        self.clear_calls += 1
        removed_count = self._saved_entry_count
        self._saved_entry_count = 0
        return removed_count


def test_clear_all_tier_cards_if_confirmed_clears_saved_entries(monkeypatch):
    board = FakeTierBoard(saved_entry_count=2)
    confirmation_calls = []
    update_calls = []
    log_messages = []
    monkeypatch.setattr(
        clear_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )

    handled = clear_service.clear_all_tier_cards_if_confirmed(
        board,
        ask_confirmation=lambda: confirmation_calls.append(True) or True,
        update_tier_buttons_state=lambda: update_calls.append(True),
    )

    assert handled is True
    assert confirmation_calls == [True]
    assert board.clear_calls == 1
    assert board.saved_entry_count() == 0
    assert update_calls == [True]
    assert log_messages == [
        ("tier_board", "clear_all_entries_confirmation: decision='yes'"),
        ("tier_board", "clear_all_entries_completed: count=2"),
    ]


def test_clear_all_tier_cards_if_confirmed_cancels_without_clearing(monkeypatch):
    board = FakeTierBoard(saved_entry_count=1)
    update_calls = []
    log_messages = []
    monkeypatch.setattr(
        clear_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )

    handled = clear_service.clear_all_tier_cards_if_confirmed(
        board,
        ask_confirmation=lambda: False,
        update_tier_buttons_state=lambda: update_calls.append(True),
    )

    assert handled is False
    assert board.clear_calls == 0
    assert board.saved_entry_count() == 1
    assert update_calls == []
    assert log_messages == [
        ("tier_board", "clear_all_entries_confirmation: decision='no'"),
        ("tier_board", "clear_all_entries_cancelled"),
    ]


def test_confirmed_clear_finishes_active_edit_before_removing_cards(monkeypatch):
    board = FakeTierBoard(saved_entry_count=1)
    board.editing_entry = object()
    calls = []

    handled = clear_service.clear_all_tier_cards_if_confirmed(
        board,
        ask_confirmation=lambda: True,
        update_tier_buttons_state=lambda: calls.append("updated"),
        finish_editing=lambda: calls.append("edit_finished"),
    )

    assert handled is True
    assert calls == ["edit_finished", "updated"]
    assert board.clear_calls == 1


def test_cancelled_clear_keeps_active_edit_open(monkeypatch):
    board = FakeTierBoard(saved_entry_count=1)
    board.editing_entry = object()
    finish_calls = []

    handled = clear_service.clear_all_tier_cards_if_confirmed(
        board,
        ask_confirmation=lambda: False,
        update_tier_buttons_state=lambda: None,
        finish_editing=lambda: finish_calls.append(True),
    )

    assert handled is False
    assert finish_calls == []
    assert board.clear_calls == 0


def test_clear_all_tier_cards_if_confirmed_updates_buttons_when_board_is_empty(
    monkeypatch,
):
    board = FakeTierBoard(saved_entry_count=0)
    confirmation_calls = []
    update_calls = []
    log_messages = []
    monkeypatch.setattr(
        clear_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )

    handled = clear_service.clear_all_tier_cards_if_confirmed(
        board,
        ask_confirmation=lambda: confirmation_calls.append(True) or True,
        update_tier_buttons_state=lambda: update_calls.append(True),
    )

    assert handled is False
    assert confirmation_calls == []
    assert board.clear_calls == 0
    assert update_calls == [True]
    assert log_messages == [
        ("tier_board", "clear_all_entries_skipped: count=0"),
    ]
