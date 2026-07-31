from app.widgets import config_messages


def test_profiles_config_error_uses_hungarian_title(monkeypatch):
    calls = []
    monkeypatch.setattr(
        config_messages.QMessageBox,
        "warning",
        lambda parent, title, text: calls.append((parent, title, text)),
    )

    config_messages.show_profiles_config_error(None, "profiles.json missing")

    assert calls == [
        (None, "Konfigurációs hiba", "profiles.json missing")
    ]


def test_ui_config_error_uses_hungarian_title(monkeypatch):
    calls = []
    monkeypatch.setattr(
        config_messages.QMessageBox,
        "warning",
        lambda parent, title, text: calls.append((parent, title, text)),
    )

    config_messages.show_ui_config_error(None, "ui.json invalid")

    assert calls == [
        (None, "Felületkonfigurációs hiba", "ui.json invalid")
    ]


def test_config_dialog_title_translation_is_resolved_when_opened(monkeypatch):
    calls = []
    monkeypatch.setattr(
        config_messages,
        "translate",
        lambda key: {"dialog.config_profiles.title": "Configuration error"}[key],
    )
    monkeypatch.setattr(
        config_messages.QMessageBox,
        "warning",
        lambda parent, title, text: calls.append((title, text)),
    )

    config_messages.show_profiles_config_error(None, "broken")

    assert calls == [("Configuration error", "broken")]
