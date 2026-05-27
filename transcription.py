"""Audio transcription using OpenAI Whisper."""

import threading
from pathlib import Path

from config import WHISPER_MODEL

_whisper_model = None
_model_lock = threading.Lock()


class TranscriptionError(Exception):
    """Raised when audio cannot be transcribed."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def _load_model():
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model

    with _model_lock:
        if _whisper_model is not None:
            return _whisper_model
        try:
            import whisper
        except ImportError as exc:
            raise TranscriptionError(
                "Whisper is not installed. Run: pip install openai-whisper"
            ) from exc

        try:
            _whisper_model = whisper.load_model(WHISPER_MODEL)
        except Exception as exc:
            raise TranscriptionError(
                f"Failed to load Whisper model '{WHISPER_MODEL}': {exc}"
            ) from exc
        return _whisper_model


def transcribe_audio(file_path: Path) -> str:
    """Transcribe an audio file to text."""
    try:
        model = _load_model()
        result = model.transcribe(str(file_path))
    except TranscriptionError:
        raise
    except Exception as exc:
        raise TranscriptionError(f"Transcription failed: {exc}") from exc

    text = (result.get("text") or "").strip()
    if not text:
        raise TranscriptionError(
            "No speech detected in the audio file. Try a clearer recording."
        )
    return text
