"""
File helpers for upload / extract / classify.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import dt_utility as utility

VERSION: Final[str] = "1.0.0"

ROOT_DIR: Final[Path] = Path(__file__).resolve().parent
TEMP_DIR: Final[Path] = ROOT_DIR / "temp" / "uploads"

IMAGE_EXTENSIONS: Final[set[str]] = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
TEXT_EXTENSIONS: Final[set[str]] = {".txt", ".md", ".markdown", ".csv"}
PDF_EXTENSIONS: Final[set[str]] = {".pdf"}
AUDIO_EXTENSIONS: Final[set[str]] = {".mp3", ".wav", ".m4a", ".ogg"}


def ensure_temp_dir() -> Path:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    return TEMP_DIR


def get_extension(file_name: str) -> str:
    return Path(file_name).suffix.lower()


def detect_file_kind(file_name: str) -> str:
    """Return: image | pdf | text | audio | unknown"""

    extension = get_extension(file_name=file_name)
    if extension in IMAGE_EXTENSIONS:
        return "image"
    if extension in PDF_EXTENSIONS:
        return "pdf"
    if extension in TEXT_EXTENSIONS:
        return "text"
    if extension in AUDIO_EXTENSIONS:
        return "audio"
    return "unknown"


def save_uploaded_file(file_name: str, file_bytes: bytes) -> Path:
    """Save uploaded bytes to temp/uploads and return path."""

    ensure_temp_dir()
    safe_name = Path(file_name).name
    target = TEMP_DIR / f"{utility.get_formated_now(with_miliseconds=True)}_{safe_name}"
    target.write_bytes(file_bytes)
    return target


def extract_text_from_txt(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="ignore")


def extract_text_from_pdf(file_path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception as exception:
        raise RuntimeError(
            "بسته pypdf نصب نیست. لطفا اجرا کنید: pip install pypdf"
        ) from exception

    reader = PdfReader(str(file_path))
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        text = utility.fix_text(text=text)
        if text:
            parts.append(text)
    return "\n\n".join(parts).strip()


def extract_text(file_path: Path) -> str:
    """Extract text from txt/md/pdf."""

    kind = detect_file_kind(file_name=file_path.name)
    if kind == "text":
        return extract_text_from_txt(file_path=file_path)
    if kind == "pdf":
        return extract_text_from_pdf(file_path=file_path)
    raise ValueError("این نوع فایل متن قابل استخراج ندارد.")


def truncate_text(text: str, max_chars: int = 12000) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... متن طولانی بود و خلاصه‌سازی روی بخش اول انجام شد ...]"


if __name__ == "__main__":
    utility.display_just_one_error_message(
        message=utility.ERROR_MESSAGE_MODULE_IS_NOT_EXECUTED_DIRECTLY,
    )
