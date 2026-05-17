import pytest

import app.widgets.tier_board_widget as tier_board_module
from app.widgets.tier_board_widget import TierBoardWidget


@pytest.fixture
def tier_board(monkeypatch, qtbot):
    monkeypatch.setattr(tier_board_module, "log_debug", lambda *args, **kwargs: None)
    monkeypatch.setattr(tier_board_module, "log_info", lambda *args, **kwargs: None)
    monkeypatch.setattr(tier_board_module, "log_warning", lambda *args, **kwargs: None)

    board = TierBoardWidget()
    board.resize(420, 520)
    qtbot.addWidget(board)
    board.show()
    qtbot.waitExposed(board)
    return board


def test_add_saved_entry_adds_card_to_requested_tier(tier_board):
    was_added = tier_board.add_saved_entry("Teszt anime", 8.4, "A")

    assert was_added is True
    assert len(tier_board.saved_entries_by_tier["A"]) == 1
    assert "teszt anime" in tier_board.saved_titles
    assert tier_board.saved_entries_by_tier["A"][0] in tier_board.saved_title_by_entry


def test_add_saved_entry_rejects_empty_title(tier_board):
    was_added = tier_board.add_saved_entry("", 7.0, "B")

    assert was_added is False
    assert tier_board.saved_entries_by_tier["B"] == []
    assert tier_board.saved_titles == set()


def test_add_saved_entry_rejects_placeholder_title(tier_board):
    was_added = tier_board.add_saved_entry("(nincs cím)", 7.0, "B")

    assert was_added is False
    assert tier_board.saved_entries_by_tier["B"] == []
    assert tier_board.saved_titles == set()


def test_add_saved_entry_rejects_invalid_tier(tier_board):
    was_added = tier_board.add_saved_entry("Teszt anime", 7.0, "Z")

    assert was_added is False
    assert "teszt anime" not in tier_board.saved_titles


def test_add_saved_entry_rejects_duplicate_title_case_insensitive(tier_board):
    first_added = tier_board.add_saved_entry("Teszt Anime", 8.0, "A")
    second_added = tier_board.add_saved_entry("teszt anime", 7.5, "B")

    assert first_added is True
    assert second_added is False
    assert len(tier_board.saved_entries_by_tier["A"]) == 1
    assert len(tier_board.saved_entries_by_tier["B"]) == 0
    assert len(tier_board.saved_titles) == 1


def test_remove_saved_entry_removes_card_and_allows_title_to_be_added_again(tier_board, qtbot):
    assert tier_board.add_saved_entry("Törölhető anime", 6.8, "C") is True

    entry = tier_board.saved_entries_by_tier["C"][0]
    entry.remove_requested.emit(entry)
    qtbot.wait(20)

    assert tier_board.saved_entries_by_tier["C"] == []
    assert "törölhető anime" not in tier_board.saved_titles
    assert entry not in tier_board.saved_title_by_entry

    assert tier_board.add_saved_entry("Törölhető anime", 6.8, "C") is True
    assert len(tier_board.saved_entries_by_tier["C"]) == 1


def test_update_current_entry_creates_preview_without_saving_it(tier_board):
    tier_board.update_current_entry("Preview anime", 5.5, "D")

    assert tier_board.current_entry is not None
    assert tier_board.current_tier == "D"
    assert tier_board.current_entry.is_preview is True
    assert tier_board.saved_entries_by_tier["D"] == []
    assert "preview anime" not in tier_board.saved_titles


def test_update_current_entry_moves_preview_between_tiers(tier_board):
    tier_board.update_current_entry("Preview anime", 5.5, "D")
    first_preview = tier_board.current_entry

    tier_board.update_current_entry("Preview anime", 8.2, "A")

    assert tier_board.current_entry is not None
    assert tier_board.current_entry is not first_preview
    assert tier_board.current_tier == "A"
    assert tier_board.saved_entries_by_tier["D"] == []
    assert tier_board.saved_entries_by_tier["A"] == []


def test_prepare_export_mode_hides_and_restores_preview(tier_board):
    tier_board.update_current_entry("Preview anime", 7.1, "B")
    preview = tier_board.current_entry

    preview.show()
    assert preview.isHidden() is False

    tier_board.prepare_export_mode(True)
    assert preview.isHidden() is True

    tier_board.prepare_export_mode(False)
    assert preview.isHidden() is False


def test_prepare_export_mode_hides_and_restores_remove_button_on_saved_entry(tier_board):
    assert tier_board.add_saved_entry("Mentett anime", 9.1, "S") is True
    entry = tier_board.saved_entries_by_tier["S"][0]

    assert entry.remove_button.isHidden() is False

    tier_board.prepare_export_mode(True)
    assert entry.remove_button.isHidden() is True

    tier_board.prepare_export_mode(False)
    assert entry.remove_button.isHidden() is False