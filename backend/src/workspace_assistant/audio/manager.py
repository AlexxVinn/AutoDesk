"""System volume and output device control — Windows-first."""

from __future__ import annotations

import logging
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from workspace_assistant.config import get_config

logger = logging.getLogger(__name__)


@dataclass
class AudioDeviceInfo:
    id: str
    name: str


class AudioManager:
    def list_devices(self) -> list[AudioDeviceInfo]:
        if sys.platform == "win32":
            return self._list_devices_win()
        return [
            AudioDeviceInfo(id="stub-headset", name="Headset (stub)"),
            AudioDeviceInfo(id="stub-earbuds", name="Earbuds (stub)"),
        ]

    def list_output_devices(self) -> list[dict[str, str]]:
        return [{"id": d.id, "name": d.name} for d in self.list_devices()]

    def get_volume_percent(self) -> int | None:
        if sys.platform != "win32":
            return 50
        try:
            from comtypes import CLSCTX_ALL
            from ctypes import cast, POINTER
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            device = AudioUtilities.GetSpeakers()
            interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            scalar = volume.GetMasterVolumeLevelScalar(None)
            return int(round(scalar * 100))
        except Exception as exc:
            logger.error("get_volume failed: %s", exc)
            return None

    def set_volume_percent(self, level: int) -> bool:
        level = max(0, min(100, int(level)))
        if sys.platform != "win32":
            logger.info("stub set volume %s", level)
            return True
        try:
            from comtypes import CLSCTX_ALL
            from ctypes import cast, POINTER
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            device = AudioUtilities.GetSpeakers()
            interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            return True
        except Exception as exc:
            logger.error("set_volume failed: %s", exc)
            return False

    def adjust_volume(self, delta: int) -> bool:
        current = self.get_volume_percent()
        if current is None:
            return False
        return self.set_volume_percent(current + int(delta))

    def set_mute(self, muted: bool) -> bool:
        if sys.platform != "win32":
            logger.info("stub mute=%s", muted)
            return True
        try:
            from comtypes import CLSCTX_ALL
            from ctypes import cast, POINTER
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            device = AudioUtilities.GetSpeakers()
            interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(1 if muted else 0, None)
            return True
        except Exception as exc:
            logger.error("mute failed: %s", exc)
            return False

    def resolve_device_alias(self, alias: str) -> str | None:
        cfg = get_config().audio
        key = alias.strip().lower()
        aliases = cfg.get("aliases", {})
        if key in aliases:
            key = aliases[key]
        devices_cfg = cfg.get("devices", {})
        if key in devices_cfg:
            return key
        return None

    def set_output_device(self, alias: str) -> bool:
        device_key = self.resolve_device_alias(alias)
        if not device_key:
            logger.warning("Unknown audio device alias: %s", alias)
            return False
        if sys.platform != "win32":
            logger.info("stub audio device %s", device_key)
            return True
        device_cfg = get_config().audio.get("devices", {}).get(device_key, {})
        patterns = device_cfg.get("match", [device_key])
        device = self._find_device_by_patterns(patterns)
        if not device:
            logger.warning("No playback device matched %s", patterns)
            return False
        return self._set_default_device_win(device.id)

    def _find_device_by_patterns(self, patterns: list[str]) -> AudioDeviceInfo | None:
        compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
        for dev in self._list_devices_win():
            if any(c.search(dev.name) for c in compiled):
                return dev
        return None

    def _list_devices_win(self) -> list[AudioDeviceInfo]:
        try:
            from pycaw.pycaw import AudioUtilities

            result: list[AudioDeviceInfo] = []
            for dev in AudioUtilities.GetAllDevices():
                state = getattr(dev, "state", 1)
                if state != 1:
                    continue
                flow = getattr(dev, "flow", 1)
                if flow != 1:
                    continue
                name = getattr(dev, "FriendlyName", None) or str(dev)
                dev_id = getattr(dev, "id", name)
                result.append(AudioDeviceInfo(id=dev_id, name=name))
            return result
        except Exception as exc:
            logger.error("list_devices failed: %s", exc)
            return []

    def _set_default_device_win(self, device_id: str) -> bool:
        script = Path(__file__).resolve().parents[4] / "scripts" / "switch-audio-device.ps1"
        if not script.exists():
            script = get_config().project_root / "scripts" / "switch-audio-device.ps1"
        try:
            proc = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script),
                    "-DeviceId",
                    device_id,
                ],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            if proc.returncode == 0:
                logger.info("Switched audio device")
                return True
            logger.error("switch-audio failed: %s", proc.stderr)
        except Exception as exc:
            logger.error("switch-audio subprocess: %s", exc)
        return False


_manager: AudioManager | None = None


def get_audio_manager() -> AudioManager:
    global _manager
    if _manager is None:
        _manager = AudioManager()
    return _manager
