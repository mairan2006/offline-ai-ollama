"""
TTS router: Edge (online) or offline Windows SAPI.
"""

from __future__ import annotations

from typing import Final

import dt_tts_edge as tts_edge
import dt_tts_offline as tts_offline
import dt_utility as utility

VERSION: Final[str] = "1.0.0"

ENGINE_EDGE: Final[str] = "edge"
ENGINE_OFFLINE: Final[str] = "offline"

ENGINE_OPTIONS: Final[list[str]] = [
    ENGINE_EDGE,
    ENGINE_OFFLINE,
]


def normalize_engine(engine: str) -> str:
    value = (engine or ENGINE_EDGE).replace(" ", "").lower()
    if value in ENGINE_OPTIONS:
        return value
    return ENGINE_EDGE


def synthesize_persian(
    text: str,
    engine: str = ENGINE_EDGE,
    voice: str = "",
    max_chars: int = tts_edge.MAX_SPEECH_CHARS,
) -> tuple[str, int, float, bool, str]:
    """
    Create speech audio for Persian text.

    Returns:
        audio_path, word_count, elapsed_seconds, truncated, mime_type
    """

    selected = normalize_engine(engine=engine)
    if selected == ENGINE_OFFLINE:
        audio_path, word_count, elapsed, truncated = tts_offline.synthesize_persian(
            text=text,
            voice=voice,
            max_chars=max_chars,
        )
        return audio_path, word_count, elapsed, truncated, "audio/wav"

    edge_voice = voice or tts_edge.VOICES_FEMALE[0]
    audio_path, word_count, elapsed, truncated = tts_edge.synthesize_persian(
        text=text,
        voice=edge_voice,
        max_chars=max_chars,
    )
    return audio_path, word_count, elapsed, truncated, "audio/mpeg"


def list_offline_voices() -> list[dict]:
    """Proxy to offline voice listing."""

    return tts_offline.list_system_voices()


def has_persian_offline_voice() -> bool:
    """Return True when offline Persian voice seems available."""

    return tts_offline.has_persian_system_voice()


if __name__ == "__main__":
    utility.display_just_one_error_message(
        message=utility.ERROR_MESSAGE_MODULE_IS_NOT_EXECUTED_DIRECTLY,
    )
