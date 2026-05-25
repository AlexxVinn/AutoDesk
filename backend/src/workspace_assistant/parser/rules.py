"""Fast rule-based command parser — deterministic patterns first."""

from __future__ import annotations

import re
from typing import Callable

from workspace_assistant.automation.profiles import resolve_chrome_profile
from workspace_assistant.config import get_config
from workspace_assistant.executor.actions import ActionStep, CommandPlan
from workspace_assistant.presets import PresetManager


class RuleParser:
    def __init__(self) -> None:
        self._presets = PresetManager()
        self._config = get_config()
        self._rules: list[tuple[re.Pattern[str], Callable[[re.Match[str], str], CommandPlan | None]]] = [
            (re.compile(r"^open coding workspace$", re.I), self._preset("open_coding_workspace")),
            (re.compile(r"^coding mode$", re.I), self._preset("coding_mode")),
            (re.compile(r"^focus mode$", re.I), self._preset("focus_mode")),
            (re.compile(r"^split screen$", re.I), self._preset("split_screen")),
            (re.compile(r"^alexandr browser stack$", re.I), self._preset("alexandr_browser_stack")),
            (
                re.compile(
                    r"^copy (?:the )?results?(?: from chatgpt)?(?: and)? paste (?:it )?(?:to|into|in) cursor$",
                    re.I,
                ),
                self._copy_chatgpt_to_cursor,
            ),
            (re.compile(r"^copy chatgpt(?: response)? to cursor$", re.I), self._copy_chatgpt_to_cursor),
            (
                re.compile(
                    r"^(?:make a )?prompt (?:to )?chatgpt[:\s]+[\"\u201c](?P<text>.+?)[\"\u201d]\s*$",
                    re.I,
                ),
                self._chatgpt_prompt_quoted,
            ),
            (
                re.compile(
                    r"^(?:tell|ask) chatgpt[:\s]+[\"\u201c](?P<text>.+?)[\"\u201d]\s*$",
                    re.I,
                ),
                self._chatgpt_prompt_quoted,
            ),
            (
                re.compile(r"^open chrome in (?:my )?(?P<profile>.+?)(?: account)?$", re.I),
                self._open_chrome_profile,
            ),
            (re.compile(r"^open chrome$", re.I), self._open_chrome_default),
            (re.compile(r"^open (?:cursor|courser)$", re.I), self._open_cursor_fullscreen),
            (re.compile(r"^open youtube(?: tab)?$", re.I), self._open_youtube),
            (re.compile(r"^open chatgpt$", re.I), self._open_chatgpt),
            (re.compile(r"^launch cursor(?: and chrome)?$", re.I), self._launch_cursor_chrome),
            (re.compile(r"^focus cursor$", re.I), self._focus("cursor")),
            (re.compile(r"^focus chrome$", re.I), self._focus("chrome")),
            (re.compile(r"^open (?P<project>.+?) project$", re.I), self._open_project),
            (re.compile(r"^open my (?P<project>.+)$", re.I), self._open_project_loose),
            (re.compile(r"^search google for (?P<query>.+)$", re.I), self._google_search),
            (re.compile(r"^google (?P<query>.+)$", re.I), self._google_search),
            (
                re.compile(
                    r"^open cursor and chatgpt side by side(?: and load (?P<project>.+))?$",
                    re.I,
                ),
                self._cursor_chatgpt_split,
            ),
        ]

    def _preset(self, preset_id: str):
        def handler(_m: re.Match[str], text: str) -> CommandPlan:
            return CommandPlan(
                source_text=text,
                steps=[ActionStep(action="run_preset", params={"preset_id": preset_id})],
                parser="rules",
            )

        return handler

    def _copy_chatgpt_to_cursor(self, _m: re.Match[str], text: str) -> CommandPlan:
        return CommandPlan(
            source_text=text,
            steps=[ActionStep(action="copy_chatgpt_to_cursor", params={})],
            parser="rules",
        )

    def _chatgpt_prompt_quoted(self, m: re.Match[str], text: str) -> CommandPlan:
        return CommandPlan(
            source_text=text,
            steps=[ActionStep(action="chatgpt_prompt", params={"text": m.group("text").strip()})],
            parser="rules",
        )

    def _open_chrome_profile(self, m: re.Match[str], text: str) -> CommandPlan:
        profile = resolve_chrome_profile(m.group("profile"))
        return CommandPlan(
            source_text=text,
            steps=[ActionStep(action="open_app", params={"app_id": "chrome", "profile": profile})],
            parser="rules",
        )

    def _open_chrome_default(self, _m: re.Match[str], text: str) -> CommandPlan:
        return CommandPlan(
            source_text=text,
            steps=[
                ActionStep(
                    action="open_app",
                    params={"app_id": "chrome", "profile": "alexandr_vinnitchii"},
                )
            ],
            parser="rules",
        )

    def _open_cursor_fullscreen(self, _m: re.Match[str], text: str) -> CommandPlan:
        return CommandPlan(
            source_text=text,
            steps=[ActionStep(action="open_app", params={"app_id": "cursor", "fullscreen": True})],
            parser="rules",
        )

    def _open_youtube(self, _m: re.Match[str], text: str) -> CommandPlan:
        return CommandPlan(
            source_text=text,
            steps=[
                ActionStep(
                    action="open_url",
                    params={"app_id": "youtube", "profile": "alexandr_vinnitchii"},
                )
            ],
            parser="rules",
        )

    def _launch_cursor_chrome(self, _m: re.Match[str], text: str) -> CommandPlan:
        return CommandPlan(
            source_text=text,
            steps=[
                ActionStep(action="launch_app", params={"app_id": "cursor"}),
                ActionStep(
                    action="launch_app",
                    params={"app_id": "chrome", "profile": "alexandr_vinnitchii"},
                ),
            ],
            parser="rules",
        )

    def _open_chatgpt(self, _m: re.Match[str], text: str) -> CommandPlan:
        return CommandPlan(
            source_text=text,
            steps=[
                ActionStep(
                    action="open_url",
                    params={"app_id": "chatgpt", "profile": "alexandr_vinnitchii"},
                )
            ],
            parser="rules",
        )

    def _focus(self, app_id: str):
        def handler(_m: re.Match[str], text: str) -> CommandPlan:
            return CommandPlan(
                source_text=text,
                steps=[ActionStep(action="focus_app", params={"app_id": app_id})],
                parser="rules",
            )

        return handler

    def _resolve_project_id(self, name: str) -> str | None:
        key = name.strip().lower().replace(" ", "_")
        projects = self._config.projects
        if key in projects:
            return key
        for pid, proj in projects.items():
            aliases = [a.lower() for a in proj.get("alias", [])]
            if name.lower() in aliases or proj.get("label", "").lower() == name.lower():
                return pid
        return key if key in projects else None

    def _open_project(self, m: re.Match[str], text: str) -> CommandPlan | None:
        pid = self._resolve_project_id(m.group("project"))
        if not pid:
            return None
        return CommandPlan(
            source_text=text,
            steps=[ActionStep(action="open_project", params={"project_id": pid})],
            parser="rules",
        )

    def _open_project_loose(self, m: re.Match[str], text: str) -> CommandPlan | None:
        return self._open_project(m, text)

    def _google_search(self, m: re.Match[str], text: str) -> CommandPlan:
        return CommandPlan(
            source_text=text,
            steps=[ActionStep(action="search_google", params={"query": m.group("query").strip()})],
            parser="rules",
        )

    def _cursor_chatgpt_split(self, m: re.Match[str], text: str) -> CommandPlan:
        steps = [
            ActionStep(action="launch_app", params={"app_id": "cursor"}),
            ActionStep(
                action="launch_app",
                params={"app_id": "chrome", "profile": "alexandr_vinnitchii"},
            ),
            ActionStep(
                action="open_url",
                params={"app_id": "chatgpt", "profile": "alexandr_vinnitchii"},
            ),
            ActionStep(
                action="snap_layout",
                params={"layout": "split_lr", "left": "cursor", "right": "chrome"},
            ),
        ]
        if m.groupdict().get("project"):
            pid = self._resolve_project_id(m.group("project"))
            if pid:
                steps.insert(2, ActionStep(action="open_project", params={"project_id": pid}))
        return CommandPlan(source_text=text, steps=steps, parser="rules")

    def parse(self, text: str) -> CommandPlan | None:
        cleaned = text.strip().rstrip(".")
        if not cleaned:
            return None

        preset_id = self._presets.find_by_alias(cleaned)
        if preset_id:
            return CommandPlan(
                source_text=text,
                steps=[ActionStep(action="run_preset", params={"preset_id": preset_id})],
                parser="rules",
            )

        for pattern, handler in self._rules:
            match = pattern.match(cleaned)
            if match:
                plan = handler(match, text)
                if plan:
                    return plan
        return None
