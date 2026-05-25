"""FastAPI HTTP + WebSocket routes."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from workspace_assistant.config import get_config
from workspace_assistant.executor import ActionExecutor, CommandPlan
from workspace_assistant.parser import CommandParser
from workspace_assistant.presets import PresetManager
from workspace_assistant.voice import VoiceEvent, VoiceListener
from workspace_assistant.windows import get_window_manager

logger = logging.getLogger(__name__)

router = APIRouter()
_executor = ActionExecutor()
_parser = CommandParser()
_presets = PresetManager()

_voice_listener: VoiceListener | None = None
_ws_clients: list[WebSocket] = []
_main_loop: asyncio.AbstractEventLoop | None = None


class CommandRequest(BaseModel):
    text: str


class CommandResponse(BaseModel):
    success: bool
    plan: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    error: str | None = None


class VoiceToggleRequest(BaseModel):
    enabled: bool


def _set_main_loop(loop: asyncio.AbstractEventLoop) -> None:
    global _main_loop
    _main_loop = loop


def _schedule(coro) -> None:
    if _main_loop and _main_loop.is_running():
        asyncio.run_coroutine_threadsafe(coro, _main_loop)


def _broadcast_status_sync(status: str) -> None:
    _schedule(_broadcast({"type": "status", "status": status}))


def _schedule_broadcast_command(text: str) -> None:
    _schedule(_broadcast_command(text))


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@router.get("/presets")
def list_presets() -> list[dict[str, str]]:
    return _presets.list_presets()


@router.get("/windows")
def list_windows() -> list[dict[str, Any]]:
    wm = get_window_manager()
    return [
        {"hwnd": w.hwnd, "title": w.title, "rect": w.rect}
        for w in wm.list_windows()
    ]


@router.post("/command", response_model=CommandResponse)
def run_command(req: CommandRequest) -> CommandResponse:
    plan = _parser.parse(req.text)
    if not plan:
        return CommandResponse(success=False, error="Could not parse command")
    result = _executor.execute_plan(plan)
    return CommandResponse(
        success=result["success"],
        plan=plan.model_dump(),
        result=result,
    )


@router.post("/preset/{preset_id}")
def run_preset(preset_id: str) -> CommandResponse:
    steps = _presets.steps_for_preset(preset_id)
    if not steps:
        return CommandResponse(success=False, error=f"Unknown preset: {preset_id}")
    plan = CommandPlan(source_text=f"preset:{preset_id}", steps=steps, parser="preset")
    result = _executor.execute_plan(plan)
    return CommandResponse(success=result["success"], plan=plan.model_dump(), result=result)


@router.post("/voice/toggle")
def voice_toggle(req: VoiceToggleRequest) -> dict[str, Any]:
    global _voice_listener
    cfg = get_config().settings.voice
    if req.enabled:
        if _voice_listener is None:

            def on_transcript(event: VoiceEvent) -> None:
                _schedule_broadcast_command(event.text)

            _voice_listener = VoiceListener(
                cfg,
                on_transcript=on_transcript,
                on_status=_broadcast_status_sync,
            )
        _voice_listener.start()
        return {"listening": True}
    if _voice_listener:
        _voice_listener.stop()
    return {"listening": False}


async def _broadcast(payload: dict[str, Any]) -> None:
    dead: list[WebSocket] = []
    for ws in _ws_clients:
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in _ws_clients:
            _ws_clients.remove(ws)


async def _broadcast_command(text: str) -> None:
    plan = _parser.parse(text)
    payload: dict[str, Any] = {"type": "transcript", "text": text}
    if plan:
        result = _executor.execute_plan(plan)
        payload["plan"] = plan.model_dump()
        payload["result"] = result
        payload["success"] = result["success"]
    else:
        payload["success"] = False
        payload["error"] = "parse_failed"
    await _broadcast(payload)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    global _main_loop
    if _main_loop is None:
        _set_main_loop(asyncio.get_running_loop())

    await ws.accept()
    _ws_clients.append(ws)
    cfg = get_config()
    await ws.send_json({
        "type": "hello",
        "voice_enabled": cfg.settings.voice.enabled,
        "llm_enabled": cfg.settings.parser.llm_enabled,
    })
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")
            if msg_type == "command":
                text = data.get("text", "")
                plan = _parser.parse(text)
                if not plan:
                    await ws.send_json({"type": "result", "success": False, "error": "parse_failed"})
                    continue
                result = _executor.execute_plan(plan)
                await ws.send_json({
                    "type": "result",
                    "success": result["success"],
                    "plan": plan.model_dump(),
                    "result": result,
                })
            elif msg_type == "ping":
                await ws.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
    finally:
        if ws in _ws_clients:
            _ws_clients.remove(ws)
