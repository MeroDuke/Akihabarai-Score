from PyQt6.QtCore import QPoint
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


def test_board_reflows_when_scroll_viewport_shrinks_after_wide_layout(qtbot):
    panel = TierPanelWidget()
    panel.resize(1000, 700)
    qtbot.addWidget(panel)
    panel.show()
    qtbot.waitExposed(panel)

    for index in range(6):
        assert panel.tier_board.add_saved_entry(
            f"Anime {index}", 5.0, "C"
        ) is True

    qtbot.waitUntil(
        lambda: panel.tier_board._rendered_cards_per_row.get("C", 0) >= 6,
    )

    panel.resize(430, 700)
    qtbot.waitUntil(
        lambda: panel.tier_board._rendered_cards_per_row.get("C") == 2,
    )

    positions = [
        panel.tier_board.rows["C"].getItemPosition(index)[:2]
        for index in range(panel.tier_board.rows["C"].count())
    ]
    assert positions == [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]


def test_drag_near_viewport_bottom_scrolls_down(qtbot):
    panel = TierPanelWidget()
    panel.resize(500, 300)
    qtbot.addWidget(panel)
    panel.show()
    qtbot.waitExposed(panel)
    scrollbar = panel.tier_scroll_area.verticalScrollBar()
    scrollbar.setRange(0, 500)
    scrollbar.setValue(100)
    viewport = panel.tier_scroll_area.viewport()

    panel._update_drag_auto_scroll(
        viewport.mapToGlobal(QPoint(20, viewport.height() - 2))
    )
    panel._perform_drag_auto_scroll()

    assert scrollbar.value() == 100 + panel.DRAG_SCROLL_STEP
    assert panel._drag_scroll_direction == 1


def test_drag_near_viewport_top_scrolls_up(qtbot):
    panel = TierPanelWidget()
    panel.resize(500, 300)
    qtbot.addWidget(panel)
    panel.show()
    qtbot.waitExposed(panel)
    scrollbar = panel.tier_scroll_area.verticalScrollBar()
    scrollbar.setRange(0, 500)
    scrollbar.setValue(100)
    viewport = panel.tier_scroll_area.viewport()

    panel._update_drag_auto_scroll(viewport.mapToGlobal(QPoint(20, 2)))
    panel._perform_drag_auto_scroll()

    assert scrollbar.value() == 100 - panel.DRAG_SCROLL_STEP
    assert panel._drag_scroll_direction == -1


def test_drag_in_viewport_middle_or_finished_stops_auto_scroll(qtbot):
    panel = TierPanelWidget()
    panel.resize(500, 300)
    qtbot.addWidget(panel)
    panel.show()
    qtbot.waitExposed(panel)
    viewport = panel.tier_scroll_area.viewport()

    panel._update_drag_auto_scroll(viewport.mapToGlobal(QPoint(20, 2)))
    assert panel._drag_scroll_timer.isActive() is True

    panel._update_drag_auto_scroll(
        viewport.mapToGlobal(QPoint(20, viewport.height() // 2))
    )
    assert panel._drag_scroll_direction == 0
    assert panel._drag_scroll_timer.isActive() is False

    panel._update_drag_auto_scroll(viewport.mapToGlobal(QPoint(20, 2)))
    panel.tier_board.drag_scrolling_stopped.emit()
    assert panel._drag_scroll_direction == 0
    assert panel._drag_scroll_timer.isActive() is False
