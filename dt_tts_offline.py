"""
Offline TTS via Windows SAPI.

Uses win32com SpFileStream when available (reliable WAV export),
with pyttsx3 as a fallback helper for voice discovery.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Final

import dt_tts_edge as tts_edge
import dt_utility as utility

VERSION: Final[str] = "1.1.0"

ROOT_DIR: Final[Path] = Path(__file__).resolve().parent
TTS_DIR: Final[Path] = ROOT_DIR / "temp" / "tts"

DEFAULT_RATE: Final[int] = 0  # SAPI relative rate (-10..10)
DEFAULT_VOLUME: Final[int] = 100


def _require_win32com():
    try:
        import win32com.client  # noqa: F401
    except Exception as exception:
        raise RuntimeError(
            "بسته pywin32 برای TTS آفلاین لازم است. "
            "لطفا اجرا کنید: pip install pyttsx3 pywin32"
        ) from exception


def list_system_voices() -> list[dict]:
    """
    Return installed SAPI voices.

    Each item: id, name, languages
    """

    _require_win32com()
    import win32com.client

    voice = win32com.client.Dispatch("SAPI.SpVoice")
    voices = []
    try:
        tokens = voice.GetVoices()
        for index in range(int(tokens.Count)):
            token = tokens.Item(index)
            voice_id = str(token.Id)
            name = str(token.GetDescription())
            try:
                language = str(token.GetAttribute("Language"))
            except Exception:
                language = ""
            voices.append(
                {
                    "id": voice_id,
                    "name": name,
                    "languages": language,
                }
            )
    except Exception as exception:
        raise RuntimeError(
            "خواندن صداهای ویندوز ناموفق بود. "
            f"({exception})"
        ) from exception
    return voices


def find_best_offline_voice_id(preferred: str = "") -> str:
    """Prefer an explicit voice id, else a Persian-looking voice, else first voice."""

    voices = list_system_voices()
    if not voices:
        raise RuntimeError(
            "هیچ صدای سیستمی برای TTS آفلاین پیدا نشد. "
            "در تنظیمات ویندوز یک Voice فارسی/انگلیسی نصب کنید."
        )

    preferred = (preferred or "").strip()
    if preferred:
        for item in voices:
            if item["id"] == preferred or preferred.lower() in item["name"].lower():
                return item["id"]

    for item in voices:
        blob = f"{item['id']} {item['name']} {item['languages']}".lower()
        if any(token in blob for token in ("fa-ir", "persian", "farsi", "iran", "فارسی")):
            return item["id"]

    return voices[0]["id"]


def _contains_persian(text: str) -> bool:
    return any("\u0600" <= ch <= "\u06FF" for ch in text)


def has_persian_system_voice() -> bool:
    """Return True when an installed SAPI voice looks Persian."""

    for item in list_system_voices():
        blob = f"{item['id']} {item['name']} {item['languages']}".lower()
        if any(token in blob for token in ("fa-ir", "persian", "farsi", "iran", "فارسی")):
            return True
    return False


def convert_text_to_speech(
    text: str,
    audio_file_path: str,
    voice: str = "",
    rate: int = DEFAULT_RATE,
    volume: int = DEFAULT_VOLUME,
) -> tuple[int, float]:
    """Convert text to speech offline and save a WAV file via SAPI."""

    _require_win32com()
    import win32com.client

    text = tts_edge.fix_text_for_speech(text=text)
    if not text:
        raise RuntimeError("متنی برای خواندن وجود ندارد.")

    voice_id = find_best_offline_voice_id(preferred=voice)
    if _contains_persian(text=text) and not has_persian_system_voice():
        raise RuntimeError(
            "روی این ویندوز صدای فارسی نصب نیست؛ TTS آفلاین نمی‌تواند فارسی را درست بخواند. "
            "موتور TTS را روی Edge بگذارید، یا Voice فارسی ویندوز را نصب کنید."
        )
    word_count = utility.get_word_count(text=text)
    start_time = time.perf_counter()

    target = Path(audio_file_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()

    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    stream = win32com.client.Dispatch("SAPI.SpFileStream")

    try:
        # 3 = SSFMCreateForWrite
        stream.Open(str(target), 3)
        speaker.AudioOutputStream = stream
        speaker.Rate = int(rate)
        speaker.Volume = int(volume)

        tokens = speaker.GetVoices()
        selected_name = ""
        for index in range(int(tokens.Count)):
            token = tokens.Item(index)
            if str(token.Id) == voice_id:
                speaker.Voice = token
                selected_name = str(token.GetDescription())
                break

        speaker.Speak(text)
    except Exception as exception:
        raise RuntimeError(
            "ساخت صدا با TTS آفلاین ناموفق بود. "
            f"({exception})"
        ) from exception
    finally:
        try:
            stream.Close()
        except Exception:
            pass

    size = target.stat().st_size if target.exists() else 0
    if size < 1000:
        if target.exists():
            try:
                target.unlink()
            except Exception:
                pass
        if _contains_persian(text=text):
            raise RuntimeError(
                "TTS آفلاین نتوانست متن فارسی را بخواند. "
                f"صدای فعلی سیستم «{selected_name or 'نامشخص'}» فارسی نیست. "
                "یا Voice فارسی ویندوز نصب کنید، یا موتور TTS را روی Edge بگذارید."
            )
        raise RuntimeError(
            "فایل صدای آفلاین ساخته نشد یا خیلی کوتاه بود. "
            "صدای Speech ویندوز را بررسی کنید."
        )

    elapsed_time = time.perf_counter() - start_time
    return word_count, elapsed_time


def synthesize_persian(
    text: str,
    voice: str = "",
    max_chars: int = tts_edge.MAX_SPEECH_CHARS,
) -> tuple[str, int, float, bool]:
    """
    Create a Persian WAV with offline SAPI TTS.

    Returns:
        audio path, word count, elapsed seconds, truncated flag
    """

    speech_text, truncated = tts_edge.clean_text_for_speech(
        text=text,
        max_chars=max_chars,
    )
    TTS_DIR.mkdir(parents=True, exist_ok=True)
    audio_path = TTS_DIR / f"reply_offline_{utility.get_formated_now(with_miliseconds=True)}.wav"
    word_count, elapsed_time = convert_text_to_speech(
        text=speech_text,
        audio_file_path=str(audio_path),
        voice=voice,
    )
    return str(audio_path), word_count, elapsed_time, truncated


if __name__ == "__main__":
    utility.display_just_one_error_message(
        message=utility.ERROR_MESSAGE_MODULE_IS_NOT_EXECUTED_DIRECTLY,
    )
