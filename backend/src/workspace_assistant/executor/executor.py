"""Deterministic action executor — no AI in this layer."""

from __future__ import annotations

import logging
import time
from typing import Any

from workspace_assistant.automation import AppLauncher, KeyboardAutomation
from workspace_assistant.config import get_config
from workspace_assistant.presets import PresetManager
from workspace_assistant.windows import get_window_manager

from .actions import ActionStep, CommandPlan

logger = logging.getLogger(__name__)


class ActionExecutor:
    def __init__(self) -> None:
        self._launcher = AppLauncher()
        self._keyboard = KeyboardAutomation()
        self._windows = get_window_manager()
        self._presets = PresetManager()
        self._config = get_config()
        self._running_preset: set[str] = set()

    def execute_plan(self, plan: CommandPlan) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        for step in plan.steps:
            ok, detail = self.execute_step(step)
            results.append({"action": step.action, "ok": ok, "detail": detail})
            time.sleep(0.15)
        success = all(r["ok"] for r in results) if results else False
        return {
            "success": success,
            "steps": results,
            "source": plan.source_text,
            "parser": plan.parser,
        }

    def execute_step(self, step: ActionStep) -> tuple[bool, str]:
        action = step.action
        params = step.params
        handlers = {
            "launch_app": self._launch_app,
            "focus_app": self._focus_app,
            "open_url": self._open_url,
            "open_folder": self._open_folder,
            "open_project": self._open_project,
            "snap_window": self._snap_window,
            "snap_layout": self._snap_layout,
            "maximize": self._maximize,
            "minimize": self._minimize,
            "close_apps": self._close_apps,
            "hotkey": self._hotkey,
            "run_preset": self._run_preset,
            "search_google": self._search_google,
            "focus_window": self._focus_window,
            "move_monitor": self._move_monitor,
        }
        handler = handlers.get(action)
        if not handler:
            return False, f"unknown action: {action}"
        try:
            return handler(params)
        except Exception as exc:
            logger.exception("Step failed: %s", action)
            return False, str(exc)

    def _app_patterns(self, app_id: str) -> list[str]:
        app = self._config.apps.get(app_id, {})
        plat = app.get("windows", app)
        return plat.get("title_patterns", [app.get("name", app_id)])

    def _launch_app(self, params: dict) -> tuple[bool, str]:
        ok = self._launcher.launch_app(
            params["app_id"],
            profile=params.get("profile"),
            args=params.get("args"),
        )
        return ok, f"launch {params['app_id']}"

    def _focus_app(self, params: dict) -> tuple[bool, str]:
        patterns = self._app_patterns(params["app_id"])
        ok = self._windows.focus_app(patterns)
        return ok, f"focus {params['app_id']}"

    def _open_url(self, params: dict) -> tuple[bool, str]:
        if "url" in params:
            ok = self._launcher.open_url(params["url"])
        else:
            ok = self._launcher.open_url_for_app(params.get("app_id", "chatgpt"))
        return ok, "open_url"

    def _open_folder(self, params: dict) -> tuple[bool, str]:
        if "project_id" in params:
            return self._open_project({"project_id": params["project_id"]})
        path = params.get("path", "")
        ok = self._launcher.open_folder(path)
        return ok, f"folder {path}"

    def _open_project(self, params: dict) -> tuple[bool, str]:
        ok = self._launcher.open_project(params["project_id"])
        return ok, f"project {params['project_id']}"

    def _snap_window(self, params: dict) -> tuple[bool, str]:
        patterns = self._app_patterns(params["app_id"])
        win = self._windows.find_by_title_patterns(patterns)
        if not win:
            return False, "window not found"
        layout = params.get("side", "left")
        ok = self._windows.snap(win.hwnd, layout)
        return ok, f"snap {layout}"

    def _snap_layout(self, params: dict) -> tuple[bool, str]:
        left = self._app_patterns(params.get("left", "cursor"))
        right = self._app_patterns(params.get("right", "chrome"))
        ok = self._windows.apply_split_lr(left, right)
        return ok, "split_lr"

    def _maximize(self, params: dict) -> tuple[bool, str]:
        patterns = self._app_patterns(params["app_id"])
        win = self._windows.find_by_title_patterns(patterns)
        if not win:
            return False, "not found"
        return self._windows.snap(win.hwnd, "maximize"), "maximize"

    def _minimize(self, params: dict) -> tuple[bool, str]:
        patterns = self._app_patterns(params["app_id"])
        win = self._windows.find_by_title_patterns(patterns)
        if not win:
            return False, "not found"
        return self._windows.snap(win.hwnd, "minimize"), "minimize"

    def _close_apps(self, params: dict) -> tuple[bool, str]:
        ok_all = True
        for app_id in params.get("app_ids", []):
            win = self._windows.find_by_title_patterns(self._app_patterns(app_id))
            if win:
                ok_all = self._windows.close(win.hwnd) and ok_all
        return ok_all, "close_apps"

    def _hotkey(self, params: dict) -> tuple[bool, str]:
        keys = params.get("keys", [])
        ok = self._keyboard.send_hotkey(*keys)
        return ok, "hotkey"

    def _run_preset(self, params: dict) -> tuple[bool, str]:
        preset_id = params["preset_id"]
        if preset_id in self._running_preset:
            return False, "preset recursion blocked"
        self._running_preset.add(preset_id)
        try:
            steps = self._presets.steps_for_preset(preset_id)
            plan = CommandPlan(source_text=f"preset:{preset_id}", steps=steps, parser="preset")
            result = self.execute_plan(plan)
            return result["success"], f"preset {preset_id}"
        finally:
            self._running_preset.discard(preset_id)

    def _search_google(self, params: dict) -> tuple[bool, str]:
        query = params.get("query", "")
        ok = self._launcher.open_url_for_app("google", query=query)
        return ok, f"search {query}"

    def _focus_window(self, params: dict) -> tuple[bool, str]:
        title = params.get("title", "")
        win = self._windows.find_by_title_patterns([title])
        if win:
            return self._windows.focus(win.hwnd), "focused"
        return False, "not found"

    def _move_monitor(self, params: dict) -> tuple[bool, str]:
        patterns = self._app_patterns(params["app_id"])
        win = self._windows.find_by_title_patterns(patterns)
        if not win:
            return False, "not found"
        idx = int(params.get("monitor", 0))
        return self._windows.move_to_monitor(win.hwnd, idx), f"monitor {idx}"
