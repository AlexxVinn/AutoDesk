"""Configuration loading and path resolution."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


def _find_config_root() -> Path:
    env = os.environ.get("WORKSPACE_ASSISTANT_CONFIG")
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    cwd = Path.cwd()
    for candidate in (cwd, cwd.parent, cwd.parent.parent):
        if (candidate / "config" / "settings.json").exists():
            return candidate / "config"
    return Path(__file__).resolve().parents[3] / "config"


def expand_path(value: str) -> str:
    return os.path.expandvars(os.path.expanduser(value))


class VoiceSettings(BaseModel):
    enabled: bool = True
    always_listen: bool = True
    wake_word_enabled: bool = False
    wake_word: str = "hey desk"
    sample_rate: int = 16000
    chunk_seconds: float = 2.0
    silence_threshold: float = 0.012
    min_speech_seconds: float = 0.4
    whisper_model: str = "base.en"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"


class ParserSettings(BaseModel):
    mode: str = "hybrid"
    llm_enabled: bool = False
    provider: str = "openai"
    base_url: str | None = None
    llm_model: str = "gpt-4o-mini"
    openai_api_key_env: str = "OPENAI_API_KEY"
    api_key_env: str | None = None
    use_openai_sdk: bool = True


class PathsSettings(BaseModel):
    config_dir: str = "config"
    presets_file: str = "config/presets.json"
    apps_file: str = "config/apps.json"


class AppSettings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 9477
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
    parser: ParserSettings = Field(default_factory=ParserSettings)
    feedback: dict[str, Any] = Field(default_factory=dict)
    paths: PathsSettings = Field(default_factory=PathsSettings)

    model_config = {"extra": "allow"}


class ConfigStore:
    """Loads JSON config files from the project config directory."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or _find_config_root()
        self.project_root = self.root.parent
        self.settings = self._load_settings()
        self.apps = self._load_json("apps.json", fallback={})
        self.presets = self._load_json("presets.json", fallback={})
        self.projects = self._load_json("projects.json", fallback={})
        self.layouts = self._load_json("layouts.json", fallback={})
        self.audio = self._load_json("audio.json", fallback={})

    def _load_settings(self) -> AppSettings:
        path = self.root / "settings.json"
        if not path.exists():
            return AppSettings()
        data = json.loads(path.read_text(encoding="utf-8"))
        return AppSettings(**data)

    def _load_json(self, name: str, fallback: dict) -> dict:
        path = self.root / name
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))

    def resolve(self, relative: str) -> Path:
        p = Path(relative)
        if p.is_absolute():
            return p
        return self.project_root / relative

    def save_settings(self) -> None:
        path = self.root / "settings.json"
        path.write_text(
            json.dumps(self.settings.model_dump(), indent=2),
            encoding="utf-8",
        )


_store: ConfigStore | None = None


def get_config() -> ConfigStore:
    global _store
    if _store is None:
        _store = ConfigStore()
    return _store
