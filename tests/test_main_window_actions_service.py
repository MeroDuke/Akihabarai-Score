from types import SimpleNamespace

from app.services import main_window_actions_service as actions


class FakeButton:
    def __init__(self):
        self.enabled = None
        self.text = ""
        self.style_sheet = ""

    def setEnabled(self, enabled):
        self.enabled = enabled

    def setText(self, text):
        self.text = text

    def setStyleSheet(self, style_sheet):
        self.style_sheet = style_sheet


def test_set_add_tier_button_enabled_uses_trimmed_title():
    button = FakeButton()

    actions.set_add_tier_button_enabled(button, " Cowboy Bebop ")
    assert button.enabled is True

    actions.set_add_tier_button_enabled(button, "   ")
    assert button.enabled is False


def test_open_releases_page_from_button_delegates_url(monkeypatch):
    opened = []
    monkeypatch.setattr(
        actions,
        "open_release_page",
        lambda releases_url, open_url_func: opened.append((releases_url, open_url_func)),
    )
    open_url = object()

    actions.open_releases_page_from_button(
        releases_url="https://example.test/releases",
        open_url_func=open_url,
    )

    assert opened == [("https://example.test/releases", open_url)]


def test_check_for_updates_from_button_delegates_update_check(monkeypatch):
    calls = []
    monkeypatch.setattr(
        actions,
        "apply_update_check_to_version_button",
        lambda **kwargs: calls.append(kwargs),
    )
    button = FakeButton()
    check_func = object()

    actions.check_for_updates_from_button(
        version_btn=button,
        app_version="0.18.0",
        default_button_text="Verzió: v0.18.0",
        check_for_update_func=check_func,
    )

    assert calls == [
        {
            "version_btn": button,
            "app_version": "0.18.0",
            "default_button_text": "Verzió: v0.18.0",
            "check_for_update_func": check_func,
        }
    ]


def test_tier_actions_delegate_to_existing_services(monkeypatch):
    calls = []
    tier_board = object()
    update = lambda: None
    ask = lambda: True

    monkeypatch.setattr(
        actions,
        "flip_all_tier_cards_if_available",
        lambda *args: calls.append(("flip", args)),
    )
    monkeypatch.setattr(
        actions,
        "clear_all_tier_cards_if_confirmed",
        lambda *args, **kwargs: calls.append(("clear", args, kwargs)),
    )

    actions.flip_tier_cards_from_button(
        tier_board=tier_board,
        update_tier_buttons_state=update,
    )
    actions.clear_tier_cards_from_button(
        tier_board=tier_board,
        ask_confirmation=ask,
        update_tier_buttons_state=update,
    )

    assert calls[0] == ("flip", (tier_board, update))
    assert calls[1] == (
        "clear",
        (tier_board,),
        {
            "ask_confirmation": ask,
            "update_tier_buttons_state": update,
        },
    )


def test_copy_actions_delegate_to_existing_services(monkeypatch):
    calls = []
    monkeypatch.setattr(
        actions,
        "copy_details_with_feedback",
        lambda **kwargs: calls.append(("details", kwargs)),
    )
    monkeypatch.setattr(
        actions,
        "copy_result_image_with_feedback",
        lambda *args: calls.append(("result_image", args)),
    )
    monkeypatch.setattr(
        actions,
        "copy_tier_image_with_feedback",
        lambda **kwargs: calls.append(("tier_image", kwargs)),
    )

    actions.copy_details_from_button(
        profiles={"Balanced": [1.0]},
        profile_combos=[],
        weight_spins=[],
        mix_mode="1 profil",
        mix_modes={"1 profil": 1},
        states=[],
        tier_thresholds={"A": 8.0},
        title="Title",
        copy_btn=FakeButton(),
    )
    actions.copy_result_image_from_button(
        result_card=SimpleNamespace(name="card"),
        copy_img_btn=FakeButton(),
    )
    actions.copy_tier_image_from_button(
        parent=object(),
        tier_board=object(),
        copy_tier_btn=FakeButton(),
        update_tier_buttons_state=lambda: None,
    )

    assert [name for name, _ in calls] == [
        "details",
        "result_image",
        "tier_image",
    ]
