"""Structured action models — deterministic execution contract."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ActionStep(BaseModel):
    action: str
    params: dict[str, Any] = Field(default_factory=dict)


class CommandPlan(BaseModel):
    """Result of parsing — ordered deterministic steps."""

    source_text: str = ""
    steps: list[ActionStep] = Field(default_factory=list)
    confidence: float = 1.0
    parser: str = "rules"
