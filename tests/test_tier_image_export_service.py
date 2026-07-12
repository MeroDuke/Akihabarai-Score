from app.services.tier_image_export_service import (
    TierImageExportStatus,
    copy_tier_board_image_to_clipboard,
)


class FakeClipboard:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.pixmaps = []

    def setPixmap(self, pixmap):
        if self.should_fail:
            raise RuntimeError("clipboard unavailable")

        self.pixmaps.append(pixmap)


class FakeTierBoard:
    def __init__(self, saved_entry_count=1):
        self._saved_entry_count = saved_entry_count
        self.export_modes = []
        self.grab_count = 0
        self.pixmap = object()

    def saved_entry_count(self):
        return self._saved_entry_count

    def prepare_export_mode(self, enabled):
        self.export_modes.append(enabled)

    def grab(self):
        self.grab_count += 1
        return self.pixmap


def test_copy_tier_board_image_to_clipboard_skips_empty_board():
    board = FakeTierBoard(saved_entry_count=0)
    clipboard = FakeClipboard()
    process_events = []

    outcome = copy_tier_board_image_to_clipboard(
        board,
        process_events=lambda: process_events.append(True),
        clipboard_provider=lambda: clipboard,
    )

    assert outcome.status == TierImageExportStatus.EMPTY
    assert board.export_modes == []
    assert board.grab_count == 0
    assert clipboard.pixmaps == []
    assert process_events == []


def test_copy_tier_board_image_to_clipboard_copies_grabbed_pixmap():
    board = FakeTierBoard(saved_entry_count=1)
    clipboard = FakeClipboard()
    process_events = []

    outcome = copy_tier_board_image_to_clipboard(
        board,
        process_events=lambda: process_events.append(True),
        clipboard_provider=lambda: clipboard,
    )

    assert outcome.status == TierImageExportStatus.COPIED
    assert board.export_modes == [True, False]
    assert board.grab_count == 1
    assert clipboard.pixmaps == [board.pixmap]
    assert process_events == [True]


def test_copy_tier_board_image_to_clipboard_restores_export_mode_on_failure():
    board = FakeTierBoard(saved_entry_count=1)
    clipboard = FakeClipboard(should_fail=True)

    outcome = copy_tier_board_image_to_clipboard(
        board,
        process_events=lambda: None,
        clipboard_provider=lambda: clipboard,
    )

    assert outcome.status == TierImageExportStatus.FAILED
    assert isinstance(outcome.error, RuntimeError)
    assert board.export_modes == [True, False]
    assert board.grab_count == 1
