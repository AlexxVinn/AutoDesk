"""Window management abstraction — platform-specific implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

from .zones import PixelRect, zone_to_rect

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
    def place_rect(self, hwnd: int, rect: PixelRect) -> bool:
        ...

    @abstractmethod
    def get_primary_work_area(self) -> tuple[int, int, int, int]:
        """Return (left, top, width, height) of primary monitor work area."""
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

    def place_in_zone(self, hwnd: int, zone: str) -> bool:
        left, top, width, height = self.get_primary_work_area()
        rect = zone_to_rect(zone, left, top, width, height)
        if not rect:
            return False
        return self.place_rect(hwnd, rect)

    def apply_slots(self, slots: list[dict[str, Any]], pattern_resolver) -> bool:
        ok = True
        for slot in slots:
            app_id = slot.get("app_id", "")
            zone = slot.get("zone", "left")
            patterns = pattern_resolver(app_id)
            win = self.find_by_title_patterns(patterns)
            if not win:
                ok = False
                continue
            if self.place_in_zone(win.hwnd, zone):
                self.focus(win.hwnd)
            else:
                ok = False
        return ok
