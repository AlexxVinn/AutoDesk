"""ChatGPT web UI automation — keyboard-first with optional UI Automation fallback."""

from __future__ import annotations

import logging
import sys
import time

from workspace_assistant.automation.keyboard import KeyboardAutomation
from workspace_assistant.windows import get_window_manager

logger = logging.getLogger(__name__)


class ChatGPTAutomation:
    def __init__(self) -> None:
        self._keyboard = KeyboardAutomation()
        self._windows = get_window_manager()

    def _focus_chatgpt_window(self, title_patterns: list[str] | None = None) -> bool:
        patterns = title_patterns or ["ChatGPT", "chatgpt.com", "ChatGPT -"]
        win = self._windows.find_by_title_patterns(patterns)
        if not win:
            win = self._windows.find_by_title_patterns(["Google Chrome", "Chrome"])
        if not win:
            return False
        return self._windows.focus(win.hwnd)

    def send_prompt(
        self,
        text: str,
        *,
        submit: bool = True,
        title_patterns: list[str] | None = None,
        pause_before_type: float = 0.35,
    ) -> bool:
        if not self._focus_chatgpt_window(title_patterns):
            logger.warning("ChatGPT/Chrome window not found for prompt")
            return False
        time.sleep(pause_before_type)
        if not self._keyboard.type_text(text):
            return False
        if submit:
            time.sleep(0.1)
            return self._keyboard.send_combo(["enter"])
        return True

    def copy_last_response(
        self,
        *,
        title_patterns: list[str] | None = None,
        wait_before_copy: float = 0.2,
    ) -> bool:
        if not self._focus_chatgpt_window(title_patterns):
            return False
        time.sleep(wait_before_copy)

        if sys.platform == "win32" and self._copy_via_uia(title_patterns):
            return True
        if sys.platform == "win32" and self._copy_via_pywinauto():
            return True

        # Fallback: select-all in page often grabs too much; try copy anyway after focus.
        return self._keyboard.send_combo(["ctrl", "c"])

    def _copy_via_pywinauto(self) -> bool:
        try:
            from pywinauto import Desktop

            win = Desktop(backend="uia").window(title_re=".*(ChatGPT|Chrome).*")
            buttons = win.descendants(title="Copy", control_type="Button")
            if not buttons:
                buttons = win.descendants(title_re="Copy", control_type="Button")
            if buttons:
                buttons[-1].click_input()
                time.sleep(0.15)
                return True
        except Exception as exc:
            logger.debug("pywinauto copy fallback: %s", exc)
        return False

    def _copy_via_uia(self, title_patterns: list[str] | None) -> bool:
        try:
            import uiautomation as auto

            patterns = title_patterns or ["ChatGPT", "Chrome"]
            window = None
            for pat in patterns:
                window = auto.WindowControl(searchDepth=1, RegexName=f".*{pat}.*")
                if window.Exists(0.5):
                    break
            if not window or not window.Exists(0):
                return False
            window.SetFocus()
            copies = window.GetChildren()
            copy_buttons = []
            stack = list(copies)
            while stack:
                node = stack.pop()
                if getattr(node, "Name", "") == "Copy":
                    copy_buttons.append(node)
                stack.extend(node.GetChildren())
            if copy_buttons:
                copy_buttons[-1].Click()
                time.sleep(0.15)
                return True
        except ImportError:
            pass
        except Exception as exc:
            logger.debug("uiautomation copy: %s", exc)
        return False
