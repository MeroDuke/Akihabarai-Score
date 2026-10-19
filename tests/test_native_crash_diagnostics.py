import sys

from app import native_crash_diagnostics as diagnostics


def test_classify_evidence_prefers_graphics_platform_markers():
    category, limitation = diagnostics.classify_evidence(
        "PyQt6 Qt6Gui qwindows.dll NVIDIA"
    )

    assert category == "graphics-or-platform-plugin"
    assert limitation == "likely_layer_only_not_root_cause"


def test_classify_evidence_reports_own_application_frame():
    category, limitation = diagnostics.classify_evidence(
        "File D:/Akihabarai-Score/app/services/example.py"
    )

    assert category == "own-python-code"
    assert limitation == "likely_layer_only_not_root_cause"


def test_classify_evidence_does_not_guess_without_markers():
    assert diagnostics.classify_evidence("address 0x00000000") == (
        "insufficient-evidence",
        "likely_layer_only_not_root_cause",
    )


def test_linux_core_metadata_has_limit_and_handler_information():
    metadata = diagnostics.linux_core_metadata()

    if sys.platform.startswith("linux"):
        assert "linux_core_limit_soft" in metadata
        assert "linux_core_limit_hard" in metadata
        assert "linux_core_pattern" in metadata
    else:
        assert metadata == {}


def test_windows_exception_label_is_descriptive_without_claiming_root_cause():
    assert diagnostics.windows_exception_label(0xC0000005) == "access_violation"
    assert diagnostics.windows_exception_label(0xDEADBEEF) == "unknown_native_exception"
