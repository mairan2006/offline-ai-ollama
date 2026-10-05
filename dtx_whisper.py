"""
Dariush Tasdighi Custom Whisper STT Module

Prefers faster-whisper (int8) for lower RAM and better Persian accuracy.
Falls back to openai-whisper if faster-whisper is unavailable.
"""

from __future__ import annotations

import gc
import logging
import os
import shutil
import subprocess
import time
import wave
from pathlib import Path
from typing import Final, Optional

import dt_utility as utility

VERSION: Final[str] = "1.4.0"

TEMP_AUDIO_FILE_PATH: Final[str] = "./temp/temp_audio.mp3"

STT_TEMPRETURE: Final[float] = 0.0
STT_BEAM_SIZE: Final[int] = 8
STT_VALID_AUDIO_FILE_EXTENSIONS: Final[list[str]] = [
    "mp3",
    "wav",
    "m4a",
    "ogg",
    "webm",
]

# Persian offline STT. Prefer medium when RAM allows (auto mode).
STT_LANGUAGE: Final[str] = "fa"
STT_MODEL_NAME: Final[str] = "medium"
STT_INITIAL_PROMPT: Final[str] = (
    "این یک گفتگوی فارسی روزمره و فنی است. "
    "کلمات رایج: پروژه، هوش مصنوعی، ایران، معرفی، برنامه، مدل، "
    "سلام، لطفا، ممنون، بله، نه، خوب، چطور."
)

# Common Whisper Persian mishearings → corrected forms.
STT_SIMPLE_FIXES: Final[tuple[tuple[str, str], ...]] = (
    ("پروجه", "پروژه"),
    ("پرژه", "پروژه"),
    ("هوشه مصنوعی", "هوش مصنوعی"),
    ("هوشهصنعی", "هوش مصنوعی"),
    ("مستنوی", "هوش مصنوعی"),
    ("بوش مصنوعی", "هوش مصنوعی"),
)

# Approximate RAM while model is loaded (faster-whisper int8 estimates).
WHISPER_RAM_BYTES: Final[dict[str, int]] = {
    "tiny": 500_000_000,
    "base": 700_000_000,
    "small": 1_200_000_000,
    "medium": 2_800_000_000,
    "turbo": 4_200_000_000,
}
WHISPER_TINY_RAM_BYTES: Final[int] = WHISPER_RAM_BYTES["tiny"]

# Map UI names to faster-whisper / openai-whisper model ids.
FASTER_MODEL_IDS: Final[dict[str, str]] = {
    "tiny": "tiny",
    "base": "base",
    "small": "small",
    "medium": "medium",
    "turbo": "large-v3-turbo",
}
OPENAI_MODEL_IDS: Final[dict[str, str]] = {
    "tiny": "tiny",
    "base": "base",
    "small": "small",
    "medium": "medium",
    "turbo": "turbo",
}

logger = logging.getLogger(name=__name__)
logger.addHandler(hdlr=logging.NullHandler())

_cached_model = None
_cached_model_name: str = ""
_cached_backend: str = ""
_pending_freed_bytes: int = 0
_pending_freed_at: float = 0.0


def estimate_ram_bytes(model_name: str) -> int:
    """Return a conservative RAM estimate for a Whisper model."""

    key = (model_name or STT_MODEL_NAME).replace(" ", "").lower()
    return int(WHISPER_RAM_BYTES.get(key, WHISPER_RAM_BYTES["small"]))


def is_model_loaded(model_name: str = "") -> bool:
    """Return True when a Whisper model is cached in this process."""

    if _cached_model is None:
        return False
    if not model_name:
        return True
    return _cached_model_name == model_name.replace(" ", "").lower()


def get_loaded_model_name() -> str:
    """Return the cached Whisper model name, or an empty string."""

    if _cached_model is None:
        return ""
    return _cached_model_name


def get_pending_freed_bytes(max_age_seconds: float = 90.0) -> int:
    """
    Bytes recently freed by release_model that the OS may not report yet.
    """

    if _pending_freed_bytes <= 0:
        return 0
    if (time.perf_counter() - _pending_freed_at) > max_age_seconds:
        return 0
    return int(_pending_freed_bytes)


def clear_pending_freed_bytes() -> None:
    """Clear the pending freed-RAM estimate."""

    global _pending_freed_bytes, _pending_freed_at

    _pending_freed_bytes = 0
    _pending_freed_at = 0.0


def release_model() -> bool:
    """Drop the cached Whisper model so its RAM can be reused."""

    global _cached_model, _cached_model_name, _cached_backend
    global _pending_freed_bytes, _pending_freed_at

    had_model = _cached_model is not None
    if had_model:
        _pending_freed_bytes = estimate_ram_bytes(model_name=_cached_model_name)
        _pending_freed_at = time.perf_counter()

    _cached_model = None
    _cached_model_name = ""
    _cached_backend = ""
    gc.collect()

    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:
        pass

    gc.collect()
    return had_model


def choose_model_for_ram(available_bytes: int, preferred: str = STT_MODEL_NAME) -> str:
    """
    Pick the best Whisper size that fits in available RAM.

    For "auto", always choose the strongest model that fits.
    """

    preferred = (preferred or "auto").replace(" ", "").lower()
    # Keep a modest cushion for OS + Streamlit while STT runs.
    budget = max(0, int(available_bytes) - 700_000_000)
    ranking = ["turbo", "medium", "small", "base", "tiny"]

    # Explicit choice: use it if it fits, otherwise fall down the ranking.
    if preferred not in {"", "auto"}:
        if preferred in WHISPER_RAM_BYTES and estimate_ram_bytes(preferred) <= budget:
            return preferred
        start = ranking.index(preferred) + 1 if preferred in ranking else 0
        for name in ranking[start:]:
            if estimate_ram_bytes(name) <= budget:
                return name
        return "tiny"

    for name in ranking:
        if estimate_ram_bytes(name) <= budget:
            return name
    return "tiny"


def apply_simple_persian_fixes(text: str) -> str:
    """Apply a tiny dictionary of common Persian STT mistakes."""

    fixed = utility.fix_text(text=text)
    for wrong, right in STT_SIMPLE_FIXES:
        fixed = fixed.replace(wrong, right)
    return fixed


def _faster_whisper_available() -> bool:
    try:
        from faster_whisper import WhisperModel  # noqa: F401

        return True
    except Exception:
        return False


def _load_model(model_name: str):
    """Load Whisper once per model name and reuse it."""

    global _cached_model, _cached_model_name, _cached_backend

    model_name = model_name.replace(" ", "").lower()
    if _cached_model is not None and _cached_model_name == model_name:
        return _cached_model, _cached_backend

    release_model()

    if _faster_whisper_available():
        from faster_whisper import WhisperModel

        try:
            import torch

            use_cuda = bool(torch.cuda.is_available())
        except Exception:
            use_cuda = False

        device = "cuda" if use_cuda else "cpu"
        compute_type = "float16" if use_cuda else "int8"
        model_id = FASTER_MODEL_IDS.get(model_name, model_name)
        try:
            model = WhisperModel(
                model_id,
                device=device,
                compute_type=compute_type,
            )
            _cached_model = model
            _cached_model_name = model_name
            _cached_backend = "faster"
            return model, "faster"
        except Exception as exception:
            logger.warning(
                msg=f"faster-whisper load failed ({exception}); falling back to openai-whisper"
            )

    try:
        import torch
        import whisper
    except Exception as exception:
        raise RuntimeError(
            "بسته Whisper نصب نیست. لطفا اجرا کنید: "
            "pip install faster-whisper  یا  pip install openai-whisper torch"
        ) from exception

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_id = OPENAI_MODEL_IDS.get(model_name, model_name)
    model = whisper.load_model(device=device, name=model_id)
    _cached_model = model
    _cached_model_name = model_name
    _cached_backend = "openai"
    return model, "openai"


def _resample_audio(audio, original_rate: int, target_rate: int = 16_000):
    """Resample mono float audio to Whisper's 16 kHz rate."""

    import numpy as np

    audio = np.asarray(audio, dtype=np.float32)
    if original_rate == target_rate or len(audio) == 0:
        return audio

    target_length = max(1, int(round(len(audio) * target_rate / original_rate)))
    source_x = np.linspace(0.0, 1.0, num=len(audio), endpoint=False)
    target_x = np.linspace(0.0, 1.0, num=target_length, endpoint=False)
    return np.interp(target_x, source_x, audio).astype(np.float32)


def preprocess_audio(audio):
    """
    Normalize and trim quiet edges for clearer Persian STT.

    Helps a lot on quiet laptop mics without using extra RAM.
    """

    import numpy as np

    audio = np.asarray(audio, dtype=np.float32).reshape(-1)
    if audio.size == 0:
        return audio

    peak = float(np.max(np.abs(audio)))
    if peak > 1e-6:
        audio = audio / peak * 0.92

    # Soft noise gate for very quiet samples.
    noise_floor = float(np.percentile(np.abs(audio), 20))
    gate = max(0.008, min(0.03, noise_floor * 2.5))
    audio = np.where(np.abs(audio) < gate, audio * 0.15, audio)

    # Trim long leading/trailing silence.
    window = 1600  # 100ms at 16kHz
    energies = []
    for index in range(0, len(audio), window):
        chunk = audio[index : index + window]
        energies.append(float(np.sqrt(np.mean(chunk**2))) if chunk.size else 0.0)

    if energies:
        speech_idx = [i for i, energy in enumerate(energies) if energy >= gate]
        if speech_idx:
            start = max(0, speech_idx[0] - 1) * window
            end = min(len(audio), (speech_idx[-1] + 2) * window)
            audio = audio[start:end]

    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 1e-6:
        audio = audio / peak * 0.95

    return np.ascontiguousarray(audio, dtype=np.float32)


def read_wav_for_whisper(audio_file_path: str):
    """
    Load a WAV file as 16 kHz mono float32.

    Whisper's file loader needs ffmpeg. Recorded WAV files can skip that.
    """

    import numpy as np

    with wave.open(audio_file_path, mode="rb") as wave_file:
        channels = wave_file.getnchannels()
        sample_rate = wave_file.getframerate()
        sample_width = wave_file.getsampwidth()
        raw_frames = wave_file.readframes(wave_file.getnframes())

    if not raw_frames:
        raise RuntimeError("فایل صوتی خالی است.")

    if sample_width == 2:
        audio = np.frombuffer(raw_frames, dtype=np.int16).astype(np.float32) / 32_768.0
    elif sample_width == 4:
        audio = np.frombuffer(raw_frames, dtype=np.int32).astype(np.float32) / 2_147_483_648.0
    elif sample_width == 1:
        audio = (np.frombuffer(raw_frames, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    else:
        raise RuntimeError("این wav برای Whisper قابل خواندن نیست.")

    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)

    audio = _resample_audio(audio=audio, original_rate=sample_rate)
    return preprocess_audio(audio=audio)


def ensure_ffmpeg_on_path() -> Optional[str]:
    """Return ffmpeg path, preferring PATH then imageio-ffmpeg."""

    existing = shutil.which("ffmpeg")
    if existing:
        return existing

    try:
        import imageio_ffmpeg

        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None

    if not ffmpeg_path or not os.path.exists(ffmpeg_path):
        return None

    ffmpeg_dir = os.path.dirname(ffmpeg_path)
    path_value = os.environ.get("PATH", "")
    if ffmpeg_dir and ffmpeg_dir not in path_value.split(os.pathsep):
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + path_value
    return ffmpeg_path


def convert_audio_to_wav(audio_file_path: str) -> str:
    """Convert non-wav audio to a temporary 16-bit mono wav for Whisper."""

    ffmpeg_path = ensure_ffmpeg_on_path()
    if not ffmpeg_path:
        raise RuntimeError(
            "برای mp3/webm و فرمت‌های غیر wav، ffmpeg پیدا نشد. "
            "لطفا اجرا کنید: pip install imageio-ffmpeg"
        )

    root = Path(audio_file_path).resolve().parent
    target = root / f"{Path(audio_file_path).stem}_whisper16k.wav"
    command = [
        ffmpeg_path,
        "-y",
        "-i",
        audio_file_path,
        "-ac",
        "1",
        "-ar",
        "16000",
        str(target),
    ]
    completed = subprocess.run(
        args=command,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0 or not target.exists():
        detail = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(
            "تبدیل فایل صوتی به wav ناموفق بود. "
            + (detail[-300:] if detail else "")
        )
    return str(target)


def prepare_whisper_audio(audio_file_path: str):
    """Return a Whisper audio array for wav, or a converted wav path."""

    extension = audio_file_path.split(sep=".")[-1].lower()
    if extension == "wav":
        return read_wav_for_whisper(audio_file_path=audio_file_path)

    wav_path = convert_audio_to_wav(audio_file_path=audio_file_path)
    return read_wav_for_whisper(audio_file_path=wav_path)


def _transcribe_faster(
    model,
    audio,
    language: str,
    tempreture: float,
    prompt: Optional[str],
) -> str:
    segments, _info = model.transcribe(
        audio,
        language=language,
        beam_size=STT_BEAM_SIZE,
        best_of=STT_BEAM_SIZE,
        temperature=tempreture,
        initial_prompt=prompt,
        condition_on_previous_text=False,
        vad_filter=True,
        vad_parameters={
            "min_silence_duration_ms": 500,
            "speech_pad_ms": 400,
        },
        no_speech_threshold=0.6,
        compression_ratio_threshold=2.4,
    )
    parts = [str(segment.text).strip() for segment in segments if str(segment.text).strip()]
    return " ".join(parts).strip()


def _transcribe_openai(
    model,
    audio,
    language: str,
    tempreture: float,
    prompt: Optional[str],
    fp16_enabled: bool,
) -> str:
    response: dict = model.transcribe(
        fp16=fp16_enabled,
        language=language,
        audio=audio,
        temperature=tempreture,
        initial_prompt=prompt,
        condition_on_previous_text=False,
        without_timestamps=True,
        beam_size=STT_BEAM_SIZE,
        best_of=STT_BEAM_SIZE,
    )
    return str(response.get("text", "")).strip()


def transcribe(
    language: str = STT_LANGUAGE,
    model_name: str = STT_MODEL_NAME,
    tempreture: float = STT_TEMPRETURE,
    audio_file_path: str = TEMP_AUDIO_FILE_PATH,
    initial_prompt: Optional[str] = STT_INITIAL_PROMPT,
) -> tuple[str, float]:
    """
    Offline transcribe speech to text
    """

    logger.debug(msg=f"Whisper Model: '{model_name}' - Transcribe started...")

    start_time: float = time.perf_counter()

    if not os.path.exists(path=audio_file_path):
        raise Exception(f"File '{audio_file_path}' not found")

    if not os.path.isfile(path=audio_file_path):
        raise Exception(f"File '{audio_file_path}' not found")

    file_extension: str = audio_file_path.split(sep=".")[-1].lower()
    if file_extension not in STT_VALID_AUDIO_FILE_EXTENSIONS:
        raise Exception(f"The '{audio_file_path}' file format is not valid")

    model, backend = _load_model(model_name=model_name)
    audio = prepare_whisper_audio(audio_file_path=audio_file_path)
    prompt = initial_prompt if language.replace(" ", "").lower().startswith("fa") else None

    if backend == "faster":
        text = _transcribe_faster(
            model=model,
            audio=audio,
            language=language,
            tempreture=tempreture,
            prompt=prompt,
        )
    else:
        try:
            import torch

            fp16_enabled = bool(torch.cuda.is_available())
        except Exception:
            fp16_enabled = False
        text = _transcribe_openai(
            model=model,
            audio=audio,
            language=language,
            tempreture=tempreture,
            prompt=prompt,
            fp16_enabled=fp16_enabled,
        )

    end_time: float = time.perf_counter()
    elapsed_time: float = end_time - start_time

    text = apply_simple_persian_fixes(text=text)

    logger.debug(msg=f"Whisper Model: '{model_name}' - Transcribe finished.")

    return text, elapsed_time


if __name__ == "__main__":
    utility.display_just_one_error_message(
        message=utility.ERROR_MESSAGE_MODULE_IS_NOT_EXECUTED_DIRECTLY,
    )
