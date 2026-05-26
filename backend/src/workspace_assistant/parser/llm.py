"""LLM command parser — OpenAI, Ollama, or any OpenAI-compatible local server."""

from __future__ import annotations

import json
import logging
import os
import re

import httpx

from workspace_assistant.config import get_config
from workspace_assistant.executor.actions import ActionStep, CommandPlan
from workspace_assistant.parser.prompt import build_system_prompt

logger = logging.getLogger(__name__)


class LLMParser:
    """Maps natural language → CommandPlan. Does NOT execute anything."""

    def __init__(self) -> None:
        self._settings = get_config().settings.parser
        self._client = None

    @property
    def available(self) -> bool:
        if not self._settings.llm_enabled:
            return False
        provider = self._provider()
        if provider in ("ollama", "openai_compatible", "local"):
            return bool(self._base_url())
        return bool(os.environ.get(self._settings.openai_api_key_env, "").strip())

    def _provider(self) -> str:
        return getattr(self._settings, "provider", "openai") or "openai"

    def _base_url(self) -> str | None:
        url = getattr(self._settings, "base_url", None)
        if url:
            return url.rstrip("/")
        if self._provider() in ("ollama", "local"):
            return "http://127.0.0.1:11434/v1"
        return None

    def _api_key(self) -> str:
        env_name = getattr(self._settings, "api_key_env", None) or self._settings.openai_api_key_env
        key = os.environ.get(env_name, "").strip()
        if key:
            return key
        if self._provider() in ("ollama", "openai_compatible", "local"):
            return "ollama"
        return ""

    def _model(self) -> str:
        return self._settings.llm_model

    def _get_openai_client(self):
        if self._client is None:
            from openai import OpenAI

            kwargs: dict = {}
            base = self._base_url()
            if base:
                kwargs["base_url"] = base
            key = self._api_key()
            if key:
                kwargs["api_key"] = key
            self._client = OpenAI(**kwargs)
        return self._client

    def parse(self, text: str) -> CommandPlan | None:
        if not self.available:
            return None
        try:
            if self._provider() == "ollama" and not getattr(self._settings, "use_openai_sdk", True):
                raw = self._parse_via_ollama_native(text)
            else:
                raw = self._parse_via_openai_compatible(text)
            data = json.loads(raw)
            steps = [ActionStep(**s) for s in data.get("steps", [])]
            if not steps:
                return None
            return CommandPlan(
                source_text=text,
                steps=steps,
                parser=f"llm:{self._provider()}",
                confidence=0.8,
            )
        except Exception as exc:
            logger.error("LLM parse failed (%s): %s", self._provider(), exc)
            return None

    def _parse_via_openai_compatible(self, text: str) -> str:
        client = self._get_openai_client()
        kwargs: dict = {
            "model": self._model(),
            "temperature": 0,
            "messages": [
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": text},
            ],
        }
        # Local models often lack json_schema; ask clearly + extract JSON
        if self._provider() == "openai" and not self._base_url():
            kwargs["response_format"] = {"type": "json_object"}
        response = client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or "{}"
        return _extract_json(content)

    def _parse_via_ollama_native(self, text: str) -> str:
        base = self._base_url() or "http://127.0.0.1:11434"
        host = base.replace("/v1", "")
        payload = {
            "model": self._model(),
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": text},
            ],
            "options": {"temperature": 0},
        }
        with httpx.Client(timeout=60.0) as client:
            r = client.post(f"{host}/api/chat", json=payload)
            r.raise_for_status()
            content = r.json().get("message", {}).get("content", "{}")
        return _extract_json(content)


def _extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("{"):
        return text
    match = re.search(r"\{[\s\S]*\}", text)
    return match.group(0) if match else "{}"
