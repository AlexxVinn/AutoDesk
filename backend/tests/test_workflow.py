import os

os.environ.setdefault("WORKSPACE_ASSISTANT_CONFIG", os.path.join(os.path.dirname(__file__), "../../config"))

from workspace_assistant.automation.profiles import resolve_chrome_profile
from workspace_assistant.parser import CommandParser


def test_resolve_chrome_profile_alias():
    assert resolve_chrome_profile("Alexandr Vinnitchii") == "alexandr_vinnitchii"
    assert resolve_chrome_profile("my alexandr vinnitchii account") == "alexandr_vinnitchii"


def test_open_cursor_fullscreen():
    plan = CommandParser().parse("open courser")
    assert plan is not None
    assert plan.steps[0].action == "open_app"
    assert plan.steps[0].params["app_id"] == "cursor"
    assert plan.steps[0].params["fullscreen"] is True


def test_open_chrome_profile():
    plan = CommandParser().parse("open chrome in my Alexandr Vinnitchii account")
    assert plan is not None
    assert plan.steps[0].params["profile"] == "alexandr_vinnitchii"


def test_chatgpt_prompt():
    plan = CommandParser().parse('make a prompt to chatgpt: "Make me a prompt for this topic"')
    assert plan is not None
    assert plan.steps[0].action == "chatgpt_prompt"
    assert "Make me a prompt" in plan.steps[0].params["text"]


def test_copy_to_cursor():
    plan = CommandParser().parse("copy the results and paste to cursor")
    assert plan is not None
    assert plan.steps[0].action == "copy_chatgpt_to_cursor"
