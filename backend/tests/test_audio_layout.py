import os

os.environ.setdefault("WORKSPACE_ASSISTANT_CONFIG", os.path.join(os.path.dirname(__file__), "../../config"))

from workspace_assistant.parser import CommandParser
from workspace_assistant.windows.layouts import LayoutManager
from workspace_assistant.windows.zones import list_zones


def test_layout_alias_lookup():
    lm = LayoutManager()
    lid = lm.find_by_alias("cursor right chrome top left telegram bottom left")
    assert lid == "cursor_right_chrome_tl_telegram_bl"


def test_freeform_layout_parse():
    plan = CommandParser().parse(
        "put cursor on the right and chrome top left and telegram bottom left"
    )
    assert plan is not None
    assert plan.steps[0].action == "apply_layout"
    slots = plan.steps[0].params["slots"]
    assert len(slots) == 3
    zones = {s["app_id"]: s["zone"] for s in slots}
    assert zones["cursor"] == "right"
    assert zones["chrome"] == "top_left"
    assert zones["telegram"] == "bottom_left"


def test_volume_commands():
    plan = CommandParser().parse("set volume to 40")
    assert plan is not None
    assert plan.steps[0].action == "set_volume"
    assert plan.steps[0].params["level"] == 40

    plan2 = CommandParser().parse("volume up")
    assert plan2.steps[0].action == "adjust_volume"


def test_audio_device_command():
    plan = CommandParser().parse("switch audio to earbuds")
    assert plan is not None
    assert plan.steps[0].action == "set_audio_device"


def test_zones_list():
    assert "top_left" in list_zones()
    assert "bottom_right" in list_zones()
