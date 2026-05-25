"""Windows-native window management via Win32 APIs."""

from __future__ import annotations

import ctypes
import re
import sys
from ctypes import wintypes

from .base import SnapLayout, WindowInfo, WindowManager

if sys.platform != "win32":
    raise RuntimeError("win32_manager is Windows-only")

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

SW_RESTORE = 9
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
HWND_TOP = 0
SWP_SHOWWINDOW = 0x0040
MONITOR_DEFAULTTONEAREST = 2


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wintypes.DWORD),
    ]


def _get_window_text(hwnd: int) -> str:
    length = user32.GetWindowTextLengthW(hwnd) + 1
    buf = ctypes.create_unicode_buffer(length)
    user32.GetWindowTextW(hwnd, buf, length)
    return buf.value


def _is_visible(hwnd: int) -> bool:
    return bool(user32.IsWindowVisible(hwnd))


def _enum_windows() -> list[int]:
    handles: list[int] = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def callback(hwnd, _lparam):
        if _is_visible(hwnd) and _get_window_text(hwnd):
            handles.append(hwnd)
        return True

    user32.EnumWindows(callback, 0)
    return handles


def _work_area_for_window(hwnd: int) -> RECT:
    monitor = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
    info = MONITORINFO()
    info.cbSize = ctypes.sizeof(MONITORINFO)
    user32.GetMonitorInfoW(monitor, ctypes.byref(info))
    return info.rcWork


class Win32WindowManager(WindowManager):
    def list_windows(self) -> list[WindowInfo]:
        result: list[WindowInfo] = []
        for hwnd in _enum_windows():
            title = _get_window_text(hwnd)
            rect = RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            result.append(
                WindowInfo(
                    hwnd=hwnd,
                    title=title,
                    rect=(rect.left, rect.top, rect.right, rect.bottom),
                )
            )
        return result

    def focus(self, hwnd: int) -> bool:
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetForegroundWindow(hwnd)
        user32.BringWindowToTop(hwnd)
        return True

    def find_by_title_patterns(self, patterns: list[str]) -> WindowInfo | None:
        compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
        for win in self.list_windows():
            if any(c.search(win.title) for c in compiled):
                return win
        return None

    def snap(self, hwnd: int, layout: SnapLayout) -> bool:
        if layout == "maximize":
            user32.ShowWindow(hwnd, SW_MAXIMIZE)
            return True
        if layout == "minimize":
            user32.ShowWindow(hwnd, SW_MINIMIZE)
            return True
        if layout == "restore":
            user32.ShowWindow(hwnd, SW_RESTORE)
            return True

        work = _work_area_for_window(hwnd)
        width = work.right - work.left
        height = work.bottom - work.top
        half = width // 2

        if layout in ("left", "split_lr"):
            user32.SetWindowPos(
                hwnd, HWND_TOP, work.left, work.top, half, height, SWP_SHOWWINDOW
            )
            return True
        if layout == "right":
            user32.SetWindowPos(
                hwnd,
                HWND_TOP,
                work.left + half,
                work.top,
                width - half,
                height,
                SWP_SHOWWINDOW,
            )
            return True
        return False

    def move_to_monitor(self, hwnd: int, monitor_index: int) -> bool:
        monitors: list[RECT] = []

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(RECT), wintypes.LPARAM)
        def callback(hmon, _hdc, lprect, _lparam):
            monitors.append(lprect.contents)
            return True

        user32.EnumDisplayMonitors(0, 0, callback, 0)
        if monitor_index < 0 or monitor_index >= len(monitors):
            return False
        m = monitors[monitor_index]
        w = m.right - m.left
        h = m.bottom - m.top
        user32.SetWindowPos(hwnd, HWND_TOP, m.left, m.top, w, h, SWP_SHOWWINDOW)
        return True

    def close(self, hwnd: int) -> bool:
        return bool(user32.PostMessageW(hwnd, 0x0010, 0, 0))  # WM_CLOSE
