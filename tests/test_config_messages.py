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
