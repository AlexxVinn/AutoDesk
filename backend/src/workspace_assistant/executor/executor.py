"""Deterministic action executor — no AI in this layer."""

from __future__ import annotations

import logging
import time
from typing import Any

from workspace_assistant.automation import AppLauncher, ChatGPTAutomation, Clipboard, KeyboardAutomation
from workspace_assistant.automation.profiles import resolve_chrome_profile
from workspace_assistant.config import get_config
from workspace_assistant.presets import PresetManager
from workspace_assistant.windows import get_window_manager

from .actions import ActionStep, CommandPlan

logger = logging.getLogger(__name__)


class ActionExecutor:
    def __init__(self) -> None:
        self._launcher = AppLauncher()
        self._keyboard = KeyboardAutomation()
        self._chatgpt = ChatGPTAutomation()
        self._clipboard = Clipboard()
        self._windows = get_window_manager()
        self._presets = PresetManager()
        self._config = get_config()
        self._running_preset: set[str] = set()

    def execute_plan(self, plan: CommandPlan) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        for step in plan.steps:
            ok, detail = self.execute_step(step)
            results.append({"action": step.action, "ok": ok, "detail": detail})
            delay = step.params.get("delay_after", 0.15)
            if isinstance(delay, (int, float)):
                time.sleep(float(delay))
        success = all(r["ok"] for r in results) if results else False
        return {
            "success": success,
            "steps": results,
            "source": plan.source_text,
            "parser": plan.parser,
        }

    def execute_step(self, step: ActionStep) -> tuple[bool, str]:
        handlers = {
            "launch_app": self._launch_app,
            "open_app": self._open_app,
            "focus_app": self._focus_app,
            "open_url": self._open_url,
            "open_url_in_chrome": self._open_url_in_chrome,
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
            "wait": self._wait,
            "chatgpt_prompt": self._chatgpt_prompt,
            "copy_chatgpt": self._copy_chatgpt,
            "paste_to_app": self._paste_to_app,
            "copy_chatgpt_to_cursor": self._copy_chatgpt_to_cursor,
        }
        handler = handlers.get(step.action)
        if not handler:
            return False, f"unknown action: {step.action}"
        try:
            return handler(step.params)
        except Exception as exc:
            logger.exception("Step failed: %s", step.action)
            return False, str(exc)

    def _app_patterns(self, app_id: str) -> list[str]:
        app = self._config.apps.get(app_id, {})
        if app.get("title_patterns"):
            return list(app["title_patterns"])
        plat = app.get("windows", app)
        return plat.get("title_patterns", [app.get("name", app_id)])

    def _resolve_profile(self, params: dict) -> str | None:
        raw = params.get("profile")
        return resolve_chrome_profile(raw) if raw else None

    def _launch_app(self, params: dict) -> tuple[bool, str]:
        profile = self._resolve_profile(params)
        ok = self._launcher.launch_app(params["app_id"], profile=profile, args=params.get("args"))
        return ok, f"launch {params['app_id']}"

    def _open_app(self, params: dict) -> tuple[bool, str]:
        app_id = params["app_id"]
        patterns = self._app_patterns(app_id)
        win = self._windows.find_by_title_patterns(patterns)
        if not win:
            profile = self._resolve_profile(params)
            self._launcher.launch_app(app_id, profile=profile, args=params.get("args"))
            time.sleep(float(params.get("launch_wait", 1.2)))
        else:
            self._windows.focus(win.hwnd)

        win = self._windows.find_by_title_patterns(patterns)
        if win:
            self._windows.focus(win.hwnd)
            if params.get("fullscreen") or params.get("maximize"):
                self._windows.snap(win.hwnd, "maximize")
        return True, f"open {app_id}"

    def _focus_app(self, params: dict) -> tuple[bool, str]:
        patterns = self._app_patterns(params["app_id"])
        ok = self._windows.focus_app(patterns)
        return ok, f"focus {params['app_id']}"

    def _open_url(self, params: dict) -> tuple[bool, str]:
        profile = self._resolve_profile(params)
        if "url" in params:
            if params.get("browser") == "chrome" or profile:
                ok = self._launcher.open_url_in_chrome(params["url"], profile=profile)
            else:
                ok = self._launcher.open_url(params["url"])
        else:
            ok = self._launcher.open_url_for_app(
                params.get("app_id", "chatgpt"),
                query=params.get("query"),
                profile=profile or resolve_chrome_profile(
                    self._config.apps.get(params.get("app_id", ""), {}).get("chrome_profile")
                ),
            )
        return ok, "open_url"

    def _open_url_in_chrome(self, params: dict) -> tuple[bool, str]:
        profile = self._resolve_profile(params)
        if not profile and params.get("app_id"):
            app = self._config.apps.get(params["app_id"], {})
            profile = resolve_chrome_profile(app.get("chrome_profile"))
        if params.get("app_id") and not params.get("url"):
            return self._open_url({**params, "browser": "chrome"})
        url = params.get("url", "")
        ok = self._launcher.open_url_in_chrome(url, profile=profile)
        return ok, f"chrome url {url[:40]}"

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
        ok = self._windows.snap(win.hwnd, params.get("side", "left"))
        return ok, "snap"

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
        return self._keyboard.send_combo(list(keys)), "hotkey"

    def _wait(self, params: dict) -> tuple[bool, str]:
        time.sleep(float(params.get("seconds", 1.0)))
        return True, "wait"

    def _chatgpt_prompt(self, params: dict) -> tuple[bool, str]:
        text = params.get("text", "")
        patterns = None
        app = self._config.apps.get("chatgpt", {})
        if app.get("title_patterns"):
            patterns = app["title_patterns"]
        ok = self._chatgpt.send_prompt(text, title_patterns=patterns)
        return ok, "chatgpt_prompt"

    def _copy_chatgpt(self, params: dict) -> tuple[bool, str]:
        wait = float(params.get("wait_before_copy", 0.2))
        app = self._config.apps.get("chatgpt", {})
        patterns = app.get("title_patterns")
        ok = self._chatgpt.copy_last_response(title_patterns=patterns, wait_before_copy=wait)
        return ok, "copy_chatgpt"

    def _paste_to_app(self, params: dict) -> tuple[bool, str]:
        app_id = params.get("app_id", "cursor")
        patterns = self._app_patterns(app_id)
        win = self._windows.find_by_title_patterns(patterns)
        if not win:
            self._launcher.launch_app(app_id)
            time.sleep(1.0)
            win = self._windows.find_by_title_patterns(patterns)
        if win:
            self._windows.focus(win.hwnd)
        time.sleep(0.15)
        ok = self._keyboard.send_combo(["ctrl", "v"])
        return ok, f"paste {app_id}"

    def _copy_chatgpt_to_cursor(self, params: dict) -> tuple[bool, str]:
        ok1, _ = self._copy_chatgpt(params)
        time.sleep(0.2)
        ok2, _ = self._paste_to_app({"app_id": "cursor"})
        return ok1 and ok2, "chatgpt_to_cursor"

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
        profile = self._resolve_profile(params)
        ok = self._launcher.open_url_for_app("google", query=params.get("query", ""), profile=profile)
        return ok, "search"

    def _focus_window(self, params: dict) -> tuple[bool, str]:
        win = self._windows.find_by_title_patterns([params.get("title", "")])
        if win:
            return self._windows.focus(win.hwnd), "focused"
        return False, "not found"

    def _move_monitor(self, params: dict) -> tuple[bool, str]:
        win = self._windows.find_by_title_patterns(self._app_patterns(params["app_id"]))
        if not win:
            return False, "not found"
        return self._windows.move_to_monitor(win.hwnd, int(params.get("monitor", 0))), "move"
