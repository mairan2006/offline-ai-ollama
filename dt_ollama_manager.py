"""
Ollama service manager:
- check/start service
- list/pull models
- RAM-safe load with unload of previous models
"""

from __future__ import annotations

import os
import time
import shutil
import logging
import threading
import subprocess

from typing import (
    Any,
    Final,
    Optional,
    Callable,
)

import psutil

import dt_utility as utility
import model_constants as model_constants
from dtx_dotenv import get_key_value
from dtx_ollama import get_offline_client

VERSION: Final[str] = "2.0.0"

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
    """Try to start local Ollama service."""

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
    """Ensure Ollama is running. Start it if needed."""

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


def _normalize_model_name(model_name: str) -> str:
    return model_name.replace(" ", "").lower()


def list_downloaded_models(base_url: str = BASE_URL_OFFLINE) -> list[str]:
    """Return sorted list of locally downloaded model names."""

    client = get_offline_client(base_url=base_url)
    response = client.list()
    models = getattr(response, "models", None) or []

    names: list[str] = []
    for model_item in models:
        name = getattr(model_item, "model", None) or getattr(model_item, "name", None)
        if name:
            names.append(_normalize_model_name(model_name=str(name)))

    names = sorted(set(names))
    return names


def is_model_downloaded(
    model_name: str,
    base_url: str = BASE_URL_OFFLINE,
) -> bool:
    """Return True if model exists locally."""

    target = _normalize_model_name(model_name=model_name)
    downloaded = list_downloaded_models(base_url=base_url)

    if target in downloaded:
        return True

    for item in downloaded:
        if item == target:
            return True
        if item.startswith(f"{target}:"):
            return True

    return False


def get_download_size_bytes(model_name: str) -> int:
    """Return approximate download size for a model."""

    model_name = _normalize_model_name(model_name=model_name)
    item = model_constants.MODEL_CATALOG.get(model_name)
    if item and item.get("download_bytes"):
        return int(item["download_bytes"])
    return model_constants.DEFAULT_MODEL_DOWNLOAD_BYTES


def get_model_details(model_name: str) -> dict:
    """Return full details for UI display."""

    model_name = _normalize_model_name(model_name=model_name)
    item = model_constants.MODEL_CATALOG.get(model_name, {})

    download_bytes = int(
        item.get("download_bytes", model_constants.DEFAULT_MODEL_DOWNLOAD_BYTES)
    )
    ram_bytes = int(
        item.get("approx_ram_bytes", model_constants.DEFAULT_MODEL_RAM_BYTES)
    )

    return {
        "name": model_name,
        "title": item.get("title", model_name),
        "category": item.get("category", "سایر"),
        "description": item.get(
            "description",
            "این مدل در کاتالوگ داخلی نیست؛ از مدل‌های نصب‌شده روی سیستم شماست.",
        ),
        "download_bytes": download_bytes,
        "approx_ram_bytes": ram_bytes,
        "download_label": format_bytes(download_bytes),
        "ram_label": format_bytes(ram_bytes),
    }


def get_model_display_options(
    base_url: str = BASE_URL_OFFLINE,
) -> list[tuple[str, str, bool]]:
    """
    Build short dropdown options.

    Returns list of (model_name, short_label, is_downloaded)
    Full description is shown outside the dropdown.
    """

    downloaded = set(list_downloaded_models(base_url=base_url))
    catalog_names = list(model_constants.CATALOG_MODEL_NAMES)

    for name in sorted(downloaded):
        if name not in catalog_names:
            catalog_names.append(name)

    options: list[tuple[str, str, bool]] = []
    for name in catalog_names:
        is_downloaded = name in downloaded
        mark = "🟢" if is_downloaded else "⬇️"
        label = f"{mark} {name}"
        options.append((name, label, is_downloaded))

    return options


_download_jobs: dict[str, dict[str, Any]] = {}
_download_jobs_lock = threading.Lock()


def get_download_jobs() -> dict[str, dict[str, Any]]:
    """Return a copy of in-process download jobs (survives dialog close)."""

    with _download_jobs_lock:
        return {name: dict(job) for name, job in _download_jobs.items()}


def get_download_job(model_name: str) -> Optional[dict[str, Any]]:
    """Return one download job snapshot, or None."""

    model_name = _normalize_model_name(model_name=model_name)
    with _download_jobs_lock:
        job = _download_jobs.get(model_name)
        return dict(job) if job else None


def clear_finished_download_job(model_name: str) -> None:
    """Remove a done/error job entry from the in-memory map."""

    model_name = _normalize_model_name(model_name=model_name)
    with _download_jobs_lock:
        job = _download_jobs.get(model_name)
        if job and job.get("status") in {"done", "error"}:
            _download_jobs.pop(model_name, None)


def _update_download_job(model_name: str, **fields: Any) -> None:
    """Merge fields into a download job record."""

    with _download_jobs_lock:
        current = dict(_download_jobs.get(model_name) or {})
        current.update(fields)
        _download_jobs[model_name] = current


def _parse_pull_event(event: Any) -> dict[str, Any]:
    """Normalize an ollama.pull stream event into status/bytes/percent."""

    if isinstance(event, dict):
        status = event.get("status")
        completed = event.get("completed")
        total = event.get("total")
    else:
        status = getattr(event, "status", None)
        completed = getattr(event, "completed", None)
        total = getattr(event, "total", None)

    percent: Optional[float] = None
    try:
        if completed is not None and total:
            percent = max(
                0.0,
                min(100.0, 100.0 * float(completed) / float(total)),
            )
    except Exception:
        percent = None

    return {
        "status": str(status or ""),
        "completed": int(completed) if completed is not None else None,
        "total": int(total) if total is not None else None,
        "percent": percent,
    }


def pull_model(
    model_name: str,
    base_url: str = BASE_URL_OFFLINE,
    progress_callback: Optional[Callable[[str], None]] = None,
    progress_hook: Optional[Callable[[dict[str, Any]], None]] = None,
) -> None:
    """Download model with ollama.pull (optional percent via progress_hook)."""

    model_name = _normalize_model_name(model_name=model_name)
    client = get_offline_client(base_url=base_url)

    if progress_callback:
        progress_callback(f"شروع دانلود مدل {model_name}...")
    if progress_hook:
        progress_hook(
            {
                "status": f"شروع دانلود مدل {model_name}...",
                "completed": None,
                "total": None,
                "percent": 0.0,
            }
        )

    stream = client.pull(model=model_name, stream=True)
    for event in stream:
        parsed = _parse_pull_event(event)
        status = parsed.get("status") or ""
        if progress_callback and status:
            progress_callback(str(status))
        if progress_hook:
            progress_hook(parsed)


def start_model_download(
    model_name: str,
    base_url: str = BASE_URL_OFFLINE,
) -> tuple[bool, str]:
    """
    Start a background download job if one is not already running.

    Job state lives in-process so closing/reopening the dialog keeps progress.
    """

    model_name = _normalize_model_name(model_name=model_name)
    if is_model_downloaded(model_name=model_name, base_url=base_url):
        return False, f"مدل {model_name} از قبل دانلود شده است."

    with _download_jobs_lock:
        existing = _download_jobs.get(model_name)
        if existing and existing.get("status") == "running":
            return False, f"دانلود {model_name} از قبل در حال اجراست."
        _download_jobs[model_name] = {
            "model_name": model_name,
            "status": "running",
            "percent": 0.0,
            "message": "در صف دانلود...",
            "bytes_done": 0,
            "bytes_total": 0,
            "error": "",
        }

    worker = threading.Thread(
        target=_download_worker,
        args=(model_name, base_url),
        daemon=True,
        name=f"ollama-pull-{model_name}",
    )
    worker.start()
    return True, f"دانلود {model_name} شروع شد."


def _download_worker(model_name: str, base_url: str) -> None:
    """Background worker that pulls one model and updates job progress."""

    def hook(parsed: dict[str, Any]) -> None:
        fields: dict[str, Any] = {
            "status": "running",
            "message": str(parsed.get("status") or "در حال دانلود..."),
        }
        if parsed.get("completed") is not None:
            fields["bytes_done"] = int(parsed["completed"])
        if parsed.get("total") is not None:
            fields["bytes_total"] = int(parsed["total"])
        if parsed.get("percent") is not None:
            fields["percent"] = float(parsed["percent"])
        _update_download_job(model_name, **fields)

    try:
        pull_model(
            model_name=model_name,
            base_url=base_url,
            progress_hook=hook,
        )
        if is_model_downloaded(model_name=model_name, base_url=base_url):
            _update_download_job(
                model_name,
                status="done",
                percent=100.0,
                message="دانلود کامل شد.",
                error="",
            )
        else:
            _update_download_job(
                model_name,
                status="error",
                message="دانلود تمام شد ولی مدل پیدا نشد.",
                error="download incomplete",
            )
    except Exception as exception:
        _update_download_job(
            model_name,
            status="error",
            message="دانلود ناموفق بود.",
            error=str(exception),
        )


def list_loaded_models(base_url: str = BASE_URL_OFFLINE) -> list[str]:
    """Return models currently loaded in memory (ollama ps)."""

    client = get_offline_client(base_url=base_url)
    try:
        response = client.ps()
    except Exception as exception:
        logger.debug(msg=f"client.ps failed: {exception}")
        return []

    models = getattr(response, "models", None) or []
    names: list[str] = []
    for model_item in models:
        name = getattr(model_item, "model", None) or getattr(model_item, "name", None)
        if name:
            names.append(_normalize_model_name(model_name=str(name)))
    return names


def unload_model(
    model_name: str,
    base_url: str = BASE_URL_OFFLINE,
) -> None:
    """Unload one model from RAM."""

    model_name = _normalize_model_name(model_name=model_name)
    client = get_offline_client(base_url=base_url)

    try:
        client.generate(
            model=model_name,
            prompt="",
            keep_alive=0,
        )
        logger.debug(msg=f"Unloaded model via generate keep_alive=0: {model_name}")
        return
    except Exception as exception:
        logger.debug(msg=f"generate unload failed: {exception}")

    ollama_path = find_ollama_executable()
    if ollama_path:
        subprocess.run(
            args=[ollama_path, "stop", model_name],
            check=False,
            capture_output=True,
            text=True,
        )


def unload_all_loaded_models(base_url: str = BASE_URL_OFFLINE) -> list[str]:
    """Unload all currently loaded models. Returns unloaded names."""

    loaded = list_loaded_models(base_url=base_url)
    for model_name in loaded:
        unload_model(model_name=model_name, base_url=base_url)
    return loaded


def get_available_ram_bytes() -> int:
    """Return currently available system RAM in bytes."""

    return int(psutil.virtual_memory().available)


def get_total_ram_bytes() -> int:
    """Return total system RAM in bytes."""

    return int(psutil.virtual_memory().total)


def format_bytes(num_bytes: int) -> str:
    """Human-readable bytes in Persian-friendly GB/MB."""

    gb = num_bytes / (1024**3)
    if gb >= 1:
        return f"{gb:.1f} گیگابایت"
    mb = num_bytes / (1024**2)
    return f"{mb:.0f} مگابایت"


def estimate_model_ram_bytes(model_name: str) -> int:
    """Estimate RAM needed for a model."""

    model_name = _normalize_model_name(model_name=model_name)
    item = model_constants.MODEL_CATALOG.get(model_name)
    if item:
        return int(item["approx_ram_bytes"])
    return model_constants.DEFAULT_MODEL_RAM_BYTES


def can_fit_model_in_ram(
    model_name: str,
    *,
    available_bytes: Optional[int] = None,
    margin_bytes: Optional[int] = None,
) -> tuple[bool, str, int]:
    """
    Check whether model can fit with a RAM safety margin.

    Returns:
        ok, message, available_ram_bytes
    """

    needed = estimate_model_ram_bytes(model_name=model_name)
    available = (
        get_available_ram_bytes() if available_bytes is None else int(available_bytes)
    )
    margin = (
        model_constants.RAM_SAFETY_MARGIN_BYTES
        if margin_bytes is None
        else int(margin_bytes)
    )
    required_free = needed + margin

    if available >= required_free:
        message = (
            f"رم کافی است. آزاد: {format_bytes(available)} | "
            f"موردنیاز تقریبی مدل+حاشیه امن: {format_bytes(required_free)}"
        )
        return True, message, available

    message = (
        f"رم کافی نیست. آزاد: {format_bytes(available)} | "
        f"موردنیاز تقریبی مدل+حاشیه امن: {format_bytes(required_free)}"
    )
    return False, message, available


def _release_whisper_for_ram() -> int:
    """
    Unload cached Whisper if present.

    Returns estimated bytes that should become free after release,
    including a recent release that the OS may not have reported yet.
    """

    try:
        import dtx_whisper as whisper_module
    except Exception:
        return 0

    if whisper_module.is_model_loaded():
        whisper_module.release_model()

    return int(whisper_module.get_pending_freed_bytes())


def _effective_available_ram_bytes() -> int:
    """Available RAM plus Whisper bytes that were just released."""

    available = get_available_ram_bytes()
    try:
        import dtx_whisper as whisper_module

        pending = whisper_module.get_pending_freed_bytes()
    except Exception:
        pending = 0
    return int(available + max(0, pending))


def _suggest_lighter_models(model_name: str) -> str:
    """Build a short Persian hint for lighter catalog models."""

    current = estimate_model_ram_bytes(model_name=model_name)
    suggestions: list[str] = []
    for name, item in model_constants.MODEL_CATALOG.items():
        if name == model_name:
            continue
        category = str(item.get("category", ""))
        if category in {"امبدینگ", "vision", "بینایی"}:
            continue
        ram = int(item.get("approx_ram_bytes", 0))
        if ram <= 0 or ram >= current:
            continue
        if category not in {"خیلی سبک", "سبک", "متعادل"} and ram > 2_500_000_000:
            continue
        suggestions.append(f"{name} (~{format_bytes(ram)})")
        if len(suggestions) >= 3:
            break

    if not suggestions:
        return "یک مدل سبک‌تر از لیست کنار صفحه انتخاب کنید."
    return "مدل سبک‌تر پیشنهاد می‌شود: " + "، ".join(suggestions)


def prepare_model_for_use(
    model_name: str,
    base_url: str = BASE_URL_OFFLINE,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> tuple[bool, str]:
    """
    Make sure model is downloaded and RAM-safe to start.

    - pull if missing
    - if RAM is low, unload Whisper + previous Ollama models
    - after cleanup, allow a smaller absolute free-RAM floor
    - refuse start if still not enough free RAM
    """

    model_name = _normalize_model_name(model_name=model_name)

    ok, ollama_message = ensure_ollama_running(base_url=base_url)
    if not ok:
        return False, ollama_message

    if not is_model_downloaded(model_name=model_name, base_url=base_url):
        if progress_callback:
            progress_callback(f"مدل {model_name} دانلود نشده؛ در حال دانلود...")
        try:
            pull_model(
                model_name=model_name,
                base_url=base_url,
                progress_callback=progress_callback,
            )
        except Exception as exception:
            return False, f"دانلود مدل {model_name} ناموفق بود: {exception}"

        if not is_model_downloaded(model_name=model_name, base_url=base_url):
            return False, f"دانلود مدل {model_name} کامل به نظر نمی‌رسد!"

    fits, ram_message, _ = can_fit_model_in_ram(
        model_name=model_name,
        available_bytes=_effective_available_ram_bytes(),
    )
    if fits:
        try:
            import dtx_whisper as whisper_module

            whisper_module.clear_pending_freed_bytes()
        except Exception:
            pass
        return True, f"مدل {model_name} آماده است. {ram_message}"

    if progress_callback:
        progress_callback(
            "رم کافی نیست؛ در حال آزاد کردن Whisper و مدل‌های قبلی از رم..."
        )

    _release_whisper_for_ram()
    unloaded = unload_all_loaded_models(base_url=base_url)
    time.sleep(1.0)

    effective_available = _effective_available_ram_bytes()

    fits_preferred, ram_message_after, _ = can_fit_model_in_ram(
        model_name=model_name,
        available_bytes=effective_available,
    )
    if fits_preferred:
        unloaded_text = "، ".join(unloaded) if unloaded else "هیچ مدل Ollama"
        try:
            import dtx_whisper as whisper_module

            whisper_module.clear_pending_freed_bytes()
        except Exception:
            pass
        return True, (
            f"مدل {model_name} آماده است. "
            f"مدل‌های قبلی از رم خارج شد ({unloaded_text}). "
            f"{ram_message_after}"
        )

    fits_minimum, ram_message_min, _ = can_fit_model_in_ram(
        model_name=model_name,
        available_bytes=effective_available,
        margin_bytes=model_constants.RAM_ABSOLUTE_MIN_FREE_BYTES,
    )
    if fits_minimum:
        try:
            import dtx_whisper as whisper_module

            whisper_module.clear_pending_freed_bytes()
        except Exception:
            pass
        return True, (
            f"مدل {model_name} با حاشیه امن کمتر آماده شد تا مکالمه قطع نشود. "
            f"آزاد مؤثر تقریبی: {format_bytes(effective_available)}. "
            "اگر سیستم کند شد، مدل سبک‌تری انتخاب کنید."
        )

    needed_only = estimate_model_ram_bytes(model_name=model_name)
    if effective_available >= needed_only:
        try:
            import dtx_whisper as whisper_module

            whisper_module.clear_pending_freed_bytes()
        except Exception:
            pass
        return True, (
            f"مدل {model_name} با رم بسیار فشرده آماده شد. "
            f"آزاد مؤثر تقریبی: {format_bytes(effective_available)} | "
            f"برآورد خود مدل: {format_bytes(needed_only)}. "
            "پنجره‌های اضافی را ببندید؛ در غیر این صورت سیستم ممکن است کند شود."
        )

    return False, (
        f"برای جلوگیری از کند شدن/کرش سیستم، مدل {model_name} استارت نشد. "
        f"{ram_message_min} "
        f"{_suggest_lighter_models(model_name=model_name)}"
    )


if __name__ == "__main__":
    utility.display_just_one_error_message(
        message=utility.ERROR_MESSAGE_MODULE_IS_NOT_EXECUTED_DIRECTLY,
    )
