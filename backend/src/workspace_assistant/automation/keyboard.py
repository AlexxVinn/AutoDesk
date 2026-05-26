"""Keyboard shortcut simulation — Windows-first with ctypes fallback."""

from __future__ import annotations

import logging
import sys
import time

logger = logging.getLogger(__name__)

VK = {
    "ctrl": 0x11,
    "control": 0x11,
    "shift": 0x10,
    "alt": 0x12,
    "enter": 0x0D,
    "return": 0x0D,
    "tab": 0x09,
    "esc": 0x1B,
    "escape": 0x1B,
    "a": 0x41,
    "c": 0x43,
    "v": 0x56,
}


class KeyboardAutomation:
    """Send hotkeys and text via OS APIs."""

    def send_hotkey(self, *keys: str) -> bool:
        return self.send_combo(list(keys))

    def send_combo(self, keys: list[str]) -> bool:
        normalized = [k.lower() for k in keys]
        if sys.platform != "win32":
            logger.info("stub hotkey: %s", normalized)
            return True
        if self._send_combo_ctypes(normalized):
            return True
        try:
            import pywinauto.keyboard as kb  # type: ignore

            kb.send_keys("+".join(normalized))
            return True
        except ImportError:
            logger.warning("hotkey unavailable: %s", normalized)
            return False

    def type_text(self, text: str) -> bool:
        if not text:
            return True
        if sys.platform != "win32":
            logger.info("stub type: %s", text[:60])
            return True
        # Paste via clipboard is more reliable than per-character typing for long prompts.
        try:
            import pyperclip

            previous = pyperclip.paste()
            pyperclip.copy(text)
            time.sleep(0.05)
            ok = self.send_combo(["ctrl", "v"])
            time.sleep(0.05)
            try:
                pyperclip.copy(previous)
            except Exception:
                pass
            return ok
        except ImportError:
            pass
        try:
            import pywinauto.keyboard as kb  # type: ignore

            kb.send_keys(text, with_spaces=True)
            return True
        except ImportError:
            logger.warning("pyperclip/pywinauto not installed; cannot type text")
            return False

    def _send_combo_ctypes(self, keys: list[str]) -> bool:
        try:
            import ctypes

            user32 = ctypes.windll.user32
            KEYEVENTF_KEYUP = 0x0002

            mods = []
            main = None
            for key in keys:
                if key in ("ctrl", "control", "shift", "alt"):
                    mods.append(VK[key])
                elif key in VK:
                    main = VK[key]

            if main is None:
                return False

            for mod in mods:
                user32.keybd_event(mod, 0, 0, 0)
            user32.keybd_event(main, 0, 0, 0)
            user32.keybd_event(main, 0, KEYEVENTF_KEYUP, 0)
            for mod in reversed(mods):
                user32.keybd_event(mod, 0, KEYEVENTF_KEYUP, 0)
            return True
        except Exception as exc:
            logger.debug("ctypes hotkey failed: %s", exc)
            return False
