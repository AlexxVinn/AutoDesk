"""Faster-Whisper transcription wrapper."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


class WhisperTranscriber:
    def __init__(
        self,
        model_size: str = "base.en",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        self._model = None
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type

    def _ensure_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            logger.info("Loading Whisper model %s", self._model_size)
            self._model = WhisperModel(
                self._model_size,
                device=self._device,
                compute_type=self._compute_type,
            )

    def transcribe_audio(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        self._ensure_model()
        audio = np.asarray(audio, dtype=np.float32)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        peak = np.max(np.abs(audio)) if audio.size else 0.0
        if peak > 0:
            audio = audio / peak

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            path = Path(tmp.name)
        try:
            import wave

            pcm = (audio * 32767).astype(np.int16)
            with wave.open(str(path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(pcm.tobytes())

            segments, _info = self._model.transcribe(
                str(path),
                language="en",
                vad_filter=True,
                beam_size=1,
                best_of=1,
            )
            text = " ".join(seg.text.strip() for seg in segments).strip()
            return text
        finally:
            path.unlink(missing_ok=True)

    def transcribe_file(self, file_path: str) -> str:
        self._ensure_model()
        segments, _ = self._model.transcribe(file_path, language="en", vad_filter=True)
        return " ".join(seg.text.strip() for seg in segments).strip()
