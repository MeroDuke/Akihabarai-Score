from types import SimpleNamespace

from app.services import app_bootstrap_service as bootstrap


class FakeApplication:
    def __init__(self, argv):
        self.argv = argv
        self.icons = []
        self.exec_called = False

    def setWindowIcon(self, icon):
        self.icons.append(icon)

    def exec(self):
        self.exec_called = True
        return 12


class FakeWindow:
    def __init__(self):
        self.icons = []
        self.resize_calls = []
        self.minimum_size_calls = []
        self.show_calls = 0

    def setWindowIcon(self, icon):
        self.icons.append(icon)

    def get_default_window_size(self):
        return (1600, 720)

    def get_minimum_window_size(self):
        return (1280, 720)

    def resize(self, width, height):
        self.resize_calls.append((width, height))

    def setMinimumSize(self, width, height):
        self.minimum_size_calls.append((width, height))

    def show(self):
        self.show_calls += 1


def test_set_windows_app_user_model_id_calls_shell32():
    calls = []
    ctypes_module = SimpleNamespace(
        windll=SimpleNamespace(
            shell32=SimpleNamespace(
                SetCurrentProcessExplicitAppUserModelID=lambda app_id: calls.append(
                    app_id
                )
            )
        )
    )

    bootstrap.set_windows_app_user_model_id(
        "akihabarai.test",
        ctypes_module=ctypes_module,
    )

    assert calls == ["akihabarai.test"]


def test_set_windows_app_user_model_id_skips_when_windll_is_missing():
    bootstrap.set_windows_app_user_model_id(
        "akihabarai.test",
        ctypes_module=SimpleNamespace(),
    )


def test_apply_app_icon_sets_icon_on_app_and_window():
    app = FakeApplication([])
    window = FakeWindow()
    icon = object()

    returned = bootstrap.apply_app_icon(
        app,
        window,
        load_icon_func=lambda: icon,
    )

    assert returned is icon
    assert app.icons == [icon]
    assert window.icons == [icon]


def test_apply_app_icon_skips_when_icon_is_missing():
    app = FakeApplication([])
    window = FakeWindow()

    returned = bootstrap.apply_app_icon(
        app,
        window,
        load_icon_func=lambda: None,
    )

    assert returned is None
    assert app.icons == []
    assert window.icons == []


def test_show_main_window_applies_size_and_shows():
    window = FakeWindow()

    bootstrap.show_main_window(window)

    assert window.resize_calls == [(1600, 720)]
    assert window.minimum_size_calls == [(1280, 720)]
    assert window.show_calls == 1


def test_run_qt_application_bootstraps_and_exits(monkeypatch):
    events = []
    window = FakeWindow()
    ctypes_module = SimpleNamespace(
        windll=SimpleNamespace(
            shell32=SimpleNamespace(
                SetCurrentProcessExplicitAppUserModelID=lambda app_id: events.append(
                    ("app_id", app_id)
                )
            )
        )
    )

    def app_factory(argv):
        events.append(("app", argv))
        return FakeApplication(argv)

    bootstrap.run_qt_application(
        window_factory=lambda: events.append("window") or window,
        argv=["akihabarai-score"],
        app_user_model_id="akihabarai.test",
        qapplication_class=app_factory,
        init_logger_func=lambda: events.append("logger"),
        log_info_func=lambda component, message: events.append(
            ("log", component, message)
        ),
        load_icon_func=lambda: "icon",
        ctypes_module=ctypes_module,
        exit_func=lambda code: events.append(("exit", code)),
    )

    assert events[:4] == [
        "logger",
        ("log", "app", "Starting AkihabaraiScore"),
        ("app_id", "akihabarai.test"),
        ("app", ["akihabarai-score"]),
    ]
    assert "window" in events
    assert window.icons == ["icon"]
    assert window.resize_calls == [(1600, 720)]
    assert window.minimum_size_calls == [(1280, 720)]
    assert window.show_calls == 1
    assert events[-1] == ("exit", 12)
