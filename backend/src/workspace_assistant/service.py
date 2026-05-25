"""Orchestration service used by CLI and tests."""

from __future__ import annotations

from workspace_assistant.executor import ActionExecutor
from workspace_assistant.parser import CommandParser


class AssistantService:
    def __init__(self) -> None:
        self.parser = CommandParser()
        self.executor = ActionExecutor()

    def handle_text(self, text: str) -> dict:
        plan = self.parser.parse(text)
        if not plan:
            return {"success": False, "error": "parse_failed", "text": text}
        result = self.executor.execute_plan(plan)
        return {"success": result["success"], "plan": plan.model_dump(), "result": result}
