"""
Dariush Tasdighi Custom 'edge-tts' Package Module
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Final

import dt_utility as utility

VERSION: Final[str] = "2.3.1"

RATE: Final[str] = "+5%"
PITCH: Final[str] = "-10Hz"
VOLUME: Final[str] = "+20%"

VOICES_MALE: Final[list[str]] = [
    "fa-IR-FaridNeural",
]

VOICES_FEMALE: Final[list[str]] = [
    "fa-IR-DilaraNeural",
]

MAX_SPEECH_CHARS: Final[int] = 900

ROOT_DIR: Final[Path] = Path(__file__).resolve().parent
TTS_DIR: Final[Path] = ROOT_DIR / "temp" / "tts"


def fix_text_for_speech(text: str) -> str:
    """Fix text for speech"""

    fixed_text: str = f" {text} "

    fixed_text = fixed_text.replace(".", " . ")
    fixed_text = fixed_text.replace("؛", " . ")
    fixed_text = fixed_text.replace(",", " , ")
    fixed_text = fixed_text.replace("،", " ، ")
    fixed_text = fixed_text.replace("!", " ! ")
    fixed_text = fixed_text.replace("?", " ? ")
    fixed_text = fixed_text.replace("؟", " ؟ ")

    fixed_text = fixed_text.replace(" هسته‌ای ", " هَستِیی ")
    fixed_text = fixed_text.replace(" رای‌گیری ", " رَعْی گیری ")
    fixed_text = fixed_text.replace(" نخست‌وزیر ", " نُخُسْتْ وَزیر ")
    fixed_text = fixed_text.replace(" پرالتهاب ", " پُرْ اِلْتِهاب ")

    fixed_text = fixed_text.replace("‌", " ")

    fixed_text = fixed_text.replace(" دفن ", " دَفْنْ ")
    fixed_text = fixed_text.replace(" موعد ", " مُوعِد ")
    fixed_text = fixed_text.replace(" اهرم ", " اَهرُم ")
    fixed_text = fixed_text.replace(" مسکو ", " مُسکو ")
    fixed_text = fixed_text.replace(" نهفته ", " نَهُفْته ")
    fixed_text = fixed_text.replace(" گردان ", " گُرْدان ")
    fixed_text = fixed_text.replace(" بوشهر ", " بوشِحْر ")
    fixed_text = fixed_text.replace(" سرتیپ ", " سَرتیپ ")
    fixed_text = fixed_text.replace(" پدافند ", " پَدافَند ")
    fixed_text = fixed_text.replace(" ناموجه ", " نامُوَجَح ")
    fixed_text = fixed_text.replace(" مکانیزم ", " مِکانیزْم ")

    fixed_text = fixed_text.replace(" هتک ", " هَتْکِ ")
    fixed_text = fixed_text.replace(" هتکِ ", " هَتْکِ ")

    fixed_text = fixed_text.replace(" اتم ", " اَتُم ")
    fixed_text = fixed_text.replace(" اتمی ", " اَتُمی ")

    fixed_text = fixed_text.replace(" افشا ", " اِفشا ")
    fixed_text = fixed_text.replace(" افشای ", " اِفْشایِ ")

    fixed_text = fixed_text.replace(" پهباد ", " پَهْباد ")
    fixed_text = fixed_text.replace(" پهبادها ", " پَهْبادْها ")
    fixed_text = fixed_text.replace(" پهبادهای ", " پَهْبادْهای ")

    fixed_text = fixed_text.replace(" سانتریفیو ", " سانتریفیوژ ")
    fixed_text = fixed_text.replace(" سانتریفیوها ", " سانتریفیوژها ")

    while "  " in fixed_text:
        fixed_text = fixed_text.replace("  ", " ")

    fixed_text = fixed_text.strip()

    return fixed_text


def clean_text_for_speech(text: str, max_chars: int = MAX_SPEECH_CHARS) -> tuple[str, bool]:
    """
    Strip light markdown and limit length before Edge TTS.

    Returns:
        cleaned text, truncated flag
    """

    cleaned = utility.fix_text(text=text)
    for token in ("**", "*", "#", "`", "_"):
        cleaned = cleaned.replace(token, " ")
    cleaned = cleaned.replace("\r", " ").replace("\n", " ")
    cleaned = utility.fix_text(text=cleaned)

    truncated = False
    if len(cleaned) > max_chars:
        trimmed = cleaned[:max_chars].rsplit(" ", 1)[0].strip()
        cleaned = trimmed or cleaned[:max_chars].strip()
        truncated = True

    return cleaned, truncated


def _save_communicate(communicate, audio_file_path: str) -> None:
    """Save speech with save_sync, or asyncio if that API is absent."""

    save_sync = getattr(communicate, "save_sync", None)
    if callable(save_sync):
        save_sync(audio_fname=audio_file_path)
        return

    async def _save() -> None:
        await communicate.save(audio_fname=audio_file_path)

    asyncio.run(_save())


def convert_text_to_speech(
    text: str,
    audio_file_path: str,
    rate: str = RATE,
    pitch: str = PITCH,
    volume: str = VOLUME,
    voice: str = VOICES_FEMALE[0],
) -> tuple[int, float]:
    """Convert text to speech (Sync)"""

    try:
        from edge_tts import Communicate
    except Exception as exception:
        raise RuntimeError(
            "بسته edge-tts نصب نیست. لطفا اجرا کنید: pip install edge-tts"
        ) from exception

    text = fix_text_for_speech(text=text)
    if not text:
        raise RuntimeError("متنی برای خواندن وجود ندارد.")

    word_count: int = utility.get_word_count(text=text)
    start_time: float = time.perf_counter()

    communicate = Communicate(
        text=text,
        rate=rate,
        pitch=pitch,
        voice=voice,
        volume=volume,
    )

    try:
        _save_communicate(communicate=communicate, audio_file_path=audio_file_path)
    except Exception as exception:
        raise RuntimeError(
            "ساخت صدا با Edge TTS ناموفق بود. این بخش به اینترنت نیاز دارد. "
            f"({exception})"
        ) from exception

    end_time: float = time.perf_counter()
    elapsed_time: float = end_time - start_time
    return word_count, elapsed_time


def synthesize_persian(
    text: str,
    voice: str = VOICES_FEMALE[0],
    max_chars: int = MAX_SPEECH_CHARS,
) -> tuple[str, int, float, bool]:
    """
    Create a Persian MP3 with Edge TTS.

    Returns:
        audio path, word count, elapsed seconds, truncated flag
    """

    speech_text, truncated = clean_text_for_speech(text=text, max_chars=max_chars)
    TTS_DIR.mkdir(parents=True, exist_ok=True)
    audio_path = TTS_DIR / f"reply_{utility.get_formated_now(with_miliseconds=True)}.mp3"
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
