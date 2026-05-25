"""Hybrid parser: rules first, optional LLM fallback."""

from __future__ import annotations

from workspace_assistant.config import get_config
from workspace_assistant.executor.actions import CommandPlan

from .layout_parse import parse_layout_phrase
from .llm import LLMParser
from .rules import RuleParser


class CommandParser:
    def __init__(self) -> None:
        self._rules = RuleParser()
        self._llm = LLMParser()
        self._mode = get_config().settings.parser.mode

    def parse(self, text: str) -> CommandPlan | None:
        plan = self._rules.parse(text)
        if plan:
            return plan
        plan = parse_layout_phrase(text)
        if plan:
            return plan
        if self._mode in ("hybrid", "llm") and self._llm.available:
            return self._llm.parse(text)
        return None
