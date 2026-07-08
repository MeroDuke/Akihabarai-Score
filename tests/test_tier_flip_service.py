import app.services.tier_flip_service as flip_service


class FakeTierBoard:
    def __init__(self, has_flippable_entries):
        self._has_flippable_entries = has_flippable_entries
        self.toggle_calls = 0

    def has_flippable_entries(self):
        return self._has_flippable_entries

    def toggle_all_saved_cards(self):
        self.toggle_calls += 1


def test_flip_all_tier_cards_if_available_toggles_flippable_board(monkeypatch):
    board = FakeTierBoard(has_flippable_entries=True)
    update_calls = []
    log_messages = []
    monkeypatch.setattr(
        flip_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )

    handled = flip_service.flip_all_tier_cards_if_available(
        board,
        update_tier_buttons_state=lambda: update_calls.append(True),
    )

    assert handled is True
    assert board.toggle_calls == 1
    assert update_calls == []
    assert log_messages == []


def test_flip_all_tier_cards_if_available_updates_buttons_when_nothing_flippable(
    monkeypatch,
):
    board = FakeTierBoard(has_flippable_entries=False)
    update_calls = []
    log_messages = []
    monkeypatch.setattr(
        flip_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )

    handled = flip_service.flip_all_tier_cards_if_available(
        board,
        update_tier_buttons_state=lambda: update_calls.append(True),
    )

    assert handled is False
    assert board.toggle_calls == 0
    assert update_calls == [True]
    assert log_messages == [
        ("tier_board", "flip_all_cards_skipped: flippable_count=0"),
    ]
