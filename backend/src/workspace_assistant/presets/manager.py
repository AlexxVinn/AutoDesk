"""Preset workflow loader and runner."""

from __future__ import annotations

import logging
from typing import Any

from workspace_assistant.config import get_config
from workspace_assistant.executor.actions import ActionStep

logger = logging.getLogger(__name__)


class PresetManager:
    def __init__(self) -> None:
        self._config = get_config()

    def list_presets(self) -> list[dict[str, str]]:
        return [
            {
                "id": pid,
                "label": preset.get("label", pid),
                "description": preset.get("description", ""),
            }
            for pid, preset in self._config.presets.items()
        ]

    def get_preset(self, preset_id: str) -> dict[str, Any] | None:
        return self._config.presets.get(preset_id)

    def find_by_alias(self, phrase: str) -> str | None:
        normalized = phrase.strip().lower()
        for pid, preset in self._config.presets.items():
            aliases = preset.get("alias", [])
            if normalized == pid.replace("_", " ") or normalized in [a.lower() for a in aliases]:
                return pid
            if normalized == preset.get("label", "").lower():
                return pid
        return None

    def steps_for_preset(self, preset_id: str) -> list[ActionStep]:
        preset = self.get_preset(preset_id)
        if not preset:
            return []
        raw_steps = preset.get("steps", [])
        return [ActionStep(**step) for step in raw_steps]
