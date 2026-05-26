"""Parse free-form layout phrases into slot lists."""

from __future__ import annotations

import re

from workspace_assistant.executor.actions import ActionStep, CommandPlan

APP_ALIASES = {
    "courser": "cursor",
    "vscode": "cursor",
    "code": "cursor",
    "google chrome": "chrome",
    "browser": "chrome",
    "wt": "terminal",
    "windows terminal": "terminal",
    "powershell": "terminal",
    "tg": "telegram",
}

ZONE_PHRASES: list[tuple[str, str]] = [
    (r"on the right$", "right"),
    (r"on the left$", "left"),
    (r"top left$", "top_left"),
    (r"top right$", "top_right"),
    (r"bottom left$", "bottom_left"),
    (r"bottom right$", "bottom_right"),
    (r"top$", "top"),
    (r"bottom$", "bottom"),
    (r"left$", "left"),
    (r"right$", "right"),
]


def normalize_app(name: str) -> str:
    key = name.strip().lower()
    return APP_ALIASES.get(key, key.replace(" ", "_"))


def parse_layout_phrase(text: str) -> CommandPlan | None:
    """e.g. 'cursor on the right chrome top left and telegram bottom left'."""
    cleaned = text.strip().lower()
    for prefix in ("layout ", "put ", "arrange ", "split "):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :].strip()
            break

    parts = re.split(r"\s+and\s+", cleaned)
    slots: list[dict[str, str]] = []

    for part in parts:
        part = part.strip()
        if not part:
            continue
        zone = None
        app_name = part
        for pattern, zone_id in ZONE_PHRASES:
            m = re.search(pattern, part)
            if m:
                zone = zone_id
                app_name = part[: m.start()].strip()
                break
        if not zone or not app_name:
            return None
        slots.append({"app_id": normalize_app(app_name), "zone": zone})

    if len(slots) < 2:
        return None

    return CommandPlan(
        source_text=text,
        steps=[
            ActionStep(action="apply_layout", params={"slots": slots}),
        ],
        parser="layout",
    )
