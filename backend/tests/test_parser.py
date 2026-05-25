import os

os.environ.setdefault("WORKSPACE_ASSISTANT_CONFIG", os.path.join(os.path.dirname(__file__), "../../config"))

from workspace_assistant.parser import CommandParser


def test_rule_preset_coding_workspace():
    parser = CommandParser()
    plan = parser.parse("open coding workspace")
    assert plan is not None
    assert plan.steps[0].action == "run_preset"
    assert plan.steps[0].params["preset_id"] == "open_coding_workspace"


def test_rule_focus_cursor():
    parser = CommandParser()
    plan = parser.parse("focus cursor")
    assert plan is not None
    assert plan.steps[0].action == "focus_app"
    assert plan.steps[0].params["app_id"] == "cursor"


def test_rule_google_search():
    parser = CommandParser()
    plan = parser.parse("search google for faster whisper latency")
    assert plan is not None
    assert plan.steps[0].action == "search_google"
    assert "faster whisper" in plan.steps[0].params["query"]


def test_rule_physics_project():
    parser = CommandParser()
    plan = parser.parse("open my physics project")
    assert plan is not None
    assert plan.steps[0].action == "open_project"
    assert plan.steps[0].params["project_id"] == "physics"
