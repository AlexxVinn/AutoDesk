"""Resolve friendly Chrome profile names from config aliases."""

from __future__ import annotations

import re

from workspace_assistant.config import get_config


def resolve_chrome_profile(name: str | None) -> str | None:
    if not name:
        return None
    chrome = get_config().apps.get("chrome", {})
    aliases = chrome.get("profile_aliases", {})
    key = name.strip().lower()
    key = re.sub(r"\s+account$", "", key)
    key = re.sub(r"^my\s+", "", key)
    if key in aliases:
        return aliases[key]
    slug = key.replace(" ", "_")
    profiles = chrome.get("profiles", {})
    if slug in profiles:
        return slug
    return slug
