"""LLM command parser — maps natural language to structured actions only."""

from __future__ import annotations

import json
import logging
import os

from workspace_assistant.config import get_config
from workspace_assistant.executor.actions import ActionStep, CommandPlan

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You convert desktop workspace voice commands into JSON action plans.
Return ONLY valid JSON with this shape:
{"steps":[{"action":"<name>","params":{}}]}

Allowed actions:
launch_app (app_id, profile?, args?)
focus_app (app_id)
open_url (app_id or url)
open_project (project_id)
open_folder (path or project_id)
snap_layout (layout: split_lr, left?, right?)
snap_window (app_id, side: left|right)
maximize, minimize (app_id)
close_apps (app_ids[])
run_preset (preset_id)
search_google (query)
hotkey (keys[])

Known app_ids: cursor, chrome, terminal, spotify, chatgpt
Known presets: coding_mode, focus_mode, split_screen, open_coding_workspace
Known projects: from user config — use snake_case ids like phyzic, physics

Never invent screenshot or mouse click actions. Keep steps minimal and ordered.
"""


class LLMParser:
    def __init__(self) -> None:
        self._settings = get_config().settings.parser
        self._client = None

    @property
    def available(self) -> bool:
        if not self._settings.llm_enabled:
            return False
        return bool(os.environ.get(self._settings.openai_api_key_env))

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI()
        return self._client

    def parse(self, text: str) -> CommandPlan | None:
        if not self.available:
            return None
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self._settings.llm_model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
            )
            raw = response.choices[0].message.content or "{}"
            data = json.loads(raw)
            steps = [ActionStep(**s) for s in data.get("steps", [])]
            if not steps:
                return None
            return CommandPlan(source_text=text, steps=steps, parser="llm", confidence=0.85)
        except Exception as exc:
            logger.error("LLM parse failed: %s", exc)
            return None
