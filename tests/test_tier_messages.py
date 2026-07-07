from app.widgets import tier_messages


def test_missing_tier_title_warning_uses_hungarian_text(monkeypatch):
    calls = []
    monkeypatch.setattr(
        tier_messages.QMessageBox,
        "warning",
        lambda parent, title, text: calls.append((parent, title, text)),
    )

    tier_messages.show_missing_tier_title_warning(None)

    assert calls == [
        (
            None,
            "Hiányzó cím",
            "Tier listához csak megadott címmel lehet elemet hozzáadni.",
        )
    ]


def test_duplicate_tier_title_information_uses_hungarian_text(monkeypatch):
    calls = []
    monkeypatch.setattr(
        tier_messages.QMessageBox,
        "information",
        lambda parent, title, text: calls.append((parent, title, text)),
    )

    tier_messages.show_duplicate_tier_title_information(None)

    assert calls == [
        (
            None,
            "Már szerepel",
            "Ez a cím már szerepel a Tier listában.",
        )
    ]


def test_tier_image_copy_error_uses_hungarian_text(monkeypatch):
    calls = []
    monkeypatch.setattr(
        tier_messages.QMessageBox,
        "critical",
        lambda parent, title, text: calls.append((parent, title, text)),
    )

    tier_messages.show_tier_image_copy_error(None)

    assert calls == [
        (
            None,
            "Másolási hiba",
            "Nem sikerült a Tier listát képként vágólapra másolni.",
        )
    ]
