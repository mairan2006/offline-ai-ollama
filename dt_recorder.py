"""
Sound recorder (pattern from DT advanced Sound Recorder).

Records mono audio until silence after speech, then saves a WAV file.
"""

from __future__ import annotations

import time
import wave
from pathlib import Path
from typing import Final

import dt_utility as utility

VERSION: Final[str] = "1.0.0"

CHANNELS: Final[int] = 1
THRESHOLD: Final[float] = 0.009
SAMPLE_RATE: Final[int] = 16_000
SILENCE_DURATION: Final[float] = 2.4
CHUNK_DURATION: Final[float] = 0.1
CHUNK_SIZE: Final[int] = int(SAMPLE_RATE * CHUNK_DURATION)
MAX_RECORD_SECONDS: Final[float] = 25.0

ROOT_DIR: Final[Path] = Path(__file__).resolve().parent
RECORD_DIR: Final[Path] = ROOT_DIR / "temp" / "recordings"


def ensure_record_dir() -> Path:
    """Create the temp recordings folder."""

    RECORD_DIR.mkdir(parents=True, exist_ok=True)
    return RECORD_DIR


def save_audio(
    output_file: str,
    audio_frames: list,
    channels: int = CHANNELS,
    sample_rate: int = SAMPLE_RATE,
) -> None:
    """Save recorded float audio frames to a 16-bit WAV file."""

    if not audio_frames:
        raise RuntimeError("صدایی ضبط نشد. فایل ساخته نشد.")

    try:
        import numpy as np
    except Exception as exception:
        raise RuntimeError("بسته numpy نصب نیست. لطفا اجرا کنید: pip install numpy") from exception

    audio_data = np.concatenate(audio_frames, axis=0)
    audio_data = np.clip(audio_data, -1.0, 1.0)
    audio_data = (audio_data * 32_767).astype(dtype=np.int16)

    with wave.open(f=output_file, mode="wb") as wave_file:
        wave_file.setnchannels(nchannels=channels)
        wave_file.setsampwidth(sampwidth=2)
        wave_file.setframerate(framerate=sample_rate)
        wave_file.writeframes(data=audio_data.tobytes())


def save_audio_bytes(file_name: str, file_bytes: bytes) -> Path:
    """Save browser/uploaded audio bytes and return the path."""

    if not file_bytes:
        raise RuntimeError("فایل صوتی خالی است.")

    ensure_record_dir()
    safe_name = Path(file_name).name or "browser.wav"
    target = RECORD_DIR / f"{utility.get_formated_now(with_miliseconds=True)}_{safe_name}"
    target.write_bytes(file_bytes)
    return target


def get_default_input_device_name() -> str:
    """Return the default input device name, or an empty string."""

    try:
        import sounddevice as sd

        device = sd.query_devices(kind="input")
    except Exception:
        return ""

    if not isinstance(device, dict):
        return ""
    return str(device.get("name", "")).strip()


def record_until_silence(
    max_seconds: float = MAX_RECORD_SECONDS,
    silence_duration: float = SILENCE_DURATION,
    threshold: float = THRESHOLD,
    sample_rate: int = SAMPLE_RATE,
) -> Path:
    """
    Record from the default microphone until silence after speech.

    Stops when the speaker pauses, or when max_seconds is reached.
    """

    try:
        import numpy as np
        import sounddevice as sd
    except Exception as exception:
        raise RuntimeError(
            "بسته ضبط صدا نصب نیست. لطفا اجرا کنید: pip install sounddevice numpy"
        ) from exception

    if max_seconds < 1:
        max_seconds = 1

    silent_chunk_count: int = max(1, int(silence_duration / CHUNK_DURATION))
    frames: list = []
    speech_started: bool = False
    silent_chunks: int = 0
    stop_recording: bool = False

    def audio_callback(indata, frames_count, time_info, status) -> None:
        nonlocal speech_started, silent_chunks, stop_recording

        if stop_recording:
            return

        amplitude = float(np.sqrt(np.mean(indata**2)))
        if amplitude >= threshold:
            speech_started = True
            silent_chunks = 0
            frames.append(indata.copy())
            return

        if not speech_started:
            return

        silent_chunks += 1
        if silent_chunks >= silent_chunk_count:
            stop_recording = True
            return

        frames.append(indata.copy())

    try:
        stream = sd.InputStream(
            channels=CHANNELS,
            blocksize=CHUNK_SIZE,
            samplerate=sample_rate,
            callback=audio_callback,
        )
    except Exception as exception:
        raise RuntimeError(
            "میکروفون سیستم در دسترس نیست. از ضبط مرورگر استفاده کنید "
            f"یا میکروفون را وصل کنید. ({exception})"
        ) from exception

    try:
        with stream:
            started = time.perf_counter()
            while not stop_recording:
                sd.sleep(msec=100)
                if time.perf_counter() - started >= max_seconds:
                    break
    except Exception as exception:
        raise RuntimeError(f"ضبط صدا قطع شد: {exception}") from exception

    if not frames:
        raise RuntimeError(
            "صدایی شنیده نشد. نزدیک‌تر و واضح‌تر صحبت کنید و دوباره ضبط کنید."
        )

    ensure_record_dir()
    output_file = RECORD_DIR / f"recording_{utility.get_formated_now(with_miliseconds=True)}.wav"
    save_audio(
        output_file=str(output_file),
        audio_frames=frames,
        channels=CHANNELS,
        sample_rate=sample_rate,
    )
    return output_file


if __name__ == "__main__":
    utility.display_just_one_error_message(
        message=utility.ERROR_MESSAGE_MODULE_IS_NOT_EXECUTED_DIRECTLY,
    )
