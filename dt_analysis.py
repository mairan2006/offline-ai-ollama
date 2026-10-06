"""
File analysis helpers: image / text / pdf / audio / translation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import time

import dt_files as files
import dt_llm_utility as llm_utility
import dt_utility as utility
import dtx_whisper as whisper_module
from dt_ollama_manager import (
    format_bytes,
    get_available_ram_bytes,
    prepare_model_for_use,
    unload_all_loaded_models,
)
from model_constants import RAM_SAFETY_MARGIN_BYTES
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


def _free_whisper_if_chat_needs_ram(model_name: str) -> None:
    """Drop cached Whisper before loading a chat/vision model."""

    if not whisper_module.is_model_loaded():
        return

    whisper_module.release_model()


def _ask_ollama(
    system_prompt: str,
    user_text: str,
    model_name: str,
) -> str:
    _free_whisper_if_chat_needs_ram(model_name=model_name)
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


FILE_TASK_SYSTEM_PROMPT: Final[str] = (
    "تو یک دستیار هستی که روی محتوای فایل طبق درخواست کاربر کار می‌کند. "
    "فقط همان کاری را انجام بده که کاربر خواسته. "
    "به فارسی روان پاسخ بده مگر اینکه کاربر خلافش را بگوید. "
    "از پیشنهادهای اضافه و کارهای اختیاری خودداری کن."
)


def apply_prompt_to_file(
    file_path: Path,
    file_name: str,
    user_prompt: str,
    model_name: str,
    whisper_model: str = "auto",
) -> tuple[str, bool]:
    """
    Apply the user's free-form Persian prompt to an attached file.

    Returns:
        result text, whether Ollama models were unloaded for Whisper
    """

    prompt = utility.fix_text(text=str(user_prompt or ""))
    if not prompt:
        raise RuntimeError("ابتدا بنویسید با این فایل چه کار کنم.")

    kind = files.detect_file_kind(file_name=file_name)
    if kind == "unknown":
        raise RuntimeError("این نوع فایل پشتیبانی نمی‌شود.")

    unloaded = False

    if kind == "image":
        _free_whisper_if_chat_needs_ram(model_name=model_name)
        ok, message = prepare_model_for_use(model_name=model_name)
        if not ok:
            raise RuntimeError(message)
        answer, _, _, _ = chat_with_image(
            prompt=prompt,
            image_path=str(file_path),
            model_name=model_name,
        )
        if not answer:
            raise RuntimeError("پاسخی از مدل برای تصویر دریافت نشد.")
        return answer, unloaded

    if kind == "audio":
        text, _elapsed, unloaded, used_model = transcribe_audio(
            audio_path=file_path,
            model_name=whisper_model,
        )
        text = utility.fix_text(text=text)
        if not text:
            raise RuntimeError("متنی از صوت استخراج نشد.")
        answer = _ask_ollama(
            system_prompt=FILE_TASK_SYSTEM_PROMPT,
            user_text=(
                f"درخواست کاربر:\n{prompt}\n\n"
                f"متن استخراج‌شده از صوت «{file_name}» "
                f"(Whisper: {used_model}):\n{text}"
            ),
            model_name=model_name,
        )
        return answer, unloaded

    # pdf / text
    content = files.extract_text(file_path=file_path)
    content = files.truncate_text(text=content, max_chars=12000)
    if not content:
        raise RuntimeError("متنی از فایل استخراج نشد.")
    answer = _ask_ollama(
        system_prompt=FILE_TASK_SYSTEM_PROMPT,
        user_text=(
            f"درخواست کاربر:\n{prompt}\n\n"
            f"محتوای فایل «{file_name}»:\n{content}"
        ),
        model_name=model_name,
    )
    return answer, unloaded


def analyze_image(image_path: Path, model_name: str) -> str:
    """Analyze image with vision-capable Ollama model."""

    _free_whisper_if_chat_needs_ram(model_name=model_name)
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


def transcribe_audio(
    audio_path: Path,
    model_name: str = "",
) -> tuple[str, float, bool, str]:
    """
    Transcribe audio with Whisper (Persian).

    Unloads Ollama models first if free RAM is low.
    Returns text, elapsed seconds, whether Ollama models were unloaded,
    and the Whisper model name that was actually used.
    """

    requested = (model_name or "auto").replace(" ", "").lower()

    # Free chat models first so a stronger Whisper can fit on low-RAM PCs.
    unloaded_names = unload_all_loaded_models()
    if unloaded_names:
        time.sleep(0.8)

    available_after = get_available_ram_bytes()
    selected = whisper_module.choose_model_for_ram(
        available_bytes=available_after,
        preferred=requested,
    )

    if whisper_module.is_model_loaded() and not whisper_module.is_model_loaded(
        model_name=selected
    ):
        whisper_module.release_model()

    needed = whisper_module.estimate_ram_bytes(model_name=selected)
    if not whisper_module.is_model_loaded(model_name=selected):
        # faster-whisper needs less cushion than old openai-whisper path.
        needed += max(400_000_000, RAM_SAFETY_MARGIN_BYTES // 5)

    if not whisper_module.is_model_loaded(model_name=selected) and available_after < needed:
        # Fall back one more step if still tight.
        selected = whisper_module.choose_model_for_ram(
            available_bytes=available_after,
            preferred="auto",
        )
        needed = whisper_module.estimate_ram_bytes(model_name=selected) + 400_000_000

    if not whisper_module.is_model_loaded(model_name=selected) and available_after < needed:
        raise RuntimeError(
            "رم کافی برای Whisper نیست. "
            f"آزاد: {format_bytes(num_bytes=available_after)} | "
            f"موردنیاز تقریبی مدل {selected}: {format_bytes(num_bytes=needed)}. "
            "برنامه‌های دیگر را ببندید یا مدل سبک‌تر (tiny/base) را انتخاب کنید."
        )

    text, elapsed = whisper_module.transcribe(
        language=whisper_module.STT_LANGUAGE,
        model_name=selected,
        audio_file_path=str(audio_path),
    )
    return text, elapsed, bool(unloaded_names), selected


if __name__ == "__main__":
    utility.display_just_one_error_message(
        message=utility.ERROR_MESSAGE_MODULE_IS_NOT_EXECUTED_DIRECTLY,
    )
