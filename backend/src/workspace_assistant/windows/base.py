"""Window management abstraction — platform-specific implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

SnapLayout = Literal["left", "right", "maximize", "minimize", "restore", "split_lr"]


@dataclass
class WindowInfo:
    hwnd: int
    title: str
    process_name: str | None = None
    rect: tuple[int, int, int, int] | None = None


class WindowManager(ABC):
    @abstractmethod
    def list_windows(self) -> list[WindowInfo]:
        ...

    @abstractmethod
    def focus(self, hwnd: int) -> bool:
        ...

    @abstractmethod
    def find_by_title_patterns(self, patterns: list[str]) -> WindowInfo | None:
        ...

    @abstractmethod
    def snap(self, hwnd: int, layout: SnapLayout) -> bool:
        ...

    @abstractmethod
    def move_to_monitor(self, hwnd: int, monitor_index: int) -> bool:
        ...

    @abstractmethod
    def close(self, hwnd: int) -> bool:
        ...

    def focus_app(self, title_patterns: list[str]) -> bool:
        win = self.find_by_title_patterns(title_patterns)
        if win:
            return self.focus(win.hwnd)
        return False

    def apply_split_lr(self, left_patterns: list[str], right_patterns: list[str]) -> bool:
        left = self.find_by_title_patterns(left_patterns)
        right = self.find_by_title_patterns(right_patterns)
        ok = True
        if left:
            ok = self.snap(left.hwnd, "left") and ok
        if right:
            ok = self.snap(right.hwnd, "right") and ok
        return ok
