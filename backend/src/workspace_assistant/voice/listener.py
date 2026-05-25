"""Always-on voice listener with optional wake word filtering."""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from workspace_assistant.config import VoiceSettings

from .transcribe import WhisperTranscriber

logger = logging.getLogger(__name__)


@dataclass
class VoiceEvent:
    text: str
    raw_text: str
    wake_stripped: bool


class VoiceListener:
    def __init__(
        self,
        settings: VoiceSettings,
        on_transcript: Callable[[VoiceEvent], None],
        on_status: Callable[[str], None] | None = None,
    ) -> None:
        self._settings = settings
        self._on_transcript = on_transcript
        self._on_status = on_status or (lambda _s: None)
        self._transcriber = WhisperTranscriber(
            model_size=settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="voice-listener", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)

    def _run(self) -> None:
        try:
            import sounddevice as sd
        except ImportError:
            self._on_status("error: sounddevice not installed")
            logger.error("sounddevice required for voice input")
            return

        sr = self._settings.sample_rate
        block = int(sr * self._settings.chunk_seconds)
        self._on_status("listening")

        buffer: list[np.ndarray] = []
        silent_chunks = 0

        with sd.InputStream(samplerate=sr, channels=1, dtype="float32", blocksize=block):
            while not self._stop.is_set():
                try:
                    data, _overflowed = sd.read(block)
                except Exception as exc:
                    logger.error("Audio read error: %s", exc)
                    time.sleep(0.5)
                    continue

                chunk = data[:, 0]
                rms = float(np.sqrt(np.mean(chunk**2)))
                if rms >= self._settings.silence_threshold:
                    buffer.append(chunk.copy())
                    silent_chunks = 0
                else:
                    silent_chunks += 1
                    if buffer and silent_chunks >= 1:
                        self._process_utterance(np.concatenate(buffer), sr)
                        buffer.clear()
                        silent_chunks = 0

    def _process_utterance(self, audio: np.ndarray, sample_rate: int) -> None:
        duration = len(audio) / sample_rate
        if duration < self._settings.min_speech_seconds:
            return
        self._on_status("transcribing")
        try:
            text = self._transcriber.transcribe_audio(audio, sample_rate)
        except Exception as exc:
            logger.error("Transcription failed: %s", exc)
            self._on_status("listen_error")
            return
        if not text:
            self._on_status("listening")
            return

        event = self._apply_wake_word(text)
        if event is None:
            self._on_status("listening")
            return
        self._on_transcript(event)
        self._on_status("listening")

    def _apply_wake_word(self, text: str) -> VoiceEvent | None:
        raw = text.strip()
        if not self._settings.wake_word_enabled:
            return VoiceEvent(text=raw.lower(), raw_text=raw, wake_stripped=False)

        wake = self._settings.wake_word.lower()
        lower = raw.lower()
        if lower.startswith(wake):
            stripped = raw[len(wake) :].strip(" ,.!")
            if not stripped:
                return None
            return VoiceEvent(text=stripped.lower(), raw_text=raw, wake_stripped=True)
        return None
