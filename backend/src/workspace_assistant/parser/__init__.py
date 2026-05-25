"""Hybrid parser: fast rules, layout phrases, optional local/cloud LLM."""

from __future__ import annotations

from workspace_assistant.config import get_config
from workspace_assistant.executor.actions import CommandPlan

from .layout_parse import parse_layout_phrase
from .llm import LLMParser
from .rules import RuleParser


class CommandParser:
    """
    Parsing modes (settings.parser.mode):
    - hybrid: rules → layout → LLM (fast exact commands first)
    - natural: layout → LLM → rules (more fluid speech)
    - llm: LLM only (when enabled)
    - rules: deterministic only
    """

    def __init__(self) -> None:
        self._rules = RuleParser()
        self._llm = LLMParser()
        self._mode = get_config().settings.parser.mode

    def parse(self, text: str) -> CommandPlan | None:
        if self._mode == "rules":
            return self._rules_only(text)
        if self._mode == "llm":
            return self._llm_only(text)
        if self._mode == "natural":
            return self._natural(text)
        return self._hybrid(text)

    def _rules_only(self, text: str) -> CommandPlan | None:
        return self._rules.parse(text) or parse_layout_phrase(text)

    def _llm_only(self, text: str) -> CommandPlan | None:
        if self._llm.available:
            return self._llm.parse(text)
        return self._rules_only(text)

    def _hybrid(self, text: str) -> CommandPlan | None:
        plan = self._rules.parse(text)
        if plan:
            return plan
        plan = parse_layout_phrase(text)
        if plan:
            return plan
        if self._llm.available:
            return self._llm.parse(text)
        return None

    def _natural(self, text: str) -> CommandPlan | None:
        """Prefer LLM for conversational commands; keep layout regex as cheap path."""
        plan = parse_layout_phrase(text)
        if plan:
            return plan
        if self._llm.available:
            plan = self._llm.parse(text)
            if plan:
                return plan
        return self._rules.parse(text)
