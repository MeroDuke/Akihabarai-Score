from PyQt6.QtGui import QPixmap

from app.widgets.tier_panel_widget import TierPanelWidget


def test_tier_panel_uses_hungarian_labels(qtbot):
    panel = TierPanelWidget()
    qtbot.addWidget(panel)

    assert panel.title() == "Tier lista"
    assert panel.flip_all_tier_cards_btn.text() == "Összes kártya megfordítása"
    assert panel.clear_all_tier_cards_btn.text() == "Minden kártya törlése"
    assert panel.copy_tier_btn.text() == "Tier lista képként másolása"


def test_tier_panel_buttons_follow_board_state(qtbot):
    panel = TierPanelWidget()
    qtbot.addWidget(panel)

    panel.update_buttons_state()

    assert panel.flip_all_tier_cards_btn.isEnabled() is False
    assert panel.clear_all_tier_cards_btn.isEnabled() is False
    assert panel.copy_tier_btn.isEnabled() is False

    assert panel.tier_board.add_saved_entry("Szöveges anime", 8.0, "A") is True
    panel.update_buttons_state()

    assert panel.flip_all_tier_cards_btn.isEnabled() is False
    assert panel.clear_all_tier_cards_btn.isEnabled() is True
    assert panel.copy_tier_btn.isEnabled() is True

    cover = QPixmap(10, 10)
    cover.fill()
    assert panel.tier_board.add_saved_entry(
        "Borítós anime",
        8.5,
        "S",
        cover_pixmap=cover,
    ) is True
    panel.update_buttons_state()

    assert panel.flip_all_tier_cards_btn.isEnabled() is True
    assert panel.clear_all_tier_cards_btn.isEnabled() is True
    assert panel.copy_tier_btn.isEnabled() is True


def test_tier_panel_buttons_are_in_same_bottom_row(qtbot):
    panel = TierPanelWidget()
    qtbot.addWidget(panel)

    tier_layout = panel.layout()
    bottom_item = tier_layout.itemAt(tier_layout.count() - 1)
    button_row = bottom_item.layout()

    assert button_row is not None
    assert button_row.itemAt(0).widget() is panel.flip_all_tier_cards_btn
    assert button_row.itemAt(1).widget() is panel.clear_all_tier_cards_btn
    assert button_row.itemAt(2).widget() is panel.copy_tier_btn


def test_freehand_flip_state_only_disables_flip_action(qtbot):
    panel = TierPanelWidget()
    qtbot.addWidget(panel)
    cover = QPixmap(10, 10)
    cover.fill()
    assert panel.tier_board.add_saved_entry(
        "Flip anime", 8.0, "A", cover_pixmap=cover
    ) is True

    panel.set_flip_enabled(False)

    assert panel.flip_all_tier_cards_btn.isEnabled() is False
    assert panel.clear_all_tier_cards_btn.isEnabled() is True
    assert panel.copy_tier_btn.isEnabled() is True

    panel.update_buttons_state()

    assert panel.flip_all_tier_cards_btn.isEnabled() is False


def test_vertical_scrollbar_reserves_and_releases_card_safe_area(qtbot):
    panel = TierPanelWidget()
    qtbot.addWidget(panel)

    panel._sync_vertical_scrollbar_safe_area(0, 100)

    reserved_width = panel.tier_board.root_layout.contentsMargins().right()
    assert reserved_width > 0
    assert panel.tier_scroll_area.viewportMargins().right() == 0

    panel._sync_vertical_scrollbar_safe_area(0, 0)

    assert panel.tier_board.root_layout.contentsMargins().right() == 0
