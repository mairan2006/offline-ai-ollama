"""
Dariush Tasdighi Custom 'openai-whisper' Package Module
"""

from typing import Final

import os
import time
import logging

import dt_utility as utility

VERSION: Final[str] = "1.1.0"

TEMP_AUDIO_FILE_PATH: Final[str] = "./temp/temp_audio.mp3"

STT_TEMPRETURE: Final[float] = 0.0
STT_VALID_AUDIO_FILE_EXTENSIONS: Final[list[str]] = [
    "mp3",
    "wav",
    "m4a",
    "ogg",
]

# Persian offline STT defaults (lightweight).
STT_LANGUAGE: Final[str] = "fa"
STT_MODEL_NAME: Final[str] = "tiny"

# Approximate RAM needed for whisper tiny.
WHISPER_TINY_RAM_BYTES: Final[int] = 1_500_000_000

logger = logging.getLogger(name=__name__)
logger.addHandler(hdlr=logging.NullHandler())


def transcribe(
    language: str = STT_LANGUAGE,
    model_name: str = STT_MODEL_NAME,
    tempreture: float = STT_TEMPRETURE,
    audio_file_path: str = TEMP_AUDIO_FILE_PATH,
) -> tuple[str, float]:
    """
    Offline transcribe speech to text
    """

    try:
        import torch
        import whisper
    except Exception as exception:
        raise RuntimeError(
            "بسته Whisper نصب نیست. لطفا اجرا کنید: pip install openai-whisper torch"
        ) from exception

    logger.debug(msg=f"Whisper Model: '{model_name}' - Transcribe started...")

    start_time: float = time.perf_counter()

    if not os.path.exists(path=audio_file_path):
        raise Exception(f"File '{audio_file_path}' not found")

    if not os.path.isfile(path=audio_file_path):
        raise Exception(f"File '{audio_file_path}' not found")

    file_extension: str = audio_file_path.split(sep=".")[-1].lower()
    if file_extension not in STT_VALID_AUDIO_FILE_EXTENSIONS:
        raise Exception(f"The '{audio_file_path}' file format is not valid")

    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    fp16_enabled: bool = True if device == "cuda" else False

    model = whisper.load_model(
        device=device,
        name=model_name,
    )

    response: dict = model.transcribe(
        fp16=fp16_enabled,
        language=language,
        audio=audio_file_path,
        temperature=tempreture,
    )

    text: str = str(response.get("text", "")).strip()

    end_time: float = time.perf_counter()
    elapsed_time: float = end_time - start_time

    logger.debug(msg=f"Whisper Model: '{model_name}' - Transcribe finished.")

    return text, elapsed_time


if __name__ == "__main__":
    utility.display_just_one_error_message(
        message=utility.ERROR_MESSAGE_MODULE_IS_NOT_EXECUTED_DIRECTLY,
    )
