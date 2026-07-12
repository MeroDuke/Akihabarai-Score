from app.logger import log_info


def flip_all_tier_cards_if_available(
    tier_board,
    update_tier_buttons_state,
) -> bool:
    if not tier_board.has_flippable_entries():
        log_info("tier_board", "flip_all_cards_skipped: flippable_count=0")
        update_tier_buttons_state()
        return False

    tier_board.toggle_all_saved_cards()
    return True
