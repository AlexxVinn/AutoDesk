"""Load and resolve layout definitions from config."""

from __future__ import annotations

from typing import Any

from workspace_assistant.config import get_config


class LayoutManager:
    def __init__(self) -> None:
        self._config = get_config()
        self._layouts = self._config.layouts

    def list_layouts(self) -> list[dict[str, str]]:
        return [
            {"id": lid, "label": layout.get("label", lid), "slots": len(layout.get("slots", []))}
            for lid, layout in self._layouts.items()
        ]

    def get_layout(self, layout_id: str) -> dict[str, Any] | None:
        return self._layouts.get(layout_id)

    def find_by_alias(self, phrase: str) -> str | None:
        normalized = phrase.strip().lower()
        for lid, layout in self._layouts.items():
            if normalized == lid.replace("_", " "):
                return lid
            aliases = [a.lower() for a in layout.get("alias", [])]
            if normalized in aliases:
                return lid
            if normalized == layout.get("label", "").lower():
                return lid
        return None

    def slots_for(self, layout_id: str) -> list[dict[str, str]]:
        layout = self.get_layout(layout_id)
        if not layout:
            return []
        return list(layout.get("slots", []))
