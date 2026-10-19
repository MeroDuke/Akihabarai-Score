"""Best-effort platform evidence for fatal native process failures."""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


DEBUG_ONLY_THIS_PROCESS = 0x00000002
EXCEPTION_DEBUG_EVENT = 1
CREATE_THREAD_DEBUG_EVENT = 2
CREATE_PROCESS_DEBUG_EVENT = 3
EXIT_PROCESS_DEBUG_EVENT = 5
LOAD_DLL_DEBUG_EVENT = 6
DBG_CONTINUE = 0x00010002
DBG_EXCEPTION_NOT_HANDLED = 0x80010001
INFINITE = 0xFFFFFFFF
MINIDUMP_NORMAL = 0x00000000
MINIDUMP_WITH_UNLOADED_MODULES = 0x00000020
MINIDUMP_WITH_THREAD_INFO = 0x00001000


def linux_core_metadata() -> dict[str, str]:
    if not sys.platform.startswith("linux"):
        return {}
    metadata: dict[str, str] = {}
    try:
        import resource

        soft, hard = resource.getrlimit(resource.RLIMIT_CORE)
        metadata["linux_core_limit_soft"] = _format_rlimit(soft, resource.RLIM_INFINITY)
        metadata["linux_core_limit_hard"] = _format_rlimit(hard, resource.RLIM_INFINITY)
    except (ImportError, OSError, ValueError):
        metadata["linux_core_limit_soft"] = "unavailable"
        metadata["linux_core_limit_hard"] = "unavailable"
    try:
        metadata["linux_core_pattern"] = Path(
            "/proc/sys/kernel/core_pattern"
        ).read_text(encoding="utf-8").strip()
    except OSError:
        metadata["linux_core_pattern"] = "unavailable"
    return metadata


def _format_rlimit(value: int, infinity: int) -> str:
    return "unlimited" if value == infinity else str(value)


def should_use_windows_supervisor() -> bool:
    return (
        sys.platform == "win32"
        and bool(getattr(sys, "frozen", False))
        and os.environ.get("AKIHABARAI_CRASH_SUPERVISED") != "1"
    )


def trigger_native_crash_for_test() -> None:
    """Crash only under the explicit private regression-test contract."""
    if os.environ.get("AKIHABARAI_DIAGNOSTIC_TEST_CRASH") != "ci-native-crash-test":
        return
    if sys.platform == "win32":
        kernel32 = ctypes.WinDLL("kernel32")
        kernel32.CreateThread.restype = ctypes.c_void_p
        kernel32.CreateThread(None, 0, None, None, 0, None)
        kernel32.WaitForSingleObject(ctypes.c_void_p(-1), INFINITE)
    else:
        import faulthandler

        faulthandler._sigsegv()


@dataclass(frozen=True)
class SupervisedProcessResult:
    returncode: int
    exception_code: int | None
    dump_path: Path | None


def windows_exception_label(exception_code: int) -> str:
    return {
        0x80000003: "breakpoint",
        0xC0000005: "access_violation",
        0xC000001D: "illegal_instruction",
        0xC0000094: "integer_divide_by_zero",
        0xC00000FD: "stack_overflow",
        0xC0000409: "stack_buffer_overrun_or_fast_fail",
    }.get(exception_code, "unknown_native_exception")


if sys.platform == "win32":
    from ctypes import wintypes

    ULONG_PTR = wintypes.WPARAM

    class EXCEPTION_RECORD(ctypes.Structure):
        _fields_ = [
            ("ExceptionCode", wintypes.DWORD),
            ("ExceptionFlags", wintypes.DWORD),
            ("ExceptionRecord", wintypes.LPVOID),
            ("ExceptionAddress", wintypes.LPVOID),
            ("NumberParameters", wintypes.DWORD),
            ("ExceptionInformation", ULONG_PTR * 15),
        ]

    class EXCEPTION_DEBUG_INFO(ctypes.Structure):
        _fields_ = [
            ("ExceptionRecord", EXCEPTION_RECORD),
            ("dwFirstChance", wintypes.DWORD),
        ]

    class CREATE_THREAD_DEBUG_INFO(ctypes.Structure):
        _fields_ = [
            ("hThread", wintypes.HANDLE),
            ("lpThreadLocalBase", wintypes.LPVOID),
            ("lpStartAddress", wintypes.LPVOID),
        ]

    class CREATE_PROCESS_DEBUG_INFO(ctypes.Structure):
        _fields_ = [
            ("hFile", wintypes.HANDLE),
            ("hProcess", wintypes.HANDLE),
            ("hThread", wintypes.HANDLE),
            ("lpBaseOfImage", wintypes.LPVOID),
            ("dwDebugInfoFileOffset", wintypes.DWORD),
            ("nDebugInfoSize", wintypes.DWORD),
            ("lpThreadLocalBase", wintypes.LPVOID),
            ("lpStartAddress", wintypes.LPVOID),
            ("lpImageName", wintypes.LPVOID),
            ("fUnicode", wintypes.WORD),
        ]

    class EXIT_PROCESS_DEBUG_INFO(ctypes.Structure):
        _fields_ = [("dwExitCode", wintypes.DWORD)]

    class LOAD_DLL_DEBUG_INFO(ctypes.Structure):
        _fields_ = [
            ("hFile", wintypes.HANDLE),
            ("lpBaseOfDll", wintypes.LPVOID),
            ("dwDebugInfoFileOffset", wintypes.DWORD),
            ("nDebugInfoSize", wintypes.DWORD),
            ("lpImageName", wintypes.LPVOID),
            ("fUnicode", wintypes.WORD),
        ]

    class DEBUG_EVENT_UNION(ctypes.Union):
        _fields_ = [
            ("Exception", EXCEPTION_DEBUG_INFO),
            ("CreateThread", CREATE_THREAD_DEBUG_INFO),
            ("CreateProcessInfo", CREATE_PROCESS_DEBUG_INFO),
            ("ExitProcess", EXIT_PROCESS_DEBUG_INFO),
            ("LoadDll", LOAD_DLL_DEBUG_INFO),
            ("padding", ctypes.c_byte * 160),
        ]

    class DEBUG_EVENT(ctypes.Structure):
        _anonymous_ = ("u",)
        _fields_ = [
            ("dwDebugEventCode", wintypes.DWORD),
            ("dwProcessId", wintypes.DWORD),
            ("dwThreadId", wintypes.DWORD),
            ("u", DEBUG_EVENT_UNION),
        ]


def _write_windows_minidump(process_handle, process_id: int, path: Path) -> bool:
    import msvcrt

    dbghelp = ctypes.WinDLL("dbghelp", use_last_error=True)
    dbghelp.MiniDumpWriteDump.argtypes = [
        ctypes.c_void_p,
        ctypes.c_ulong,
        ctypes.c_void_p,
        ctypes.c_ulong,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    dbghelp.MiniDumpWriteDump.restype = ctypes.c_int
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w+b", buffering=0) as stream:
        written = bool(
            dbghelp.MiniDumpWriteDump(
                process_handle,
                process_id,
                ctypes.c_void_p(msvcrt.get_osfhandle(stream.fileno())),
                MINIDUMP_NORMAL
                | MINIDUMP_WITH_UNLOADED_MODULES
                | MINIDUMP_WITH_THREAD_INFO,
                None,
                None,
                None,
            )
        )
    if not written:
        path.unlink(missing_ok=True)
    return written


def supervise_windows_process(
    command: list[str],
    *,
    dump_path: Path,
    environment: dict[str, str] | None = None,
) -> SupervisedProcessResult:
    """Run a Windows child under the debug API and dump second-chance faults."""
    if sys.platform != "win32":
        raise RuntimeError("Windows crash supervision is only available on Windows")

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.WaitForDebugEvent.argtypes = [ctypes.POINTER(DEBUG_EVENT), wintypes.DWORD]
    kernel32.WaitForDebugEvent.restype = wintypes.BOOL
    kernel32.ContinueDebugEvent.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.DWORD]
    kernel32.ContinueDebugEvent.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    child_environment = os.environ.copy()
    if environment:
        child_environment.update(environment)
    child_environment["AKIHABARAI_CRASH_SUPERVISED"] = "1"
    process = subprocess.Popen(
        command,
        env=child_environment,
        creationflags=DEBUG_ONLY_THIS_PROCESS,
    )
    process_handle = None
    exception_code = None
    written_dump = None
    exit_code = 1

    while True:
        event = DEBUG_EVENT()
        if not kernel32.WaitForDebugEvent(ctypes.byref(event), INFINITE):
            process.kill()
            process.wait(timeout=5)
            raise OSError(ctypes.get_last_error(), "WaitForDebugEvent failed")

        continue_status = DBG_CONTINUE
        code = event.dwDebugEventCode
        if code == CREATE_PROCESS_DEBUG_EVENT:
            process_handle = event.CreateProcessInfo.hProcess
            for handle in (event.CreateProcessInfo.hFile, event.CreateProcessInfo.hThread):
                if handle:
                    kernel32.CloseHandle(handle)
        elif code == CREATE_THREAD_DEBUG_EVENT:
            if event.CreateThread.hThread:
                kernel32.CloseHandle(event.CreateThread.hThread)
        elif code == LOAD_DLL_DEBUG_EVENT:
            if event.LoadDll.hFile:
                kernel32.CloseHandle(event.LoadDll.hFile)
        elif code == EXCEPTION_DEBUG_EVENT:
            continue_status = DBG_EXCEPTION_NOT_HANDLED
            if not event.Exception.dwFirstChance:
                exception_code = int(event.Exception.ExceptionRecord.ExceptionCode)
                if process_handle and _write_windows_minidump(
                    process_handle, event.dwProcessId, dump_path
                ):
                    written_dump = dump_path
        elif code == EXIT_PROCESS_DEBUG_EVENT:
            exit_code = int(event.ExitProcess.dwExitCode)

        kernel32.ContinueDebugEvent(
            event.dwProcessId, event.dwThreadId, continue_status
        )
        if code == EXIT_PROCESS_DEBUG_EVENT:
            break

    process.wait(timeout=5)
    if process_handle:
        kernel32.CloseHandle(process_handle)
    return SupervisedProcessResult(exit_code, exception_code, written_dump)


def classify_evidence(text: str) -> tuple[str, str]:
    """Return a cautious likely layer and an explicit evidence limitation."""
    lowered = text.casefold().replace("\\", "/")
    graphics_markers = (
        "qwindows",
        "qxcb",
        "qwayland",
        "opengl",
        "vulkan",
        "nvidia",
        "amdvlk",
    )
    if any(marker in lowered for marker in graphics_markers):
        category = "graphics-or-platform-plugin"
    elif any(marker in lowered for marker in ("pyqt6", "qt6core", "qt6gui", "qt6widgets")):
        category = "pyqt-or-qt"
    elif any(marker in lowered for marker in ("app/", "akihabaraiscore")):
        category = "own-python-code"
    elif any(marker in lowered for marker in ("kernel32", "ntdll", "libc.so", "libpthread")):
        category = "operating-system-or-native-runtime"
    else:
        category = "insufficient-evidence"
    return category, "likely_layer_only_not_root_cause"
