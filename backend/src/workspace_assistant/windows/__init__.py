"""Platform window manager factory."""

from __future__ import annotations

import sys

from .base import WindowManager
from .stub_manager import StubWindowManager


def get_window_manager() -> WindowManager:
    if sys.platform == "win32":
        from .win32_manager import Win32WindowManager

        return Win32WindowManager()
    return StubWindowManager()
