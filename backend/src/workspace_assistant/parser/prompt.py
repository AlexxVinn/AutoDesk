"""Build LLM system prompt with live config context."""

from __future__ import annotations

from workspace_assistant.config import get_config
from workspace_assistant.windows.zones import list_zones

BASE_INSTRUCTIONS = """You convert casual spoken desktop commands into a JSON action plan.
Return ONLY valid JSON (no markdown):
{"steps":[{"action":"<name>","params":{}}]}

Rules:
- Map the user's intent to the smallest correct step list.
- Use only actions from the allowed list below.
- Never control the mouse, screenshots, or autonomous loops.
- Prefer run_preset or apply_layout when the user describes a known workflow.
- For Chrome profile "Alexandr" use profile: alexandr_vinnitchii
- If unsure, use one safe step (e.g. focus_app) rather than inventing tools.
"""


ACTION_CATALOG = """
Allowed actions:
- launch_app, open_app (app_id, profile?, fullscreen?, maximize?, launch_wait?)
- focus_app (app_id)
- open_url, open_url_in_chrome (url | app_id, profile?)
- open_project (project_id)
- apply_layout (layout_id | slots:[{app_id, zone}])
- place_app (app_id, zone)
- snap_layout (left, right app_ids — legacy split)
- maximize, minimize, close_apps (app_ids[])
- run_preset (preset_id)
- chatgpt_prompt (text)
- copy_chatgpt, copy_chatgpt_to_cursor, paste_to_app (app_id)
- search_google (query)
- set_volume (level 0-100), adjust_volume (delta), set_mute (muted)
- set_audio_device (device: headsets|earbuds|speakers or alias)
- hotkey (keys[]), wait (seconds)
"""


def build_system_prompt() -> str:
    cfg = get_config()
    apps = ", ".join(sorted(cfg.apps.keys()))
    presets = ", ".join(sorted(cfg.presets.keys()))
    layouts = ", ".join(sorted(cfg.layouts.keys()))
    zones = ", ".join(list_zones())
    audio_aliases = ", ".join(sorted(cfg.audio.get("aliases", {}).keys()))

    return (
        BASE_INSTRUCTIONS
        + ACTION_CATALOG
        + f"\nConfigured app_ids: {apps}"
        + f"\nConfigured presets: {presets}"
        + f"\nConfigured layouts: {layouts}"
        + f"\nLayout zones: {zones}"
        + f"\nAudio aliases: {audio_aliases}"
        + "\nExample: User: 'put cursor on the right and chrome top left with telegram below'"
        + '\n→ {"steps":[{"action":"apply_layout","params":{"slots":[{"app_id":"cursor","zone":"right"},{"app_id":"chrome","zone":"top_left"},{"app_id":"telegram","zone":"bottom_left"}]}}]}'
    )
