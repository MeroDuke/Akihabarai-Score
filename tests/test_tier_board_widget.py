import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

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


def test_add_manual_entry_creates_scoreless_non_flippable_card(tier_board):
    cover = QPixmap(10, 10)
    cover.fill()

    assert tier_board.add_manual_entry("Manual anime", "C", cover) is True

    entry = tier_board.saved_entries_by_tier["C"][0]
    assert entry.is_manual is True
    assert entry.score is None
    assert entry.has_cover is True
    assert entry.is_flippable is False
    assert entry.flip_button.isHidden() is True
    assert entry.card_data.title == "Manual anime"
    assert entry.card_data.current_tier == "C"
    assert entry.card_data.card_type == "manual"
    assert entry.card_data.score_tier is None


def test_score_display_can_hide_without_erasing_scored_card_data(tier_board):
    assert tier_board.add_saved_entry("Scored anime", 7.5, "B") is True
    entry = tier_board.saved_entries_by_tier["B"][0]
    score_labels = entry.findChildren(QLabel, "detailsScoreLabel")

    tier_board.set_score_display_enabled(False)

    assert entry.card_data.score == 7.5
    assert entry.card_data.score_tier == "B"
    assert score_labels
    assert all(label.isHidden() for label in score_labels)

    tier_board.set_score_display_enabled(True)

    assert all(not label.isHidden() for label in score_labels)


def test_new_scored_card_inherits_hidden_score_display(tier_board):
    tier_board.set_score_display_enabled(False)

    assert tier_board.add_saved_entry("Scored anime", 6.5, "C") is True

    entry = tier_board.saved_entries_by_tier["C"][0]
    score_labels = entry.findChildren(QLabel, "detailsScoreLabel")
    assert score_labels
    assert all(label.isHidden() for label in score_labels)


def test_drag_is_enabled_only_for_saved_cards(tier_board):
    tier_board.update_manual_preview("Preview")
    assert tier_board.add_manual_entry("Saved", "C") is True

    tier_board.set_drag_enabled(True)

    saved_entry = tier_board.saved_entries_by_tier["C"][0]
    assert saved_entry.drag_enabled is True
    assert saved_entry.cursor().shape() == Qt.CursorShape.OpenHandCursor
    assert tier_board.current_entry.drag_enabled is False

    saved_entry._set_drag_active(True)
    assert saved_entry.drag_active is True
    assert saved_entry.objectName() == "tierEntryDragging"

    tier_board.set_drag_enabled(False)
    assert saved_entry.drag_enabled is False
    assert saved_entry.drag_active is False
    assert saved_entry.objectName() == "tierEntry"
    assert saved_entry.cursor().shape() == Qt.CursorShape.ArrowCursor


def test_new_saved_card_inherits_enabled_freehand_drag_state(tier_board):
    tier_board.set_drag_enabled(True)

    assert tier_board.add_manual_entry("New Freehand card", "C") is True

    entry = tier_board.saved_entries_by_tier["C"][0]
    assert entry.drag_enabled is True
    assert entry.cursor().shape() == Qt.CursorShape.OpenHandCursor


def test_scrollbar_safe_width_reduces_content_without_resizing_board(tier_board):
    original_width = tier_board.width()

    tier_board.set_scrollbar_safe_width(24)

    assert tier_board.root_layout.contentsMargins().right() == 24
    assert tier_board.width() == original_width

    tier_board.set_scrollbar_safe_width(0)

    assert tier_board.root_layout.contentsMargins().right() == 0


def test_cards_per_row_follows_current_board_width_not_stale_child_width(
    tier_board, monkeypatch
):
    monkeypatch.setattr(
        tier_board.content_widgets["C"],
        "width",
        lambda: 200,
    )

    tier_board.resize(420, 520)
    narrow_count = tier_board._cards_per_row("C")
    tier_board.resize(900, 520)
    wide_count = tier_board._cards_per_row("C")

    assert narrow_count == 2
    assert wide_count == 6


def test_resize_reflows_existing_cards_when_more_columns_fit(tier_board, qtbot):
    for index in range(6):
        assert tier_board.add_saved_entry(f"Anime {index}", 5.0, "C") is True

    tier_board.resize(420, 520)
    qtbot.waitUntil(
        lambda: tier_board._rendered_cards_per_row.get("C") == 2,
    )
    narrow_positions = [
        tier_board.rows["C"].getItemPosition(index)[:2]
        for index in range(tier_board.rows["C"].count())
    ]

    tier_board.resize(900, 520)
    qtbot.waitUntil(
        lambda: tier_board._rendered_cards_per_row.get("C") == 6,
    )

    wide_positions = [
        tier_board.rows["C"].getItemPosition(index)[:2]
        for index in range(tier_board.rows["C"].count())
    ]

    assert narrow_positions == [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]
    assert wide_positions == [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]


def test_scrollbar_safe_width_reduces_cards_per_row(tier_board):
    tier_board.resize(900, 520)
    full_width_count = tier_board._cards_per_row("C")

    tier_board.set_scrollbar_safe_width(140)

    assert tier_board._cards_per_row("C") < full_width_count


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


def test_update_current_entry_keeps_flipped_preview_on_score_change(tier_board):
    cover = QPixmap(10, 10)
    cover.fill()

    tier_board.update_current_entry(
        "Preview anime",
        5.5,
        "D",
        cover_pixmap=cover,
    )
    tier_board.current_entry.set_flipped(True)

    tier_board.update_current_entry(
        "Preview anime",
        5.9,
        "D",
        cover_pixmap=cover,
    )

    assert tier_board.current_entry is not None
    assert tier_board.current_entry.card_side == tier_board.current_entry.SIDE_DETAILS
    assert tier_board.current_entry.score == 5.9


def test_update_current_entry_keeps_flipped_preview_when_score_changes_tier(tier_board):
    cover = QPixmap(10, 10)
    cover.fill()

    tier_board.update_current_entry(
        "Preview anime",
        5.5,
        "D",
        cover_pixmap=cover,
    )
    tier_board.current_entry.set_flipped(True)

    tier_board.update_current_entry(
        "Preview anime",
        6.8,
        "C",
        cover_pixmap=cover,
    )

    assert tier_board.current_tier == "C"
    assert tier_board.current_entry is not None
    assert tier_board.current_entry.card_side == tier_board.current_entry.SIDE_DETAILS


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

def test_saved_entry_flip_button_toggles_card_side(tier_board, qtbot):
    cover = QPixmap(10, 10)
    cover.fill()

    assert tier_board.add_saved_entry("Flip anime", 8.0, "A", cover_pixmap=cover) is True

    entry = tier_board.saved_entries_by_tier["A"][0]

    assert entry.card_side == entry.SIDE_COVER

    qtbot.mouseClick(
        entry.flip_button,
        Qt.MouseButton.LeftButton,
    )

    assert entry.card_side == entry.SIDE_DETAILS

    qtbot.mouseClick(
        entry.flip_button,
        Qt.MouseButton.LeftButton,
    )

    assert entry.card_side == entry.SIDE_COVER


def test_saved_entry_remove_button_emits_once(tier_board, qtbot):
    assert tier_board.add_saved_entry("Remove anime", 7.5, "B") is True

    entry = tier_board.saved_entries_by_tier["B"][0]

    emissions = []

    entry.remove_requested.connect(lambda _: emissions.append(True))

    qtbot.mouseClick(
        entry.remove_button,
        Qt.MouseButton.LeftButton,
    )

    assert len(emissions) == 1

def test_saved_entry_cover_placeholder_uses_cover_side(tier_board):
    assert tier_board.add_saved_entry(
        "Fallback anime",
        7.2,
        "B",
        show_cover_placeholder=True,
    ) is True

    entry = tier_board.saved_entries_by_tier["B"][0]

    assert entry.has_cover is False
    assert entry.has_cover_placeholder is True
    assert entry.has_cover_front is True
    assert entry.is_flippable is True
    assert entry.card_side == entry.SIDE_COVER
    assert entry.cover_label.text() == "NINCS\nKÉP"


def test_preview_cover_placeholder_uses_cover_side(tier_board):
    tier_board.update_current_entry(
        "Preview fallback anime",
        6.4,
        "C",
        show_cover_placeholder=True,
    )

    entry = tier_board.current_entry

    assert entry is not None
    assert entry.is_preview is True
    assert entry.has_cover is False
    assert entry.has_cover_placeholder is True
    assert entry.has_cover_front is True
    assert entry.is_flippable is True
    assert entry.card_side == entry.SIDE_COVER
    assert entry.cover_label.text() == "NINCS\nKÉP"




def test_text_only_entry_is_not_flippable(tier_board):
    assert tier_board.add_saved_entry("Text only anime", 6.1, "C") is True

    entry = tier_board.saved_entries_by_tier["C"][0]

    assert entry.has_cover_front is False
    assert entry.is_flippable is False
    assert entry.flip_button.isHidden() is True
    assert entry.card_side == entry.SIDE_DETAILS

    entry.toggle_card_side()

    assert entry.card_side == entry.SIDE_DETAILS


def test_flippable_entry_count_tracks_only_saved_flippable_cards(tier_board):
    cover = QPixmap(10, 10)
    cover.fill()

    assert tier_board.flippable_entry_count() == 0
    assert tier_board.has_flippable_entries() is False

    assert tier_board.add_saved_entry("Text only anime", 6.1, "C") is True

    assert tier_board.flippable_entry_count() == 0
    assert tier_board.has_flippable_entries() is False

    tier_board.update_current_entry("Preview anime", 7.0, "B", cover_pixmap=cover)

    assert tier_board.current_entry.is_flippable is True
    assert tier_board.flippable_entry_count() == 0
    assert tier_board.has_flippable_entries() is False

    assert tier_board.add_saved_entry("Cover anime", 8.0, "A", cover_pixmap=cover) is True
    assert tier_board.add_saved_entry(
        "Placeholder anime",
        7.2,
        "B",
        show_cover_placeholder=True,
    ) is True

    assert tier_board.flippable_entry_count() == 2
    assert tier_board.has_flippable_entries() is True


def test_saved_entry_count_tracks_add_and_remove(tier_board, qtbot):
    assert tier_board.saved_entry_count() == 0
    assert tier_board.has_saved_entries() is False

    assert tier_board.add_saved_entry("Első anime", 8.1, "A") is True
    assert tier_board.add_saved_entry("Második anime", 6.2, "C") is True

    assert tier_board.saved_entry_count() == 2
    assert tier_board.has_saved_entries() is True

    entry = tier_board.saved_entries_by_tier["A"][0]
    entry.remove_requested.emit(entry)
    qtbot.wait(20)

    assert tier_board.saved_entry_count() == 1
    assert tier_board.has_saved_entries() is True

    entry = tier_board.saved_entries_by_tier["C"][0]
    entry.remove_requested.emit(entry)
    qtbot.wait(20)

    assert tier_board.saved_entry_count() == 0
    assert tier_board.has_saved_entries() is False


def test_entries_changed_signal_emitted_on_successful_add_and_remove(tier_board, qtbot):
    emissions = []
    tier_board.entries_changed.connect(lambda: emissions.append(True))

    assert tier_board.add_saved_entry("Signal anime", 7.4, "B") is True
    qtbot.wait(20)

    assert len(emissions) == 1

    entry = tier_board.saved_entries_by_tier["B"][0]
    entry.remove_requested.emit(entry)
    qtbot.wait(20)

    assert len(emissions) == 2


def test_toggle_all_saved_cards_flips_only_saved_cover_cards(tier_board):
    cover = QPixmap(10, 10)
    cover.fill()

    assert tier_board.add_saved_entry("Cover anime", 8.0, "A", cover_pixmap=cover) is True
    assert tier_board.add_saved_entry(
        "Placeholder anime",
        7.2,
        "B",
        show_cover_placeholder=True,
    ) is True
    assert tier_board.add_saved_entry("Text only anime", 6.1, "C") is True
    tier_board.update_current_entry(
        "Preview anime",
        5.5,
        "D",
        cover_pixmap=cover,
    )

    cover_entry = tier_board.saved_entries_by_tier["A"][0]
    placeholder_entry = tier_board.saved_entries_by_tier["B"][0]
    text_entry = tier_board.saved_entries_by_tier["C"][0]
    preview_entry = tier_board.current_entry

    assert cover_entry.card_side == cover_entry.SIDE_COVER
    assert placeholder_entry.card_side == placeholder_entry.SIDE_COVER
    assert text_entry.card_side == text_entry.SIDE_DETAILS
    assert preview_entry.card_side == preview_entry.SIDE_COVER

    tier_board.toggle_all_saved_cards()

    assert tier_board.all_cards_flipped is True
    assert cover_entry.card_side == cover_entry.SIDE_DETAILS
    assert placeholder_entry.card_side == placeholder_entry.SIDE_DETAILS
    assert text_entry.card_side == text_entry.SIDE_DETAILS
    assert preview_entry.card_side == preview_entry.SIDE_COVER

    tier_board.toggle_all_saved_cards()

    assert tier_board.all_cards_flipped is False
    assert cover_entry.card_side == cover_entry.SIDE_COVER
    assert placeholder_entry.card_side == placeholder_entry.SIDE_COVER
    assert text_entry.card_side == text_entry.SIDE_DETAILS
    assert preview_entry.card_side == preview_entry.SIDE_COVER


def test_toggle_all_saved_cards_keeps_empty_board_unflipped(tier_board):
    assert tier_board.saved_entry_count() == 0
    assert tier_board.all_cards_flipped is False

    tier_board.toggle_all_saved_cards()

    assert tier_board.all_cards_flipped is False


def test_disabling_flip_blocks_existing_and_new_card_flip(tier_board, qtbot):
    cover = QPixmap(10, 10)
    cover.fill()
    assert tier_board.add_saved_entry(
        "Existing anime", 8.0, "A", cover_pixmap=cover
    ) is True
    existing_entry = tier_board.saved_entries_by_tier["A"][0]

    tier_board.set_flip_enabled(False)

    assert existing_entry.flip_button.isEnabled() is False
    assert existing_entry.flip_button.isHidden() is True
    existing_entry.toggle_card_side()
    tier_board.toggle_all_saved_cards()
    assert existing_entry.card_side == existing_entry.SIDE_COVER
    assert tier_board.all_cards_flipped is False

    assert tier_board.add_saved_entry(
        "New anime", 7.0, "B", cover_pixmap=cover
    ) is True
    new_entry = tier_board.saved_entries_by_tier["B"][0]
    assert new_entry.flip_button.isEnabled() is False
    assert new_entry.flip_button.isHidden() is True

    tier_board.prepare_export_mode(True)
    tier_board.prepare_export_mode(False)

    assert existing_entry.flip_button.isHidden() is True
    assert new_entry.flip_button.isHidden() is True

    tier_board.set_flip_enabled(True)

    assert existing_entry.flip_button.isEnabled() is True
    assert existing_entry.flip_button.isHidden() is False
    assert new_entry.flip_button.isEnabled() is True
    assert new_entry.flip_button.isHidden() is False


def test_show_all_front_sides_resets_saved_and_preview_cards(tier_board):
    cover = QPixmap(10, 10)
    cover.fill()
    assert tier_board.add_saved_entry(
        "Cover anime", 8.0, "A", cover_pixmap=cover
    ) is True
    assert tier_board.add_saved_entry("Text anime", 7.0, "B") is True
    tier_board.update_current_entry(
        "Preview anime", 6.0, "C", cover_pixmap=cover
    )

    cover_entry = tier_board.saved_entries_by_tier["A"][0]
    text_entry = tier_board.saved_entries_by_tier["B"][0]
    preview_entry = tier_board.current_entry
    cover_entry.set_flipped(True)
    preview_entry.set_flipped(True)
    tier_board.all_cards_flipped = True
    tier_board.set_flip_enabled(False)

    changed_count = tier_board.show_all_front_sides()

    assert changed_count == 2
    assert cover_entry.card_side == cover_entry.SIDE_COVER
    assert preview_entry.card_side == preview_entry.SIDE_COVER
    assert text_entry.card_side == text_entry.SIDE_DETAILS
    assert tier_board.all_cards_flipped is False
    assert cover_entry.flip_button.isHidden() is True


def test_show_all_front_sides_is_safe_on_empty_board(tier_board):
    assert tier_board.show_all_front_sides() == 0
    assert tier_board.all_cards_flipped is False


def test_preview_visibility_applies_to_existing_and_new_preview(tier_board):
    tier_board.update_current_entry("Existing preview", 7.0, "B")

    tier_board.set_preview_visible(False)

    assert tier_board.current_entry.isHidden() is True

    tier_board.update_current_entry("New preview", 8.0, "A")

    assert tier_board.current_entry.isHidden() is True

    tier_board.set_preview_visible(True)

    assert tier_board.current_entry.isHidden() is False


def test_manual_preview_is_scoreless_in_c_tier_and_not_saved(tier_board):
    tier_board.update_manual_preview("Frieren")

    entry = tier_board.current_entry
    assert entry is not None
    assert tier_board.current_tier == "C"
    assert entry.is_preview is True
    assert entry.is_manual is True
    assert entry.score is None
    assert entry.is_flippable is False
    assert tier_board.saved_entry_count() == 0
    assert tier_board.saved_titles == set()
    assert entry.findChildren(QLabel, "detailsScoreLabel") == []


def test_manual_preview_uses_runtime_cover_and_clears_for_empty_title(tier_board):
    cover = QPixmap(10, 10)
    cover.fill()

    tier_board.update_manual_preview("Frieren", cover_pixmap=cover)

    assert tier_board.current_entry.has_cover is True
    assert tier_board.current_entry.card_data.score is None

    tier_board.update_manual_preview("   ")

    assert tier_board.current_entry is None
    assert tier_board.current_tier is None


def test_export_restores_preview_visibility_for_current_app_mode(tier_board):
    tier_board.update_current_entry("Preview anime", 7.0, "B")

    tier_board.prepare_export_mode(True)
    assert tier_board.current_entry.isHidden() is True
    tier_board.prepare_export_mode(False)
    assert tier_board.current_entry.isHidden() is False

    tier_board.set_preview_visible(False)
    tier_board.prepare_export_mode(True)
    tier_board.prepare_export_mode(False)

    assert tier_board.current_entry.isHidden() is True


def test_visible_preview_is_not_shown_before_it_has_a_parent(
    tier_board, monkeypatch
):
    visibility_calls = []
    original_set_visible = tier_board_module.TierEntryWidget.setVisible

    def record_set_visible(entry, visible):
        visibility_calls.append((visible, entry.parentWidget()))
        original_set_visible(entry, visible)

    monkeypatch.setattr(
        tier_board_module.TierEntryWidget,
        "setVisible",
        record_set_visible,
    )

    tier_board.update_current_entry("Preview anime", 7.0, "B")

    assert not any(
        visible and parent is None
        for visible, parent in visibility_calls
    )
    assert tier_board.current_entry.parentWidget() is not None




def test_toggle_all_saved_cards_keeps_text_only_board_unflipped(tier_board):
    assert tier_board.add_saved_entry("Text only anime", 6.1, "C") is True

    text_entry = tier_board.saved_entries_by_tier["C"][0]

    assert tier_board.saved_entry_count() == 1
    assert tier_board.flippable_entry_count() == 0
    assert tier_board.all_cards_flipped is False

    tier_board.toggle_all_saved_cards()

    assert tier_board.all_cards_flipped is False
    assert text_entry.card_side == text_entry.SIDE_DETAILS


def test_removing_last_saved_entry_resets_global_flip_state(tier_board, qtbot):
    cover = QPixmap(10, 10)
    cover.fill()

    assert tier_board.add_saved_entry("Last anime", 8.5, "S", cover_pixmap=cover) is True
    tier_board.toggle_all_saved_cards()
    assert tier_board.all_cards_flipped is True

    entry = tier_board.saved_entries_by_tier["S"][0]
    entry.remove_requested.emit(entry)
    qtbot.wait(20)

    assert tier_board.saved_entry_count() == 0
    assert tier_board.all_cards_flipped is False


def test_clear_all_saved_entries_removes_saved_cards_and_keeps_preview(tier_board, qtbot):
    assert tier_board.add_saved_entry("Első anime", 8.0, "A") is True
    assert tier_board.add_saved_entry("Második anime", 7.0, "B") is True
    tier_board.update_current_entry("Preview anime", 6.0, "C")
    preview = tier_board.current_entry

    removed_count = tier_board.clear_all_saved_entries()
    qtbot.wait(20)

    assert removed_count == 2
    assert tier_board.saved_entry_count() == 0
    assert tier_board.saved_titles == set()
    assert tier_board.saved_title_by_entry == {}
    assert tier_board.current_entry is preview
    assert tier_board.current_tier == "C"
    assert tier_board.current_entry.is_preview is True


def test_clear_all_saved_entries_resets_global_flip_state(tier_board):
    cover = QPixmap(10, 10)
    cover.fill()

    assert tier_board.add_saved_entry("Flip anime", 8.5, "S", cover_pixmap=cover) is True
    tier_board.toggle_all_saved_cards()
    assert tier_board.all_cards_flipped is True

    removed_count = tier_board.clear_all_saved_entries()

    assert removed_count == 1
    assert tier_board.saved_entry_count() == 0
    assert tier_board.all_cards_flipped is False


def test_clear_all_saved_entries_returns_zero_on_empty_board(tier_board):
    removed_count = tier_board.clear_all_saved_entries()

    assert removed_count == 0
    assert tier_board.saved_entry_count() == 0
    assert tier_board.all_cards_flipped is False
