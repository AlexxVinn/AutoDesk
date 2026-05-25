import os

os.environ.setdefault("WORKSPACE_ASSISTANT_CONFIG", os.path.join(os.path.dirname(__file__), "../../config"))

from workspace_assistant.parser.llm import LLMParser, _extract_json
from workspace_assistant.parser.prompt import build_system_prompt


def test_extract_json_from_markdown():
    raw = 'Here is the plan:\n```json\n{"steps":[{"action":"focus_app","params":{"app_id":"cursor"}}]}\n```'
    assert "focus_app" in _extract_json(raw)


def test_build_system_prompt_includes_apps():
    prompt = build_system_prompt()
    assert "cursor" in prompt
    assert "apply_layout" in prompt
    assert "telegram" in prompt


def test_ollama_parser_available_when_enabled(monkeypatch):
    monkeypatch.setenv("WORKSPACE_ASSISTANT_CONFIG", os.path.join(os.path.dirname(__file__), "../../config"))
    from workspace_assistant.config import get_config

    get_config.cache_clear = lambda: None  # type: ignore
    import workspace_assistant.config as cfg_mod

    cfg_mod._store = None
    store = cfg_mod.get_config()
    store.settings.parser.llm_enabled = True
    store.settings.parser.provider = "ollama"
    store.settings.parser.base_url = "http://127.0.0.1:11434/v1"

    parser = LLMParser()
    parser._settings = store.settings.parser
    assert parser.available is True
