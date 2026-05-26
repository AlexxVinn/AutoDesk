"""Non-Windows stub for development and CI."""

from __future__ import annotations

import logging
import re

from .base import SnapLayout, WindowInfo, WindowManager
from .zones import PixelRect

logger = logging.getLogger(__name__)


class StubWindowManager(WindowManager):
    def __init__(self) -> None:
        self._windows: list[WindowInfo] = [
            WindowInfo(hwnd=1, title="Cursor - workspace-assistant"),
            WindowInfo(hwnd=2, title="Google Chrome"),
            WindowInfo(hwnd=3, title="Telegram"),
            WindowInfo(hwnd=4, title="Viber"),
            WindowInfo(hwnd=5, title="Windows Terminal"),
        ]

    def list_windows(self) -> list[WindowInfo]:
        return list(self._windows)

    def focus(self, hwnd: int) -> bool:
        logger.info("stub focus hwnd=%s", hwnd)
        return True

    def find_by_title_patterns(self, patterns: list[str]) -> WindowInfo | None:
        compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
        for win in self._windows:
            if any(c.search(win.title) for c in compiled):
                return win
        return None

    def get_primary_work_area(self) -> tuple[int, int, int, int]:
        return 0, 0, 1920, 1040

    def place_rect(self, hwnd: int, rect: PixelRect) -> bool:
        logger.info("stub place hwnd=%s rect=%s", hwnd, rect)
        return True

    def snap(self, hwnd: int, layout: SnapLayout) -> bool:
        logger.info("stub snap hwnd=%s layout=%s", hwnd, layout)
        return True

    def move_to_monitor(self, hwnd: int, monitor_index: int) -> bool:
        logger.info("stub move hwnd=%s monitor=%s", hwnd, monitor_index)
        return True

    def close(self, hwnd: int) -> bool:
        self._windows = [w for w in self._windows if w.hwnd != hwnd]
        return True
