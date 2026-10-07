from types import SimpleNamespace

from PyQt6.QtWidgets import QMainWindow

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

    def primaryScreen(self):
        return getattr(self, "primary_screen", None)

    def screens(self):
        return getattr(self, "available_screens", [])


class FakeRect:
    def __init__(self, x, y, width, height):
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    def x(self):
        return self._x

    def y(self):
        return self._y

    def width(self):
        return self._width

    def height(self):
        return self._height


class FakeScreen:
    def __init__(
        self,
        name,
        available_geometry,
        *,
        geometry=None,
        device_pixel_ratio=1.0,
        logical_dpi=96.0,
    ):
        self._name = name
        self._available_geometry = available_geometry
        self._geometry = geometry or available_geometry
        self._device_pixel_ratio = device_pixel_ratio
        self._logical_dpi = logical_dpi

    def name(self):
        return self._name

    def availableGeometry(self):
        return self._available_geometry

    def geometry(self):
        return self._geometry

    def devicePixelRatio(self):
        return self._device_pixel_ratio

    def logicalDotsPerInch(self):
        return self._logical_dpi


class FakeWindow:
    def __init__(self):
        self.icons = []
        self.resize_calls = []
        self.minimum_size_calls = []
        self.geometry_calls = []
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

    def setGeometry(self, x, y, width, height):
        self.geometry_calls.append((x, y, width, height))

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
        platform="win32",
    )

    assert calls == ["akihabarai.test"]


def test_set_windows_app_user_model_id_skips_on_non_windows_platform():
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
        platform="linux",
    )

    assert calls == []


def test_set_windows_app_user_model_id_skips_when_windll_is_missing():
    bootstrap.set_windows_app_user_model_id(
        "akihabarai.test",
        ctypes_module=SimpleNamespace(),
        platform="win32",
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


def test_show_main_window_clamps_size_and_minimum_to_startup_screen():
    window = FakeWindow()
    screen = FakeScreen(
        "Scaled monitor",
        FakeRect(1920, 0, 1280, 680),
        geometry=FakeRect(1920, 0, 1280, 720),
        device_pixel_ratio=1.5,
        logical_dpi=144.0,
    )
    logs = []

    bootstrap.show_main_window(
        window,
        screen=screen,
        log_info_func=lambda component, message: logs.append((component, message)),
    )

    assert window.resize_calls == []
    assert window.minimum_size_calls == [(1280, 680)]
    assert window.geometry_calls == [(1920, 0, 1280, 680)]
    assert window.show_calls == 1
    assert "screen='Scaled monitor'" in logs[-1][1]
    assert "requested_size=1600x720" in logs[-1][1]
    assert "applied_size=1280x680" in logs[-1][1]


def test_log_screen_environment_records_mixed_dpi_diagnostics():
    primary = FakeScreen(
        "Primary",
        FakeRect(0, 0, 1920, 1040),
        device_pixel_ratio=1.0,
        logical_dpi=96.0,
    )
    scaled = FakeScreen(
        "Scaled",
        FakeRect(1920, 0, 1280, 680),
        geometry=FakeRect(1920, 0, 1280, 720),
        device_pixel_ratio=1.5,
        logical_dpi=144.0,
    )
    app = FakeApplication([])
    app.primary_screen = primary
    app.available_screens = [primary, scaled]
    logs = []

    selected = bootstrap.select_and_log_startup_screen(
        app,
        log_info_func=lambda component, message: logs.append((component, message)),
    )

    assert selected is primary
    assert len(logs) == 2
    assert "primary=true" in logs[0][1]
    assert "name='Scaled'" in logs[1][1]
    assert "available=1920,0 1280x680" in logs[1][1]
    assert "device_pixel_ratio=1.500" in logs[1][1]
    assert "logical_dpi=144.000" in logs[1][1]


def test_main_window_startup_workflow_uses_selected_screen_geometry(qtbot):
    class StartupWindow(QMainWindow):
        def get_default_window_size(self):
            return (1600, 720)

        def get_minimum_window_size(self):
            return (1600, 720)

    window = StartupWindow()
    qtbot.addWidget(window)
    screen = FakeScreen(
        "Mixed DPI primary",
        FakeRect(100, 50, 1280, 680),
        device_pixel_ratio=1.5,
        logical_dpi=144.0,
    )

    bootstrap.show_main_window(window, screen=screen, log_info_func=lambda *_: None)
    qtbot.waitUntil(window.isVisible)

    assert window.minimumWidth() == 1280
    assert window.minimumHeight() == 680
    assert window.geometry().getRect() == (100, 50, 1280, 680)


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
        app = FakeApplication(argv)
        app.primary_screen = FakeScreen("Primary", FakeRect(0, 0, 1920, 1040))
        app.available_screens = [app.primary_screen]
        return app

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
        platform="win32",
        exit_func=lambda code: events.append(("exit", code)),
        set_exception_hook_func=lambda hook: events.append(("exception_hook", hook)),
    )

    assert events[0:2] == [
        "logger",
        ("log", "app", "Starting AkihabaraiScore"),
    ]
    assert events[2][0] == "exception_hook"
    assert events[3:5] == [
        ("app_id", "akihabarai.test"),
        ("app", ["akihabarai-score"]),
    ]
    assert "window" in events
    assert window.icons == ["icon"]
    assert window.resize_calls == []
    assert window.minimum_size_calls == [(1280, 720)]
    assert window.geometry_calls == [(160, 160, 1600, 720)]
    assert window.show_calls == 1
    assert ("log", "app", "Main window ready") in events
    assert ("log", "app", "AkihabaraiScore stopped: exit_code=12") in events
    assert events[-1] == ("exit", 12)


def test_unhandled_exception_hook_logs_and_delegates():
    events = []
    hook = bootstrap.build_unhandled_exception_hook(
        log_error_func=lambda component, message: events.append(
            ("log", component, message)
        ),
        fallback_hook=lambda *args: events.append(("fallback", args)),
    )
    error = RuntimeError("boom")

    hook(RuntimeError, error, None)

    assert events[0][0:2] == ("log", "app")
    assert "unhandled_exception" in events[0][2]
    assert "RuntimeError: boom" in events[0][2]
    assert events[1] == ("fallback", (RuntimeError, error, None))
