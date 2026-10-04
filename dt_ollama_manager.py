"""
Ollama service manager: check status and start if needed.
"""

import os
import time
import shutil
import logging
import subprocess

from typing import (
    Final,
    Optional,
)

import dt_utility as utility
from dtx_dotenv import get_key_value
from dtx_ollama import get_offline_client

VERSION: Final[str] = "1.0.0"

BASE_URL_OFFLINE: Final[str] = get_key_value(
    key="OLLAMA_HOST",
    default="http://127.0.0.1:11434",
).replace(" ", "").lower()

START_TIMEOUT_SECONDS: Final[float] = 30.0
POLL_INTERVAL_SECONDS: Final[float] = 1.0

logger = logging.getLogger(name=__name__)
logger.addHandler(hdlr=logging.NullHandler())


def is_ollama_running(base_url: str = BASE_URL_OFFLINE) -> bool:
    """Return True if local Ollama API is reachable."""

    try:
        client = get_offline_client(base_url=base_url)
        client.list()
        return True
    except Exception as exception:
        logger.debug(msg=f"Ollama is not running: {exception}")
        return False


def find_ollama_executable() -> Optional[str]:
    """Find ollama executable on this machine."""

    which_path: Optional[str] = shutil.which(cmd="ollama")
    if which_path:
        return which_path

    local_app_data: str = os.environ.get("LOCALAPPDATA", "")
    candidates: list[str] = [
        os.path.join(local_app_data, "Programs", "Ollama", "ollama.exe"),
        r"C:\Program Files\Ollama\ollama.exe",
    ]

    for candidate in candidates:
        if os.path.isfile(path=candidate):
            return candidate

    return None


def start_ollama() -> bool:
    """
    Try to start local Ollama service.

    Returns True if start command was launched successfully.
    """

    ollama_path: Optional[str] = find_ollama_executable()
    if not ollama_path:
        logger.error(msg="Ollama executable not found")
        return False

    creationflags: int = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    try:
        subprocess.Popen(
            args=[ollama_path, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=creationflags,
            close_fds=True,
        )
        logger.debug(msg=f"Started Ollama with: {ollama_path} serve")
        return True
    except Exception as exception:
        logger.error(msg=f"Failed to start Ollama: {exception}")
        return False


def ensure_ollama_running(
    base_url: str = BASE_URL_OFFLINE,
    timeout_seconds: float = START_TIMEOUT_SECONDS,
) -> tuple[bool, str]:
    """
    Ensure Ollama is running. Start it if needed.

    Returns:
        (ok, persian_status_message)
    """

    if is_ollama_running(base_url=base_url):
        return True, "Ollama روشن است و آماده کار می‌باشد."

    started: bool = start_ollama()
    if not started:
        return False, (
            "Ollama خاموش بود و برنامه نتوانست آن را پیدا/روشن کند. "
            "لطفا Ollama را نصب یا دستی اجرا کنید."
        )

    deadline: float = time.perf_counter() + timeout_seconds
    while time.perf_counter() < deadline:
        if is_ollama_running(base_url=base_url):
            return True, "Ollama خاموش بود؛ برنامه آن را روشن کرد و اکنون آماده است."
        time.sleep(POLL_INTERVAL_SECONDS)

    return False, (
        "تلاش برای روشن کردن Ollama انجام شد، ولی هنوز پاسخ نمی‌دهد. "
        "لطفا چند لحظه صبر کنید یا Ollama را دستی باز کنید."
    )


if __name__ == "__main__":
    utility.display_just_one_error_message(
        message=utility.ERROR_MESSAGE_MODULE_IS_NOT_EXECUTED_DIRECTLY,
    )
