"""Clipboard read/write for cross-app paste workflows."""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)


class Clipboard:
    def get_text(self) -> str | None:
        try:
            import pyperclip

            return pyperclip.paste()
        except Exception as exc:
            logger.error("clipboard read failed: %s", exc)
            return None

    def set_text(self, text: str) -> bool:
        try:
            import pyperclip

            pyperclip.copy(text)
            return True
        except Exception as exc:
            logger.error("clipboard write failed: %s", exc)
            return False

    def copy_selection_windows(self) -> bool:
        if sys.platform != "win32":
            logger.info("stub clipboard copy")
            return True
        from workspace_assistant.automation.keyboard import KeyboardAutomation

        return KeyboardAutomation().send_combo(["ctrl", "c"])
