from types import SimpleNamespace

from app.services import main_window_output_workflow_service as workflow


class FakeButton:
    def __init__(self):
        self.enabled = None

    def setEnabled(self, enabled):
        self.enabled = enabled


class FakeCombo:
    def __init__(self, text="1 profil"):
        self._text = text

    def currentText(self):
        return self._text


def _make_window():
    window = SimpleNamespace()
    window.GITHUB_RELEASES_URL = "https://example.test/releases"
    window.add_tier_btn = FakeButton()
    window.version_btn = object()
    window.tier_panel = object()
    window.tier_board = object()
    window.result_panel = object()
    window.result_card = object()
    window.copy_img_btn = object()
    window.copy_btn = object()
    window.copy_tier_btn = object()
    window.profiles = {"Balanced": [1.0]}
    window.profile_combos = []
    window.weight_spins = []
    window.mix_combo = FakeCombo()
    window.states = []
    window.tier_thresholds = {"A": 8.0}
    window.ui_cfg = {}
    window.title_edit = SimpleNamespace(text=lambda: "Cowboy Bebop")
    window.selected_cover_pixmap = None
    window.recompute = lambda: None
    window.update_tier_buttons_state = lambda: None
    window._build_version_button_text = lambda: "Verzió: v0.18.0"
    return window


def test_update_add_tier_button_state_uses_title():
    window = _make_window()

    workflow.update_add_tier_button_state_for_window(window, " Cowboy Bebop ")
    assert window.add_tier_btn.enabled is True

    workflow.update_add_tier_button_state_for_window(window, "   ")
    assert window.add_tier_btn.enabled is False


def test_open_releases_page_logs_and_delegates(monkeypatch):
    window = _make_window()
    log_messages = []
    calls = []
    open_url = object()
    monkeypatch.setattr(
        workflow,
        "open_releases_page_from_button",
        lambda **kwargs: calls.append(kwargs),
    )

    workflow.open_releases_page_for_window(
        window,
        log_info_func=lambda component, message: log_messages.append(
            (component, message)
        ),
        open_url_func=open_url,
    )

    assert log_messages == [("ui", "button_click: open_releases_page")]
    assert calls == [
        {
            "releases_url": "https://example.test/releases",
            "open_url_func": open_url,
        }
    ]


def test_check_for_updates_and_tier_buttons_delegate(monkeypatch):
    window = _make_window()
    calls = []
    check_func = object()
    monkeypatch.setattr(
        workflow,
        "check_for_updates_from_button",
        lambda **kwargs: calls.append(("updates", kwargs)),
    )
    monkeypatch.setattr(
        workflow,
        "update_tier_panel_buttons",
        lambda tier_panel: calls.append(("tier_buttons", tier_panel)),
    )

    workflow.check_for_updates_for_window(
        window,
        app_version="0.18.0",
        default_button_text="Verzió: v0.18.0",
        check_for_update_func=check_func,
    )
    workflow.update_tier_buttons_state_for_window(window)

    assert calls[0] == (
        "updates",
        {
            "version_btn": window.version_btn,
            "app_version": "0.18.0",
            "default_button_text": "Verzió: v0.18.0",
            "check_for_update_func": check_func,
        },
    )
    assert calls[1] == ("tier_buttons", window.tier_panel)


def test_tier_actions_log_and_delegate(monkeypatch):
    window = _make_window()
    log_messages = []
    calls = []
    monkeypatch.setattr(
        workflow,
        "flip_tier_cards_from_button",
        lambda **kwargs: calls.append(("flip", kwargs)),
    )
    monkeypatch.setattr(
        workflow,
        "clear_tier_cards_from_button",
        lambda **kwargs: calls.append(("clear", kwargs)),
    )
    window._ask_clear_all_tier_cards_confirmation = lambda: True

    workflow.flip_all_tier_cards_for_window(
        window,
        log_info_func=lambda component, message: log_messages.append(
            (component, message)
        ),
    )
    workflow.clear_all_tier_cards_for_window(
        window,
        log_info_func=lambda component, message: log_messages.append(
            (component, message)
        ),
    )

    assert log_messages == [
        ("ui", "button_click: flip_all_tier_cards"),
        ("ui", "button_click: clear_all_tier_cards"),
    ]
    assert calls[0][0] == "flip"
    assert calls[0][1]["tier_board"] is window.tier_board
    assert calls[1][0] == "clear"
    assert calls[1][1]["ask_confirmation"] is window._ask_clear_all_tier_cards_confirmation


def test_ask_clear_confirmation_logs_decision():
    window = _make_window()
    log_messages = []

    confirmed = workflow.ask_clear_all_tier_cards_confirmation_for_window(
        window,
        ask_confirmation_func=lambda parent: parent is window,
        log_info_func=lambda component, message: log_messages.append(
            (component, message)
        ),
    )

    assert confirmed is True
    assert log_messages == [
        ("tier_board", "clear_all_entries_confirmation: decision='yes'")
    ]


def test_recompute_updates_latest_result(monkeypatch):
    window = _make_window()
    expected = {"tier": "A"}
    calls = []
    monkeypatch.setattr(
        workflow,
        "recompute_from_window",
        lambda **kwargs: calls.append(kwargs) or expected,
    )

    workflow.recompute_for_window(
        window,
        mix_modes={"1 profil": 1},
        build_result_payload_func=lambda **kwargs: {},
    )

    assert window.latest_result is expected
    assert calls[0]["title"] == "Cowboy Bebop"
    assert calls[0]["mix_modes"] == {"1 profil": 1}
    assert calls[0]["tier_board"] is window.tier_board


def test_add_current_update_table_and_copy_actions_delegate(monkeypatch):
    window = _make_window()
    window.latest_result = {"tier": "A"}
    log_messages = []
    calls = []
    monkeypatch.setattr(
        workflow,
        "add_current_result_from_window",
        lambda **kwargs: calls.append(("add", kwargs)),
    )
    monkeypatch.setattr(
        workflow,
        "update_result_table_from_main",
        lambda **kwargs: calls.append(("table", kwargs)),
    )
    monkeypatch.setattr(
        workflow,
        "copy_details_from_button",
        lambda **kwargs: calls.append(("details", kwargs)),
    )
    monkeypatch.setattr(
        workflow,
        "copy_result_image_from_button",
        lambda **kwargs: calls.append(("result_image", kwargs)),
    )
    monkeypatch.setattr(
        workflow,
        "copy_tier_image_from_button",
        lambda **kwargs: calls.append(("tier_image", kwargs)),
    )
    log = lambda component, message: log_messages.append((component, message))

    workflow.add_current_result_to_tier_board_for_window(window, log_info_func=log)
    workflow.update_result_table_for_window(window, [0.9], [4.5])
    workflow.copy_details_to_clipboard_for_window(
        window,
        mix_modes={"1 profil": 1},
        log_info_func=log,
    )
    workflow.copy_result_image_to_clipboard_for_window(window)
    workflow.copy_tier_image_to_clipboard_for_window(window, log_info_func=log)

    assert log_messages == [
        ("ui", "button_click: add_current_to_tier_board"),
        ("ui", "button_click: copy_to_clipboard"),
        ("ui", "button_click: copy_tier_image_to_clipboard"),
    ]
    assert [name for name, _ in calls] == [
        "add",
        "table",
        "details",
        "result_image",
        "tier_image",
    ]
    assert calls[0][1]["latest_result"] == {"tier": "A"}
    assert calls[1][1]["relevances"] == [0.9]
    assert calls[2][1]["title"] == "Cowboy Bebop"


def test_result_summary_helpers_delegate_to_result_panel_widget():
    html = '<span style="color: red; font-weight: bold">Erős</span>'

    sanitized = workflow.sanitize_result_summary_html(html)
    stripped_style = workflow.strip_result_summary_style_color(
        "color: red; font-weight: bold"
    )

    assert "color" not in sanitized
    assert stripped_style == ' style="font-weight: bold"'
