from app.services.update_check_service import UpdateCheckResult
import app.services.version_update_workflow_service as workflow_service


class FakeButton:
    def __init__(self):
        self.text = ""
        self.style_sheet = ""

    def setText(self, text):
        self.text = text

    def setStyleSheet(self, style_sheet):
        self.style_sheet = style_sheet


def test_apply_update_check_marks_button_when_update_available(monkeypatch):
    button = FakeButton()
    log_messages = []
    monkeypatch.setattr(
        workflow_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )

    workflow_service.apply_update_check_to_version_button(
        version_btn=button,
        app_version="0.18.0",
        default_button_text="Verzió: v0.18.0",
        check_for_update_func=lambda version: UpdateCheckResult(
            ok=True,
            update_available=True,
            local_version="v0.18.0",
            latest_version="v0.19.0",
        ),
    )

    assert button.text == "Frissítés elérhető: v0.19.0"
    assert "background-color" in button.style_sheet
    assert "font-weight" in button.style_sheet
    assert log_messages == [
        (
            "update_check",
            "update_available: local='v0.18.0' latest='v0.19.0'",
        ),
    ]


def test_apply_update_check_restores_default_button_when_no_update(monkeypatch):
    button = FakeButton()
    button.setText("Frissítés elérhető: v0.19.0")
    button.setStyleSheet("background-color: red; font-weight: bold;")
    log_messages = []
    monkeypatch.setattr(
        workflow_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )

    workflow_service.apply_update_check_to_version_button(
        version_btn=button,
        app_version="0.18.0",
        default_button_text="Verzió: v0.18.0",
        check_for_update_func=lambda version: UpdateCheckResult(
            ok=True,
            update_available=False,
            local_version="v0.18.0",
            latest_version="v0.18.0",
        ),
    )

    assert button.text == "Verzió: v0.18.0"
    assert button.style_sheet == ""
    assert log_messages == [
        (
            "update_check",
            "no_update_available: local='v0.18.0' latest='v0.18.0'",
        ),
    ]


def test_apply_update_check_keeps_button_on_error(monkeypatch):
    button = FakeButton()
    button.setText("Verzió: v0.18.0")
    log_messages = []
    monkeypatch.setattr(
        workflow_service,
        "log_warning",
        lambda component, message: log_messages.append((component, message)),
    )

    workflow_service.apply_update_check_to_version_button(
        version_btn=button,
        app_version="0.18.0",
        default_button_text="Verzió: v0.18.0",
        check_for_update_func=lambda version: UpdateCheckResult(
            ok=False,
            error="network timeout",
        ),
    )

    assert button.text == "Verzió: v0.18.0"
    assert button.style_sheet == ""
    assert log_messages == [
        ("update_check", "update_check_failed: network timeout"),
    ]
