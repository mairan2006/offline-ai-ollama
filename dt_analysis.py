"""
File analysis helpers: image / text / pdf / audio / translation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import dt_files as files
import dt_llm_utility as llm_utility
import dt_utility as utility
import dtx_whisper as whisper_module
from dt_ollama_manager import (
    get_available_ram_bytes,
    prepare_model_for_use,
    unload_all_loaded_models,
)
from dtx_ollama import chat, chat_with_image

VERSION: Final[str] = "1.0.0"

IMAGE_PROMPT: Final[str] = (
    "این تصویر را به فارسی دقیق توضیح بده. "
    "اگر متنی در تصویر هست، آن را هم از راست به چپ استخراج کن."
)

SUMMARY_SYSTEM_PROMPT: Final[str] = (
    "تو یک دستیار تحلیل اسناد هستی. متن کاربر را به فارسی خلاصه و تحلیل کن. "
    "نکات مهم را شماره‌گذاری کن و کوتاه بنویس."
)

TRANSLATE_TO_FA_SYSTEM_PROMPT: Final[str] = """
تو یک مترجم حرفه‌ای به زبان فارسی هستی.

- از نوشتن عبارات مربوط به Markdown اجتناب کن.
- متن کاربر را با دقت به فارسی روان ترجمه کن.
- تمام آئین نگارش را رعایت کن.
- از نوشتن جملات اضافه اجتناب کن و فقط ترجمه را بنویس.
- نیم‌فاصله را رعایت کن (مثلا می‌شود، درخت‌ها).
"""

TRANSLATE_TO_EN_SYSTEM_PROMPT: Final[str] = """
You are a professional translator to English.

- Avoid Markdown decorations.
- Translate the user's text accurately and naturally.
- Do not add extra commentary. Return only the translation.
"""


def _ask_ollama(
    system_prompt: str,
    user_text: str,
    model_name: str,
) -> str:
    ok, message = prepare_model_for_use(model_name=model_name)
    if not ok:
        raise RuntimeError(message)

    messages = [
        {
            llm_utility.KEY_NAME_ROLE: llm_utility.ROLE_SYSTEM,
            llm_utility.KEY_NAME_CONTENT: system_prompt,
        },
        {
            llm_utility.KEY_NAME_ROLE: llm_utility.ROLE_USER,
            llm_utility.KEY_NAME_CONTENT: user_text,
        },
    ]
    answer, _, _, _ = chat(messages=messages, model_name=model_name)
    if not answer:
        raise RuntimeError("پاسخی از مدل دریافت نشد.")
    return answer


def analyze_image(image_path: Path, model_name: str) -> str:
    """Analyze image with vision-capable Ollama model."""

    ok, message = prepare_model_for_use(model_name=model_name)
    if not ok:
        raise RuntimeError(message)

    answer, _, _, _ = chat_with_image(
        prompt=IMAGE_PROMPT,
        image_path=str(image_path),
        model_name=model_name,
    )
    if not answer:
        raise RuntimeError("تحلیل تصویر پاسخی برنگرداند.")
    return answer


def summarize_document(file_path: Path, model_name: str) -> str:
    """Summarize txt/md/pdf content."""

    text = files.extract_text(file_path=file_path)
    text = files.truncate_text(text=text, max_chars=12000)
    if not text:
        raise RuntimeError("متنی از فایل استخراج نشد.")
    return _ask_ollama(
        system_prompt=SUMMARY_SYSTEM_PROMPT,
        user_text=text,
        model_name=model_name,
    )


def translate_text(
    text: str,
    model_name: str,
    to_persian: bool = True,
) -> str:
    """Translate free text with Ollama."""

    text = utility.fix_text(text=text)
    if not text:
        raise RuntimeError("متنی برای ترجمه وجود ندارد.")

    system_prompt = (
        TRANSLATE_TO_FA_SYSTEM_PROMPT if to_persian else TRANSLATE_TO_EN_SYSTEM_PROMPT
    )
    return _ask_ollama(
        system_prompt=system_prompt,
        user_text=text,
        model_name=model_name,
    )


def translate_document(
    file_path: Path,
    model_name: str,
    to_persian: bool = True,
) -> str:
    """Translate txt/md/pdf content."""

    text = files.extract_text(file_path=file_path)
    text = files.truncate_text(text=text, max_chars=8000)
    return translate_text(text=text, model_name=model_name, to_persian=to_persian)


def transcribe_audio(audio_path: Path) -> tuple[str, float]:
    """
    Transcribe audio with Whisper (fa/tiny).
    Unloads Ollama models first if free RAM is low.
    """

    needed = whisper_module.WHISPER_TINY_RAM_BYTES
    available = get_available_ram_bytes()
    if available < needed:
        unload_all_loaded_models()

    available_after = get_available_ram_bytes()
    if available_after < needed:
        raise RuntimeError(
            "رم کافی برای Whisper نیست. لطفا برنامه‌های دیگر را ببندید و دوباره تلاش کنید."
        )

    return whisper_module.transcribe(
        language=whisper_module.STT_LANGUAGE,
        model_name=whisper_module.STT_MODEL_NAME,
        audio_file_path=str(audio_path),
    )


if __name__ == "__main__":
    utility.display_just_one_error_message(
        message=utility.ERROR_MESSAGE_MODULE_IS_NOT_EXECUTED_DIRECTLY,
    )
