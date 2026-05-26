import os

os.environ.setdefault("WORKSPACE_ASSISTANT_CONFIG", os.path.join(os.path.dirname(__file__), "../../config"))

from workspace_assistant.executor import ActionExecutor, CommandPlan
from workspace_assistant.parser import CommandParser


def test_execute_focus_cursor_stub():
    parser = CommandParser()
    executor = ActionExecutor()
    plan = parser.parse("focus cursor")
    assert plan is not None
    result = executor.execute_plan(plan)
    assert result["success"] is True
    assert result["steps"][0]["action"] == "focus_app"
