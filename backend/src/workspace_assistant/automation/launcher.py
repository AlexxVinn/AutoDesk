"""Deterministic app and URL launching."""

from __future__ import annotations

import logging
import subprocess
import sys
import webbrowser
from typing import Any

from workspace_assistant.config import expand_path, get_config

logger = logging.getLogger(__name__)


class AppLauncher:
    def __init__(self) -> None:
        self._config = get_config()

    def get_app(self, app_id: str) -> dict[str, Any] | None:
        return self._config.apps.get(app_id)

    def launch_app(self, app_id: str, profile: str | None = None, args: list[str] | None = None) -> bool:
        app = self.get_app(app_id)
        if not app:
            logger.warning("Unknown app_id: %s", app_id)
            return False

        if app.get("url"):
            return self.open_url(app["url"])

        platform_key = "windows" if sys.platform == "win32" else "linux"
        plat = app.get(platform_key) or app.get("windows") or {}
        launch_cmd = plat.get("launch")
        if not launch_cmd:
            exe = plat.get("exe")
            if exe:
                launch_cmd = [expand_path(exe)]
            else:
                logger.warning("No launch config for app %s", app_id)
                return False

        cmd = [expand_path(str(c)) for c in launch_cmd]
        if profile:
            profiles = app.get("profiles", {})
            cmd.extend(profiles.get(profile, []))
        if args:
            cmd.extend(args)

        try:
            subprocess.Popen(cmd, shell=False)  # noqa: S603
            logger.info("Launched %s: %s", app_id, cmd)
            return True
        except OSError as exc:
            logger.error("Launch failed %s: %s", app_id, exc)
            return False

    def open_url(self, url: str) -> bool:
        try:
            webbrowser.open(url)
            return True
        except Exception as exc:
            logger.error("open_url failed: %s", exc)
            return False

    def open_url_for_app(self, app_id: str, query: str | None = None) -> bool:
        app = self.get_app(app_id)
        if not app:
            return False
        url = app.get("url")
        template = app.get("url_template")
        if template and query:
            from urllib.parse import quote_plus

            url = template.format(query=quote_plus(query))
        if url:
            return self.open_url(url)
        return False

    def open_folder(self, path: str) -> bool:
        path = expand_path(path)
        if sys.platform == "win32":
            subprocess.Popen(["explorer", path], shell=False)  # noqa: S603
            return True
        if sys.platform == "darwin":
            subprocess.Popen(["open", path], shell=False)  # noqa: S603
            return True
        subprocess.Popen(["xdg-open", path], shell=False)  # noqa: S603
        return True

    def open_project(self, project_id: str) -> bool:
        project = self._config.projects.get(project_id)
        if not project:
            logger.warning("Unknown project: %s", project_id)
            return False
        path = expand_path(project["path"])
        cursor_args = project.get("cursor_args")
        if cursor_args:
            args = [expand_path(a) for a in cursor_args]
            return self.launch_app("cursor", args=args)
        return self.open_folder(path)
