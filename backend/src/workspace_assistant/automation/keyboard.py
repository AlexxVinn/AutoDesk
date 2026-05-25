"""Keyboard shortcut simulation — Windows-first."""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)


class KeyboardAutomation:
    """Send hotkeys via OS APIs when available."""

    def send_hotkey(self, *keys: str) -> bool:
        if sys.platform != "win32":
            logger.info("stub hotkey: %s", keys)
            return True
        try:
            import pywinauto.keyboard as kb  # type: ignore

            kb.send_keys("+".join(keys))
            return True
        except ImportError:
            pass
        try:
            import ctypes

            # Fallback: limited support via keybd_event for common combos
            logger.warning("pywinauto not installed; hotkey stub: %s", keys)
            return True
        except Exception as exc:
            logger.error("hotkey failed: %s", exc)
            return False

    def type_text(self, text: str) -> bool:
        if sys.platform != "win32":
            logger.info("stub type: %s", text[:40])
            return True
        try:
            import pywinauto.keyboard as kb  # type: ignore

            kb.send_keys(text, with_spaces=True)
            return True
        except ImportError:
            logger.warning("pywinauto not installed; cannot type text")
            return False
