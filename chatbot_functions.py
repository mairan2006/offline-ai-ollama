"""
Chatbot Functions
"""

import base64
from pathlib import Path
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

import chatbot_constants as constants
import dt_analysis as analysis
import dt_files as files
import dt_history as history
import dt_llm_utility as llm_utility
import dt_recorder as recorder
import dt_tts as tts_router
import dt_tts_edge as tts_edge
import dtx_whisper as whisper_module
import model_constants as model_constants
from dt_ollama_manager import (
    can_fit_model_in_ram,
    clear_finished_download_job,
    ensure_ollama_running,
    format_bytes,
    get_available_ram_bytes,
    get_download_job,
    get_model_details,
    get_model_display_options,
    is_model_downloaded,
    prepare_model_for_use,
    start_model_download,
)
from dt_utility import format_seconds
from dtx_ollama import chat


def set_page_config() -> None:
    """Set Streamlit page config and RTL style."""

    st.set_page_config(
        page_title=constants.PAGE_TITLE,
        page_icon="◉",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    st.markdown(body=constants.STREAMLIT_STYLE, unsafe_allow_html=True)


def render_brand_header() -> None:
    """Product brand as the first-viewport hero signal."""

    st.markdown(body=constants.BRAND_HTML, unsafe_allow_html=True)


def render_chat_empty_state() -> None:
    """Soft empty state when there is no user/assistant turn yet."""

    has_turns = any(
        message.get(llm_utility.KEY_NAME_ROLE) != llm_utility.ROLE_SYSTEM
        for message in st.session_state.messages
    )
    if has_turns:
        return
    st.markdown(body=constants.EMPTY_CHAT_HTML, unsafe_allow_html=True)


def initial_session_state() -> None:
    """Initialize Streamlit session state."""

    history.init_db()

    if "model_name" not in st.session_state:
        st.session_state.model_name = constants.DEFAULT_MODEL_NAME

    if "messages" not in st.session_state:
        st.session_state.messages = [constants.SYSTEM_MESSAGE.copy()]

    if "ollama_ready" not in st.session_state:
        st.session_state.ollama_ready = False

    if "ollama_status_message" not in st.session_state:
        st.session_state.ollama_status_message = ""

    if "model_status_message" not in st.session_state:
        st.session_state.model_status_message = ""

    if "model_ready" not in st.session_state:
        st.session_state.model_ready = False

    if "model_options_cache" not in st.session_state:
        st.session_state.model_options_cache = []

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None

    if "history_notice" not in st.session_state:
        st.session_state.history_notice = ""

    if "history_title_hint" not in st.session_state:
        st.session_state.history_title_hint = ""

    if "history_select_box" not in st.session_state:
        st.session_state.history_select_box = -1

    if "_history_sync_id" not in st.session_state:
        st.session_state._history_sync_id = None

    if "_history_select_pending" not in st.session_state:
        st.session_state._history_select_pending = None

    if "file_analysis_result" not in st.session_state:
        st.session_state.file_analysis_result = ""

    if "file_analysis_source" not in st.session_state:
        st.session_state.file_analysis_source = ""

    if "voice_whisper_model" not in st.session_state:
        st.session_state.voice_whisper_model = "auto"

    if "voice_edge_voice" not in st.session_state:
        st.session_state.voice_edge_voice = tts_edge.VOICES_FEMALE[0]

    if "voice_tts_engine" not in st.session_state:
        st.session_state.voice_tts_engine = tts_router.ENGINE_EDGE

    if "voice_offline_voice" not in st.session_state:
        st.session_state.voice_offline_voice = ""

    if "voice_reply_mime" not in st.session_state:
        st.session_state.voice_reply_mime = "audio/mpeg"

    if "voice_max_seconds" not in st.session_state:
        st.session_state.voice_max_seconds = 15

    if "voice_last_transcript" not in st.session_state:
        st.session_state.voice_last_transcript = ""

    if "voice_reply_bytes" not in st.session_state:
        st.session_state.voice_reply_bytes = b""

    if "voice_autoplay" not in st.session_state:
        st.session_state.voice_autoplay = False

    if "voice_sent_token" not in st.session_state:
        st.session_state.voice_sent_token = ""

    if "voice_notice" not in st.session_state:
        st.session_state.voice_notice = ""

    if "voice_used_whisper" not in st.session_state:
        st.session_state.voice_used_whisper = ""

    if "voice_call_active" not in st.session_state:
        st.session_state.voice_call_active = False

    if "voice_call_use_browser" not in st.session_state:
        st.session_state.voice_call_use_browser = False

    if "pending_attachments" not in st.session_state:
        st.session_state.pending_attachments = []

    if "download_dialog_model" not in st.session_state:
        st.session_state.download_dialog_model = None

    if "history_delete_pending" not in st.session_state:
        st.session_state.history_delete_pending = None

    if "composer_nonce" not in st.session_state:
        st.session_state.composer_nonce = 0


def ensure_ollama_ready() -> bool:
    """Check Ollama and start it if needed. Cache result in session."""

    if st.session_state.ollama_ready:
        return True

    with st.spinner(text=constants.CHECKING_OLLAMA):
        ok, message = ensure_ollama_running()

    st.session_state.ollama_ready = ok
    st.session_state.ollama_status_message = message
    return ok


def refresh_model_options() -> list[tuple[str, str, bool]]:
    """Refresh dropdown model options from Ollama + catalog."""

    options = get_model_display_options()
    st.session_state.model_options_cache = options
    return options


def _request_history_select(conversation_id: Optional[int]) -> None:
    """
    Queue dropdown selection for the next sidebar render.

    Streamlit forbids writing widget keys after the widget exists; voice/chat
    persist runs after the sidebar selectbox, so we only set a pending value.
    """

    st.session_state._history_select_pending = (
        int(conversation_id) if conversation_id is not None else -1
    )


def _apply_history_select_pending() -> None:
    """Apply queued dropdown selection before the selectbox is created."""

    if "_history_select_pending" not in st.session_state:
        st.session_state._history_select_pending = None

    pending = st.session_state._history_select_pending
    if pending is None:
        return

    st.session_state.history_select_box = int(pending)
    st.session_state._history_select_pending = None
    st.session_state._history_sync_id = st.session_state.conversation_id


def start_new_conversation() -> None:
    """Start a fresh in-memory conversation (saved on first reply)."""

    st.session_state.messages = [constants.SYSTEM_MESSAGE.copy()]
    st.session_state.conversation_id = None
    st.session_state.history_title_hint = ""
    st.session_state._history_sync_id = None
    st.session_state.pending_attachments = []
    st.session_state.file_analysis_result = ""
    st.session_state.file_analysis_source = ""
    st.session_state.voice_last_transcript = ""
    st.session_state.voice_reply_bytes = b""
    st.session_state.voice_autoplay = False
    st.session_state.voice_notice = ""
    st.session_state.voice_call_active = False
    st.session_state.voice_call_use_browser = False
    st.session_state.voice_sent_token = ""
    st.session_state.download_dialog_model = None
    st.session_state.history_delete_pending = None
    # Bump chat_input widget key so leftover prompt/audio state is dropped.
    st.session_state.composer_nonce = int(st.session_state.get("composer_nonce") or 0) + 1
    _request_history_select(conversation_id=None)
    st.session_state.history_notice = constants.HISTORY_NEW


def clear_chat_history() -> None:
    """Alias used by older UI button name."""

    start_new_conversation()


def ensure_conversation_exists() -> int:
    """Create DB conversation if current chat has no id yet."""

    if st.session_state.conversation_id is not None:
        return int(st.session_state.conversation_id)

    conversation_id = history.create_conversation(
        model_name=st.session_state.model_name,
        title="گفتگوی جدید",
    )
    st.session_state.conversation_id = conversation_id
    return conversation_id


def persist_current_conversation(title_hint: str = "") -> int:
    """Save current messages into SQLite and sync history dropdown."""

    hint = (title_hint or st.session_state.history_title_hint or "").strip()
    conversation_id = ensure_conversation_exists()
    try:
        title = history.save_messages(
            conversation_id=conversation_id,
            messages=st.session_state.messages,
            model_name=st.session_state.model_name,
            title_hint=hint or None,
        )
    except Exception as exception:
        st.session_state.history_notice = (
            f"{constants.HISTORY_SAVE_FAILED} ({exception})"
        )
        raise

    if hint:
        st.session_state.history_title_hint = hint

    # Do not write history_select_box here — widget may already exist this run.
    _request_history_select(conversation_id=conversation_id)
    st.session_state.history_notice = (
        f"{constants.HISTORY_SAVED} #{conversation_id} | {title}"
    )
    return conversation_id


def load_conversation(conversation_id: int) -> None:
    """Load a conversation from SQLite into session."""

    conversation = history.get_conversation(conversation_id=conversation_id)
    if not conversation:
        st.session_state.history_notice = "گفتگوی مورد نظر پیدا نشد."
        return

    messages = history.get_messages(conversation_id=conversation_id)
    if not messages:
        messages = [constants.SYSTEM_MESSAGE.copy()]
    elif messages[0].get("role") != llm_utility.ROLE_SYSTEM:
        messages = [constants.SYSTEM_MESSAGE.copy()] + messages

    st.session_state.conversation_id = conversation_id
    st.session_state.messages = messages
    st.session_state.model_name = conversation.get(
        "model_name",
        st.session_state.model_name,
    )
    st.session_state.model_ready = False
    st.session_state.history_title_hint = str(conversation.get("title", "") or "")
    # Widget may already exist (dropdown on_change path); queue for next run.
    st.session_state._history_sync_id = conversation_id
    _request_history_select(conversation_id=conversation_id)
    st.session_state.voice_last_transcript = ""
    st.session_state.voice_reply_bytes = b""
    st.session_state.voice_call_active = False
    st.session_state.voice_call_use_browser = False
    st.session_state.pending_attachments = []
    st.session_state.history_notice = (
        f"{constants.HISTORY_LOADED} #{conversation_id} | "
        f"{conversation.get('title', '')} | "
        f"{len([m for m in messages if m.get('role') != llm_utility.ROLE_SYSTEM])} پیام"
    )


def prepare_selected_model(model_name: str) -> bool:
    """Download if needed and apply RAM policy before using model."""

    status_box = st.empty()

    def progress_callback(message: str) -> None:
        status_box.info(body=message)

    with st.spinner(text=constants.PREPARING_MODEL):
        ok, message = prepare_model_for_use(
            model_name=model_name,
            progress_callback=progress_callback,
        )

    status_box.empty()
    st.session_state.model_ready = ok
    st.session_state.model_status_message = message
    return ok


def _history_export_filename(title: str, conversation_id: int) -> str:
    """Build a safe download filename for one conversation export."""

    safe_stem = "".join(
        ch if ch.isalnum() or ch in ("-", "_") else "_"
        for ch in title
    ).strip("_") or f"chat_{conversation_id}"
    return f"{safe_stem}_{conversation_id}.json"


def _trigger_json_download(payload: str, file_name: str) -> None:
    """Start a browser download for a JSON string (sidebar-safe)."""

    b64 = base64.b64encode(payload.encode("utf-8")).decode("ascii")
    safe_name = file_name.replace('"', "").replace("'", "")
    components.html(
        f"""
        <html><body>
        <a id="oa-export-link"
           href="data:application/json;charset=utf-8;base64,{b64}"
           download="{safe_name}">download</a>
        <script>
          document.getElementById("oa-export-link").click();
        </script>
        </body></html>
        """,
        height=0,
    )


def _dismiss_history_delete_dialog() -> None:
    """Clear pending history delete when the modal is dismissed."""

    st.session_state.history_delete_pending = None


@st.dialog(
    constants.HISTORY_DELETE_CONFIRM_TITLE,
    width="small",
    on_dismiss=_dismiss_history_delete_dialog,
)
def open_history_delete_dialog() -> None:
    """Ask for confirmation before deleting one chat or all history."""

    pending = st.session_state.get("history_delete_pending") or {}
    mode = str(pending.get("mode") or "")
    title = str(pending.get("title") or "گفتگو").strip() or "گفتگو"

    if mode == "all":
        st.markdown(
            body=(
                f'<div dir="rtl">{constants.HISTORY_DELETE_CONFIRM_ALL}</div>'
            ),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            body=(
                f'<div dir="rtl">{constants.HISTORY_DELETE_CONFIRM_ONE}'
                f"<br/><strong>{title}</strong></div>"
            ),
            unsafe_allow_html=True,
        )

    col_yes, col_no = st.columns(2, gap="small")
    with col_yes:
        if st.button(
            label=constants.HISTORY_DELETE_CONFIRM_YES,
            key="hist_delete_confirm_yes",
            use_container_width=True,
            type="primary",
        ):
            if mode == "all":
                history.delete_all_conversations()
                start_new_conversation()
                st.session_state.history_notice = constants.HISTORY_DELETED_ALL
            else:
                conversation_id = int(pending.get("id") or 0)
                if conversation_id:
                    history.delete_conversation(conversation_id=conversation_id)
                    if st.session_state.conversation_id == conversation_id:
                        start_new_conversation()
                    st.session_state.history_notice = constants.HISTORY_DELETED
            st.session_state.history_delete_pending = None
            st.rerun()
    with col_no:
        if st.button(
            label=constants.HISTORY_DELETE_CONFIRM_NO,
            key="hist_delete_confirm_no",
            use_container_width=True,
        ):
            st.session_state.history_delete_pending = None
            st.rerun()


def render_history_section() -> None:
    """Render conversation history as dense sidebar buttons (no new-tab links)."""

    conversations = history.list_conversations(limit=50)
    if not conversations:
        st.caption(body=constants.HISTORY_EMPTY)
    else:
        for item in conversations:
            conversation_id = int(item["id"])
            title = str(item.get("title") or "گفتگو").strip() or "گفتگو"
            short_title = title[:32] + "…" if len(title) > 32 else title
            is_active = st.session_state.conversation_id == conversation_id
            col_open, col_export, col_del = st.columns(
                [0.70, 0.15, 0.15],
                gap="small",
            )
            with col_open:
                label = f"• {short_title}" if is_active else short_title
                if st.button(
                    label=label,
                    key=f"hist_open_{conversation_id}",
                    use_container_width=True,
                ):
                    if not is_active:
                        load_conversation(conversation_id=conversation_id)
                    st.rerun()
            with col_export:
                if st.button(
                    label=constants.HISTORY_EXPORT_ICON,
                    key=f"hist_export_{conversation_id}",
                    help=constants.HISTORY_EXPORT_HELP,
                    use_container_width=True,
                ):
                    export_json = history.export_conversation_json(
                        conversation_id=conversation_id,
                    )
                    _trigger_json_download(
                        payload=export_json,
                        file_name=_history_export_filename(
                            title=short_title,
                            conversation_id=conversation_id,
                        ),
                    )
                    st.session_state.history_notice = "خروجی JSON آماده شد."
            with col_del:
                if st.button(
                    label=constants.HISTORY_DELETE_ICON,
                    key=f"hist_del_{conversation_id}",
                    use_container_width=True,
                ):
                    st.session_state.history_delete_pending = {
                        "mode": "one",
                        "id": conversation_id,
                        "title": title,
                    }
                    st.rerun()

    if conversations and st.button(
        label=constants.HISTORY_DELETE_ALL,
        use_container_width=True,
        key="hist_delete_all",
    ):
        st.session_state.history_delete_pending = {"mode": "all"}
        st.rerun()

    if st.session_state.get("history_delete_pending"):
        open_history_delete_dialog()

    if st.session_state.history_notice:
        st.caption(body=st.session_state.history_notice)


def apply_selected_model(selected_name: str) -> None:
    """Switch to a downloaded model and apply RAM policy."""

    if selected_name == st.session_state.model_name and st.session_state.model_ready:
        return

    previous_model = st.session_state.model_name
    st.session_state.model_name = selected_name
    st.session_state.model_ready = False

    ok = prepare_selected_model(model_name=selected_name)
    if ok:
        if st.session_state.conversation_id is not None:
            persist_current_conversation()
        return

    st.session_state.model_name = previous_model
    st.session_state.model_ready = False
    st.error(body=st.session_state.model_status_message)
    st.rerun()


def _downloaded_map() -> dict[str, bool]:
    """Map model name -> downloaded from cached options."""

    return {
        str(name): bool(is_downloaded)
        for name, _label, is_downloaded in st.session_state.model_options_cache
    }


def _label_map() -> dict[str, str]:
    """Map model name -> short dropdown label."""

    return {
        str(name): str(label)
        for name, label, _is_downloaded in st.session_state.model_options_cache
    }


def _on_model_select_change() -> None:
    """Downloaded models switch immediately; others open the download dialog."""

    selected = str(st.session_state.get("sidebar_model_select") or "")
    current = str(st.session_state.model_name or "")
    if not selected or selected == current:
        return

    if _downloaded_map().get(selected, False):
        apply_selected_model(selected_name=selected)
        return

    st.session_state.download_dialog_model = selected
    # Reset selectbox to the active model (on_change runs before the widget).
    st.session_state.sidebar_model_select = current


def _dismiss_download_dialog() -> None:
    """Clear dialog target when the user closes the modal."""

    st.session_state.download_dialog_model = None


@st.fragment(run_every=1.0)
def _render_download_progress(model_name: str) -> None:
    """Live percent panel; job state survives closing/reopening the dialog."""

    job = get_download_job(model_name=model_name)
    if not job:
        st.caption(body=constants.DOWNLOAD_WAITING)
        return

    status = str(job.get("status") or "")
    percent = float(job.get("percent") or 0.0)
    message = str(job.get("message") or "")
    bytes_done = int(job.get("bytes_done") or 0)
    bytes_total = int(job.get("bytes_total") or 0)

    st.progress(min(max(percent / 100.0, 0.0), 1.0))
    st.markdown(
        body=(
            f'<div class="oa-dl-percent" dir="rtl">'
            f"{percent:.0f}٪ — {message}"
            f"</div>"
        ),
        unsafe_allow_html=True,
    )
    if bytes_total > 0:
        st.caption(
            body=f"{format_bytes(bytes_done)} / {format_bytes(bytes_total)}"
        )

    if status == "done":
        if not any(
            name == model_name and is_dl
            for name, _label, is_dl in st.session_state.model_options_cache
        ):
            refresh_model_options()
        st.success(body=constants.DOWNLOAD_DONE)
        if st.button(
            label=constants.DOWNLOAD_USE_MODEL,
            key=f"dl_use_{model_name}",
            use_container_width=True,
            type="primary",
        ):
            clear_finished_download_job(model_name=model_name)
            refresh_model_options()
            st.session_state.download_dialog_model = None
            st.session_state.sidebar_model_select = model_name
            apply_selected_model(selected_name=model_name)
            st.rerun()
    elif status == "error":
        error_text = str(job.get("error") or "")
        st.error(
            body=(
                f"{constants.DOWNLOAD_FAILED}"
                + (f" ({error_text})" if error_text else "")
            )
        )
        if st.button(
            label=constants.DOWNLOAD_RETRY,
            key=f"dl_retry_{model_name}",
            use_container_width=True,
        ):
            clear_finished_download_job(model_name=model_name)
            start_model_download(model_name=model_name)
            st.rerun()


@st.dialog(
    constants.DOWNLOAD_DIALOG_TITLE,
    width="small",
    on_dismiss=_dismiss_download_dialog,
)
def open_model_download_dialog(model_name: str) -> None:
    """Modal download UI with persistent percent progress."""

    details = get_model_details(model_name=model_name)
    st.markdown(
        body=(
            f'<div class="oa-dl-head" dir="rtl">'
            f"<strong>{details.get('title') or model_name}</strong>"
            f"<br/><span>{model_name}</span>"
            f"</div>"
        ),
        unsafe_allow_html=True,
    )
    st.caption(
        body=(
            f"{constants.DOWNLOAD_SIZE_LABEL}: "
            f"{details.get('download_label', '—')} | "
            f"{constants.RAM_NEED_LABEL}: "
            f"{details.get('ram_label', '—')}"
        )
    )

    if is_model_downloaded(model_name=model_name):
        st.success(body=constants.DOWNLOADED_YES)
        if st.button(
            label=constants.DOWNLOAD_USE_MODEL,
            key=f"dl_already_{model_name}",
            use_container_width=True,
            type="primary",
        ):
            refresh_model_options()
            st.session_state.download_dialog_model = None
            st.session_state.sidebar_model_select = model_name
            apply_selected_model(selected_name=model_name)
            st.rerun()
        return

    job = get_download_job(model_name=model_name)
    if not job:
        started, notice = start_model_download(model_name=model_name)
        if not started and "از قبل در حال اجراست" not in notice:
            st.warning(body=notice)

    _render_download_progress(model_name=model_name)

    if st.button(
        label=constants.DOWNLOAD_CLOSE,
        key=f"dl_close_{model_name}",
        use_container_width=True,
    ):
        st.session_state.download_dialog_model = None
        st.rerun()


def render_model_selector(key: str = "sidebar_model_select") -> None:
    """Model selectbox for the sidebar (under new-chat)."""

    if not st.session_state.ollama_ready:
        return

    if not st.session_state.model_options_cache:
        refresh_model_options()

    options = st.session_state.model_options_cache
    if not options:
        return

    names = [item[0] for item in options]
    current_name = st.session_state.model_name
    if current_name not in names:
        names = [current_name] + names

    labels = _label_map()
    if key not in st.session_state:
        st.session_state[key] = current_name
    elif st.session_state.get(key) not in names:
        st.session_state[key] = current_name

    st.selectbox(
        label=constants.SELECT_YOUR_MODEL,
        options=names,
        key=key,
        format_func=lambda name: labels.get(str(name), f"🟢 {name}"),
        label_visibility="collapsed",
        on_change=_on_model_select_change,
    )


def render_composer() -> None:
    """Attachment chips + voice icon dock + download dialog."""

    render_attachment_preview()
    render_voice_call_icon()

    pending = st.session_state.get("download_dialog_model")
    if pending:
        open_model_download_dialog(model_name=str(pending))

    notice = str(st.session_state.get("voice_notice") or "").strip()
    if notice:
        st.info(body=notice)
        st.session_state.voice_notice = ""

    if st.session_state.voice_call_use_browser:
        browser_audio = st.audio_input(
            label=constants.VOICE_BROWSER_LABEL,
            key="voice_call_browser_audio",
        )
        if browser_audio is not None:
            audio_bytes = browser_audio.getvalue() or b""
            audio_token = (
                f"{getattr(browser_audio, 'name', 'browser.wav')}:"
                f"{len(audio_bytes)}"
            )
            if (
                len(audio_bytes) > 0
                and st.session_state.voice_sent_token != audio_token
                and st.button(
                    label=constants.VOICE_BROWSER_SEND,
                    key="voice_call_browser_send",
                    use_container_width=True,
                )
            ):
                try:
                    browser_name = str(
                        getattr(browser_audio, "name", "") or "browser.wav"
                    )
                    if Path(browser_name).suffix.lower() not in {
                        ".wav",
                        ".mp3",
                        ".m4a",
                        ".ogg",
                        ".webm",
                    }:
                        browser_name = "browser.wav"
                    saved_path = recorder.save_audio_bytes(
                        file_name=browser_name,
                        file_bytes=audio_bytes,
                    )
                    st.session_state.voice_sent_token = audio_token
                    st.session_state.voice_call_use_browser = False
                    process_voice_audio(audio_path=saved_path)
                except Exception as exception:
                    st.session_state.voice_notice = (
                        "ارسال صدای مرورگر ناموفق بود. "
                        f"({exception})"
                    )
                    st.rerun()


def run_voice_conversation_turn() -> None:
    """One speak→listen turn: system mic until silence, then STT→LLM→TTS."""

    if not st.session_state.model_ready:
        ok = prepare_selected_model(model_name=st.session_state.model_name)
        if not ok:
            st.session_state.voice_notice = (
                st.session_state.model_status_message
                or constants.VOICE_CALL_NO_MODEL
            )
            return

    mic_name = recorder.get_default_input_device_name()
    if not mic_name:
        st.session_state.voice_call_use_browser = True
        st.session_state.voice_notice = constants.VOICE_NO_MIC
        return

    try:
        with st.spinner(text=constants.VOICE_RECORD_SPINNER):
            recorded_path = recorder.record_until_silence(
                max_seconds=float(st.session_state.voice_max_seconds or 15),
            )
        st.session_state.voice_call_use_browser = False
        process_voice_audio(audio_path=recorded_path)
    except Exception as exception:
        st.session_state.voice_call_use_browser = True
        st.session_state.voice_notice = (
            "ضبط با میکروفون سیستم ناموفق بود. از ضبط مرورگر استفاده کنید. "
            f"({exception})"
        )


def render_voice_call_icon() -> None:
    """Hidden Streamlit button + in-box proxy icon beside + / mic / send."""

    if st.button(
        label=constants.VOICE_CALL_ICON,
        key="composer_voice_call",
        help=constants.VOICE_CALL_HINT,
    ):
        st.session_state.voice_call_active = True
        run_voice_conversation_turn()
        st.rerun()
    _inject_voice_proxy_in_composer()


def _inject_voice_proxy_in_composer() -> None:
    """
    Place a clickable proxy inside the native chat_input action cluster.

    Does not move React-managed nodes (avoids freezes); only proxies .click().
    """

    import streamlit.components.v1 as components

    components.html(
        html="""
<script>
(function () {
  const doc = window.parent.document;
  function place() {
    const realBtn = doc.querySelector('[class*="st-key-composer_voice_call"] button');
    const row = doc.querySelector('[data-testid="stChatInput"] > div > div');
    if (!realBtn || !row || !row.children.length) return;
    const cluster = row.children[row.children.length - 1];
    if (!cluster) return;
    let proxy = doc.getElementById('oa-voice-proxy');
    if (!proxy) {
      proxy = doc.createElement('button');
      proxy.id = 'oa-voice-proxy';
      proxy.type = 'button';
      proxy.setAttribute('aria-label', 'مکالمه صوتی');
      proxy.title = 'مکالمه صوتی — صحبت کنید، پاسخ با صدا پخش می‌شود';
      proxy.innerHTML =
        '<span class="material-symbols-rounded" aria-hidden="true">headphones</span>';
      proxy.addEventListener('click', function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        const btn = doc.querySelector('[class*="st-key-composer_voice_call"] button');
        if (btn) btn.click();
      });
    }
    const mic = cluster.querySelector('[data-testid="stChatInputMicButton"]');
    if (mic) {
      if (proxy.parentElement !== cluster || proxy.nextElementSibling !== mic) {
        cluster.insertBefore(proxy, mic);
      }
    } else if (proxy.parentElement !== cluster) {
      cluster.appendChild(proxy);
    }
  }
  place();
  setTimeout(place, 40);
  setTimeout(place, 180);
})();
</script>
        """,
        height=0,
        width=0,
    )


def render_attachment_preview() -> None:
    """Show pending attachments as chips — preview only, no suggestions."""

    items = list(st.session_state.pending_attachments or [])
    if not items:
        return

    chips_html: list[str] = ['<div class="oa-chips" dir="rtl">']
    for item in items:
        name = str(item.get("name", "فایل"))
        kind = str(item.get("kind", ""))
        safe_name = (
            str(name)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        chips_html.append(
            f'<span class="oa-chip">{safe_name} <small>{kind}</small></span>'
        )
    chips_html.append("</div>")
    st.markdown(body="".join(chips_html), unsafe_allow_html=True)
    if st.button(label=constants.ATTACH_REMOVE, key="clear_pending_attachments"):
        clear_pending_attachments()
        st.rerun()


def render_sidebar() -> None:
    """Cursor-like sidebar: brand, new chat, compact history, light settings."""

    with st.sidebar:
        st.markdown(body=constants.SIDEBAR_BRAND_HTML, unsafe_allow_html=True)

        st.button(
            label=constants.CLEAR_CHAT,
            use_container_width=True,
            key="sidebar_new_chat",
            type="primary",
            on_click=start_new_conversation,
            help=constants.HISTORY_NEW,
        )

        st.markdown(
            body='<div class="oa-side-model" dir="rtl">',
            unsafe_allow_html=True,
        )
        render_model_selector(key="sidebar_model_select")
        st.markdown(body="</div>", unsafe_allow_html=True)

        render_history_section()

        with st.expander(label=constants.SETTINGS, expanded=False):
            if st.session_state.ollama_ready:
                st.caption(
                    body=st.session_state.ollama_status_message or "Ollama آماده است"
                )
            available_ram = get_available_ram_bytes()
            st.caption(
                body=(
                    f"رم: {format_bytes(available_ram)} | "
                    f"مدل: {st.session_state.model_name}"
                )
            )
            if st.button(label=constants.REFRESH_MODELS, use_container_width=True):
                refresh_model_options()
                st.session_state.model_ready = False
                st.rerun()
            whisper_options = ["auto", "tiny", "base", "small", "medium", "turbo"]
            if st.session_state.voice_whisper_model not in whisper_options:
                st.session_state.voice_whisper_model = "auto"
            st.selectbox(
                label=constants.VOICE_WHISPER_LABEL,
                options=whisper_options,
                key="voice_whisper_model",
            )
            engine_options = tts_router.ENGINE_OPTIONS
            st.selectbox(
                label=constants.VOICE_TTS_ENGINE_LABEL,
                options=engine_options,
                format_func=lambda name: (
                    constants.VOICE_TTS_EDGE
                    if name == tts_router.ENGINE_EDGE
                    else constants.VOICE_TTS_OFFLINE
                ),
                key="voice_tts_engine",
            )
            st.caption(body="مکالمه صوتی:")
            browser_audio = st.audio_input(label=constants.VOICE_BROWSER_LABEL)
            if browser_audio is not None:
                audio_bytes = browser_audio.getvalue()
                audio_token = (
                    f"{getattr(browser_audio, 'name', 'browser.wav')}:"
                    f"{len(audio_bytes)}"
                )
                if st.button(
                    label=constants.VOICE_BROWSER_SEND,
                    key="sidebar_voice_send",
                ):
                    if st.session_state.voice_sent_token == audio_token:
                        st.info(body=constants.VOICE_BROWSER_ALREADY)
                    else:
                        try:
                            browser_name = str(
                                getattr(browser_audio, "name", "") or "browser.wav"
                            )
                            if Path(browser_name).suffix.lower() not in {
                                ".wav",
                                ".mp3",
                                ".m4a",
                                ".ogg",
                                ".webm",
                            }:
                                browser_name = "browser.wav"
                            saved_path = recorder.save_audio_bytes(
                                file_name=browser_name,
                                file_bytes=audio_bytes,
                            )
                            process_voice_audio(audio_path=saved_path)
                            st.session_state.voice_sent_token = audio_token
                            st.rerun()
                        except Exception as exception:
                            st.error(
                                body=(
                                    "ارسال صدای مرورگر ناموفق بود. "
                                    f"({exception})"
                                )
                            )

        st.markdown(body=constants.ABOUT, unsafe_allow_html=True)


def parse_chat_input(chat_value) -> tuple[str, list, Optional[object]]:
    """Return text, uploaded files, optional audio from st.chat_input."""

    if chat_value is None:
        return "", [], None

    if isinstance(chat_value, str):
        return chat_value.strip(), [], None

    text = str(getattr(chat_value, "text", "") or "").strip()
    uploaded = list(getattr(chat_value, "files", None) or [])
    audio = getattr(chat_value, "audio", None)

    # Ignore empty audio placeholders so text+file submits are not swallowed.
    if audio is not None:
        try:
            audio_size = len(audio.getvalue() or b"")
        except Exception:
            audio_size = 0
        if audio_size <= 0:
            audio = None

    return text, uploaded, audio


def handle_chat_input_value(chat_value) -> None:
    """
    Process native chat_input submission with immediate UI feedback.

    Shows the user prompt right away, then a thinking status (Stop via
    chat_input submit_mode) while the model prepares the answer.
    """

    text, uploaded_files, audio = parse_chat_input(chat_value)

    if audio is not None:
        try:
            audio_bytes = audio.getvalue() or b""
            if len(audio_bytes) <= 0:
                st.warning(body="صوت خالی بود؛ دوباره با میکروفون ضبط کنید.")
                return
            audio_name = str(getattr(audio, "name", "") or "browser.webm")
            if Path(audio_name).suffix.lower() not in {
                ".wav",
                ".mp3",
                ".m4a",
                ".ogg",
                ".webm",
            }:
                audio_name = "browser.webm"
            saved_path = recorder.save_audio_bytes(
                file_name=audio_name,
                file_bytes=audio_bytes,
            )
            process_voice_audio(audio_path=saved_path)
        except Exception as exception:
            st.error(body=f"تبدیل گفتار به متن ناموفق بود. ({exception})")
        return

    if uploaded_files and not text:
        st.session_state.pending_attachments = store_uploaded_files(
            uploaded_files=uploaded_files,
        )
        st.rerun()
        return

    if not text:
        return

    run_chat_turn_with_ui(
        text=text,
        uploaded_files=uploaded_files or None,
    )


def clear_pending_attachments() -> None:
    """Clear queued file attachments."""

    st.session_state.pending_attachments = []


def store_uploaded_files(uploaded_files: list) -> list[dict]:
    """Save Streamlit uploaded files and return attachment metadata."""

    stored: list[dict] = []
    for uploaded in uploaded_files:
        name = str(getattr(uploaded, "name", "") or "file")
        raw = uploaded.getvalue()
        path = files.save_uploaded_file(file_name=name, file_bytes=raw)
        kind = files.detect_file_kind(file_name=name)
        stored.append(
            {
                "name": name,
                "path": str(path),
                "kind": kind,
                "size": len(raw),
            }
        )
    return stored


def _build_file_prompt_turn(
    text: str,
    pending: list[dict],
) -> tuple[str, str, str]:
    """
    Apply user prompt to pending files.

    Returns user_visible, assistant_text, title_hint.
    """

    unsupported = [item for item in pending if item.get("kind") == "unknown"]
    if unsupported:
        names = "، ".join(str(item.get("name", "")) for item in unsupported)
        raise RuntimeError(f"{constants.ATTACH_UNSUPPORTED} ({names})")

    answer_parts: list[str] = []
    display_names: list[str] = []
    for item in pending:
        name = str(item.get("name", "فایل"))
        path = Path(str(item.get("path", "")))
        display_names.append(name)
        result, unloaded = analysis.apply_prompt_to_file(
            file_path=path,
            file_name=name,
            user_prompt=text,
            model_name=st.session_state.model_name,
            whisper_model=st.session_state.voice_whisper_model,
        )
        if unloaded:
            st.session_state.model_ready = False
        if len(pending) > 1:
            answer_parts.append(f"### {name}\n{result}")
        else:
            answer_parts.append(result)

    user_visible = (
        f"{constants.HISTORY_FILE_PREFIX} "
        + "، ".join(display_names)
        + f"\n{text}"
    )
    assistant_text = "\n\n".join(answer_parts)
    title_hint = f"{constants.HISTORY_FILE_PREFIX} {display_names[0]}"
    return user_visible, assistant_text, title_hint


def run_chat_turn_with_ui(
    text: str,
    uploaded_files: Optional[list] = None,
) -> None:
    """
    Show user prompt immediately, think with status, then show the answer.

    Works with st.chat_input(submit_mode=\"stop\") so the send arrow becomes Stop
    while this function runs.
    """

    text = (text or "").strip()
    new_files = list(uploaded_files or [])
    if new_files:
        st.session_state.pending_attachments = store_uploaded_files(new_files)

    pending = list(st.session_state.pending_attachments or [])
    if not text:
        return

    use_files = bool(pending)
    if use_files:
        user_visible = (
            f"{constants.HISTORY_FILE_PREFIX} "
            + "، ".join(str(item.get("name", "فایل")) for item in pending)
            + f"\n{text}"
        )
        title_hint = (
            f"{constants.HISTORY_FILE_PREFIX} "
            f"{pending[0].get('name', 'فایل')}"
        )
    else:
        user_visible = text
        title_hint = ""

    st.session_state.messages.append(
        {
            llm_utility.KEY_NAME_ROLE: llm_utility.ROLE_USER,
            llm_utility.KEY_NAME_CONTENT: user_visible,
        }
    )

    # Immediate echo (previous messages were already rendered above).
    with st.chat_message(name="user"):
        st.markdown(body=user_visible)

    assistant_text = ""
    with st.chat_message(name="assistant"):
        with st.status(
            label=constants.THINKING_STATUS,
            expanded=True,
        ) as status:
            st.write(constants.THINKING_STATUS_HINT)
            try:
                if use_files:
                    _user_vis, assistant_text, title_hint = _build_file_prompt_turn(
                        text=text,
                        pending=pending,
                    )
                    clear_pending_attachments()
                else:
                    assistant_text = generate_assistant_reply(
                        title_hint=title_hint,
                        persist=False,
                    )
                status.update(
                    label=constants.THINKING_STATUS_DONE,
                    state="complete",
                    expanded=False,
                )
            except Exception:
                # Roll back the optimistic user turn on hard failure.
                if (
                    st.session_state.messages
                    and st.session_state.messages[-1].get(llm_utility.KEY_NAME_ROLE)
                    == llm_utility.ROLE_USER
                ):
                    st.session_state.messages.pop()
                status.update(label="خطا در آماده‌سازی پاسخ", state="error")
                raise

        if assistant_text:
            st.markdown(body=assistant_text)

    if not assistant_text:
        if (
            st.session_state.messages
            and st.session_state.messages[-1].get(llm_utility.KEY_NAME_ROLE)
            == llm_utility.ROLE_USER
        ):
            st.session_state.messages.pop()
        st.warning(body=constants.ERROR_NO_ANSWER)
        return

    if use_files:
        st.session_state.messages.append(
            {
                llm_utility.KEY_NAME_ROLE: llm_utility.ROLE_ASSISTANT,
                llm_utility.KEY_NAME_CONTENT: assistant_text,
            }
        )
    # Normal chat already appended assistant inside generate_assistant_reply.

    persist_current_conversation(title_hint=title_hint)
    # Refresh so sidebar history and the main message list stay in sync.
    st.rerun()


def handle_chat_submission(text: str, uploaded_files: Optional[list] = None) -> None:
    """Backward-compatible wrapper around the UI chat turn."""

    run_chat_turn_with_ui(text=text, uploaded_files=uploaded_files)


def add_analysis_result_to_chat(result_text: str, source_name: str) -> None:
    """Append analysis result into current chat and persist."""

    safe_name = str(source_name or "فایل").strip() or "فایل"
    user_note = (
        f"{constants.HISTORY_FILE_PREFIX} نتیجه تحلیل فایل «{safe_name}» "
        "را به گفتگو اضافه کردم."
    )
    st.session_state.messages.append(
        {
            llm_utility.KEY_NAME_ROLE: llm_utility.ROLE_USER,
            llm_utility.KEY_NAME_CONTENT: user_note,
        }
    )
    st.session_state.messages.append(
        {
            llm_utility.KEY_NAME_ROLE: llm_utility.ROLE_ASSISTANT,
            llm_utility.KEY_NAME_CONTENT: result_text,
        }
    )
    persist_current_conversation(
        title_hint=f"{constants.HISTORY_FILE_PREFIX} {safe_name}",
    )


def render_file_analysis_section() -> None:
    """Render upload + analysis actions for image/pdf/text/audio."""

    with st.container():
        uploaded = st.file_uploader(
            label=constants.FILES_UPLOAD_LABEL,
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp",
                "bmp",
                "pdf",
                "txt",
                "md",
                "markdown",
                "csv",
                "mp3",
                "wav",
                "m4a",
                "ogg",
            ],
            accept_multiple_files=False,
        )

        if not uploaded:
            st.caption(body=constants.FILES_NO_FILE)
            if st.session_state.file_analysis_result:
                st.markdown(body=f"**{constants.FILES_RESULT_LABEL}:**")
                st.write(st.session_state.file_analysis_result)
            return

        kind = files.detect_file_kind(file_name=uploaded.name)
        st.caption(body=f"نوع تشخیص‌داده‌شده: {kind} | فایل: {uploaded.name}")

        if kind == "unknown":
            st.error(body=constants.FILES_UNSUPPORTED)
            return

        file_bytes = uploaded.getvalue()
        saved_path = files.save_uploaded_file(
            file_name=uploaded.name,
            file_bytes=file_bytes,
        )
        model_name = st.session_state.model_name

        if kind == "image":
            if st.button(label=constants.FILES_ANALYZE_IMAGE):
                with st.spinner(text="در حال تحلیل تصویر..."):
                    try:
                        result = analysis.analyze_image(
                            image_path=saved_path,
                            model_name=model_name,
                        )
                        st.session_state.file_analysis_result = result
                        st.session_state.file_analysis_source = uploaded.name
                    except Exception as exception:
                        st.error(body=str(exception))

        elif kind in {"pdf", "text"}:
            col1, col2, col3 = st.columns(3)
            with col1:
                do_summary = st.button(label=constants.FILES_SUMMARIZE)
            with col2:
                do_fa = st.button(label=constants.FILES_TRANSLATE_FA)
            with col3:
                do_en = st.button(label=constants.FILES_TRANSLATE_EN)

            try:
                if do_summary:
                    with st.spinner(text="در حال خلاصه‌سازی..."):
                        result = analysis.summarize_document(
                            file_path=saved_path,
                            model_name=model_name,
                        )
                        st.session_state.file_analysis_result = result
                        st.session_state.file_analysis_source = uploaded.name
                elif do_fa:
                    with st.spinner(text="در حال ترجمه به فارسی..."):
                        result = analysis.translate_document(
                            file_path=saved_path,
                            model_name=model_name,
                            to_persian=True,
                        )
                        st.session_state.file_analysis_result = result
                        st.session_state.file_analysis_source = uploaded.name
                elif do_en:
                    with st.spinner(text="در حال ترجمه به انگلیسی..."):
                        result = analysis.translate_document(
                            file_path=saved_path,
                            model_name=model_name,
                            to_persian=False,
                        )
                        st.session_state.file_analysis_result = result
                        st.session_state.file_analysis_source = uploaded.name
            except Exception as exception:
                st.error(body=str(exception))

        elif kind == "audio":
            if st.button(label=constants.FILES_TRANSCRIBE):
                with st.spinner(text="در حال تبدیل صوت به متن با Whisper..."):
                    try:
                        text, elapsed, unloaded, used_model = analysis.transcribe_audio(
                            audio_path=saved_path,
                            model_name=st.session_state.voice_whisper_model,
                        )
                        if unloaded:
                            st.session_state.model_ready = False
                        st.session_state.voice_used_whisper = used_model
                        result = (
                            f"متن استخراج‌شده از صوت:\n\n{text}\n\n"
                            f"(زمان پردازش: {format_seconds(seconds=elapsed)})"
                        )
                        st.session_state.file_analysis_result = result
                        st.session_state.file_analysis_source = uploaded.name
                    except Exception as exception:
                        st.error(body=str(exception))

        if st.session_state.file_analysis_result:
            st.markdown(body=f"**{constants.FILES_RESULT_LABEL}:**")
            st.write(st.session_state.file_analysis_result)
            if st.button(label=constants.FILES_ADD_TO_CHAT):
                add_analysis_result_to_chat(
                    result_text=st.session_state.file_analysis_result,
                    source_name=st.session_state.file_analysis_source
                    or uploaded.name,
                )
                st.success(body="نتیجه به گفتگو اضافه و ذخیره شد.")
                st.rerun()


def render_chat_messages() -> None:
    """Render previous chat messages."""

    for message in st.session_state.messages:
        role = message.get(llm_utility.KEY_NAME_ROLE)
        content = message.get(llm_utility.KEY_NAME_CONTENT, "")

        if role == llm_utility.ROLE_SYSTEM:
            continue

        avatar_role = "user" if role == llm_utility.ROLE_USER else "assistant"
        with st.chat_message(name=avatar_role):
            st.markdown(body=content)


def _free_whisper_if_chat_needs_ram() -> None:
    """Release Whisper before chat so Ollama can reclaim RAM."""

    if not whisper_module.is_model_loaded():
        return

    whisper_module.release_model()
    st.session_state.model_ready = False


def render_voice_player() -> None:
    """Play the latest spoken reply. Autoplay only for a fresh answer."""

    audio_bytes = st.session_state.voice_reply_bytes or b""
    if not audio_bytes:
        return

    autoplay = bool(st.session_state.voice_autoplay)
    st.session_state.voice_autoplay = False
    mime = st.session_state.voice_reply_mime or "audio/mpeg"
    st.caption(body="پاسخ صوتی:")
    st.audio(data=audio_bytes, format=mime, autoplay=autoplay)


def process_voice_audio(audio_path: Path) -> None:
    """STT, chat answer, then TTS playback (Edge or offline)."""

    st.session_state.voice_notice = ""

    with st.spinner(text=constants.VOICE_STT_SPINNER):
        text, _elapsed, unloaded, used_model = analysis.transcribe_audio(
            audio_path=audio_path,
            model_name=st.session_state.voice_whisper_model,
        )
    if unloaded:
        st.session_state.model_ready = False
    st.session_state.voice_used_whisper = used_model

    text = (text or "").strip()
    st.session_state.voice_last_transcript = text

    # Always free Whisper before chat; both models cannot stay in RAM together
    # on typical 16GB machines.
    if whisper_module.is_model_loaded():
        whisper_module.release_model()
        st.session_state.model_ready = False

    if not text:
        st.session_state.voice_notice = constants.VOICE_EMPTY_TRANSCRIPT
        return

    voice_user_text = f"{constants.HISTORY_VOICE_PREFIX} {text}"
    voice_title = f"{constants.HISTORY_VOICE_PREFIX} {text}"

    try:
        with st.spinner(text="در حال فکر کردن..."):
            answer, _elapsed_text = get_assistant_answer(
                user_prompt=voice_user_text,
                title_hint=voice_title,
            )
    except Exception as exception:
        st.session_state.voice_notice = (
            "پاسخ مدل ساخته نشد. "
            f"{exception}"
        )
        return

    if answer == constants.ERROR_NO_ANSWER:
        st.session_state.voice_notice = constants.ERROR_NO_ANSWER
        return

    # Force a clean rerun so sidebar history dropdown syncs to the saved chat.
    should_rerun = True

    engine = tts_router.normalize_engine(engine=st.session_state.voice_tts_engine)
    if engine == tts_router.ENGINE_OFFLINE:
        voice = st.session_state.voice_offline_voice or ""
        spinner = constants.VOICE_TTS_SPINNER_OFFLINE
    else:
        voice = st.session_state.voice_edge_voice
        spinner = constants.VOICE_TTS_SPINNER_EDGE

    try:
        with st.spinner(text=spinner):
            audio_file, _words, _tts_elapsed, truncated, mime = tts_router.synthesize_persian(
                text=answer,
                engine=engine,
                voice=voice,
            )
        st.session_state.voice_reply_bytes = Path(audio_file).read_bytes()
        st.session_state.voice_reply_mime = mime
        st.session_state.voice_autoplay = True
        st.session_state.voice_notice = constants.VOICE_TRUNCATED if truncated else ""
    except Exception as exception:
        # Practical fallback: if offline cannot speak Persian, try Edge once.
        handled = False
        if engine == tts_router.ENGINE_OFFLINE:
            try:
                with st.spinner(text=constants.VOICE_TTS_SPINNER_EDGE):
                    audio_file, _words, _tts_elapsed, truncated, mime = (
                        tts_router.synthesize_persian(
                            text=answer,
                            engine=tts_router.ENGINE_EDGE,
                            voice=st.session_state.voice_edge_voice,
                        )
                    )
                st.session_state.voice_reply_bytes = Path(audio_file).read_bytes()
                st.session_state.voice_reply_mime = mime
                st.session_state.voice_autoplay = True
                notice = (
                    "TTS آفلاین برای فارسی روی این سیستم آماده نبود؛ "
                    "پاسخ با Edge خوانده شد. "
                    f"({exception})"
                )
                if truncated:
                    notice = f"{constants.VOICE_TRUNCATED} | {notice}"
                st.session_state.voice_notice = notice
                handled = True
            except Exception as edge_exception:
                st.session_state.voice_notice = (
                    "پاسخ متنی آماده شد و در تاریخچه ذخیره شد، ولی ساخت صدا ناموفق بود: "
                    f"آفلاین: {exception} | Edge: {edge_exception}"
                )
                handled = True

        if not handled:
            st.session_state.voice_notice = (
                "پاسخ متنی آماده شد و در تاریخچه ذخیره شد، ولی ساخت صدا ناموفق بود: "
                f"{exception}"
            )

    if should_rerun:
        st.rerun()


def render_voice_conversation_section() -> None:
    """Persian voice conversation: record, STT, model answer, TTS playback."""

    with st.container():
        st.caption(body=constants.VOICE_HELP)
        st.caption(body=constants.VOICE_RAM_HINT)

        whisper_options = ["auto", "tiny", "base", "small", "medium", "turbo"]
        whisper_labels = {
            "auto": "خودکار — قوی‌ترین مدل ممکن با رم فعلی",
            "tiny": "tiny — خیلی سبک، فارسی ضعیف‌تر",
            "base": "base — سبک",
            "small": "small — متوسط",
            "medium": "medium — پیشنهادی برای فارسی",
            "turbo": "turbo — دقیق‌ترین (رم زیاد)",
        }
        current_whisper = st.session_state.voice_whisper_model
        if current_whisper not in whisper_options:
            current_whisper = "auto"

        engine_options = tts_router.ENGINE_OPTIONS
        engine_labels = {
            tts_router.ENGINE_EDGE: constants.VOICE_TTS_EDGE,
            tts_router.ENGINE_OFFLINE: constants.VOICE_TTS_OFFLINE,
        }
        current_engine = tts_router.normalize_engine(
            engine=st.session_state.voice_tts_engine,
        )

        col_model, col_engine = st.columns(2)
        with col_model:
            st.session_state.voice_whisper_model = st.selectbox(
                label=constants.VOICE_WHISPER_LABEL,
                options=whisper_options,
                index=whisper_options.index(current_whisper),
                format_func=lambda name: whisper_labels.get(name, name),
            )
        with col_engine:
            st.session_state.voice_tts_engine = st.selectbox(
                label=constants.VOICE_TTS_ENGINE_LABEL,
                options=engine_options,
                index=engine_options.index(current_engine),
                format_func=lambda name: engine_labels.get(name, name),
            )

        if st.session_state.voice_tts_engine == tts_router.ENGINE_EDGE:
            voice_options = [
                tts_edge.VOICES_FEMALE[0],
                tts_edge.VOICES_MALE[0],
            ]
            voice_labels = {
                tts_edge.VOICES_FEMALE[0]: constants.VOICE_EDGE_FEMALE,
                tts_edge.VOICES_MALE[0]: constants.VOICE_EDGE_MALE,
            }
            current_voice = st.session_state.voice_edge_voice
            if current_voice not in voice_options:
                current_voice = tts_edge.VOICES_FEMALE[0]
            st.session_state.voice_edge_voice = st.selectbox(
                label=constants.VOICE_EDGE_LABEL,
                options=voice_options,
                index=voice_options.index(current_voice),
                format_func=lambda name: voice_labels.get(name, name),
            )
        else:
            offline_voices: list[dict] = []
            try:
                offline_voices = tts_router.list_offline_voices()
            except Exception as exception:
                st.warning(body=f"{constants.VOICE_OFFLINE_NO_VOICE} ({exception})")

            if offline_voices:
                offline_ids = [""] + [item["id"] for item in offline_voices]
                offline_labels = {"": constants.VOICE_OFFLINE_AUTO}
                for item in offline_voices:
                    offline_labels[item["id"]] = item["name"]
                current_offline = st.session_state.voice_offline_voice
                if current_offline not in offline_ids:
                    current_offline = ""
                st.session_state.voice_offline_voice = st.selectbox(
                    label=constants.VOICE_OFFLINE_VOICE_LABEL,
                    options=offline_ids,
                    index=offline_ids.index(current_offline),
                    format_func=lambda voice_id: offline_labels.get(voice_id, voice_id),
                )
                if not tts_router.has_persian_offline_voice():
                    st.warning(body=constants.VOICE_OFFLINE_HINT)
            else:
                st.caption(body=constants.VOICE_OFFLINE_NO_VOICE)
                st.caption(body=constants.VOICE_OFFLINE_HINT)

        st.slider(
            label=constants.VOICE_SECONDS_LABEL,
            min_value=5,
            max_value=30,
            step=1,
            key="voice_max_seconds",
        )

        mic_name = recorder.get_default_input_device_name()
        if mic_name:
            st.caption(body=f"میکروفون سیستم: {mic_name}")
        else:
            st.caption(body=constants.VOICE_NO_MIC)

        if st.button(
            label=constants.VOICE_RECORD_BUTTON,
            help=constants.VOICE_RECORD_HELP,
        ):
            try:
                with st.spinner(text=constants.VOICE_RECORD_SPINNER):
                    recorded_path = recorder.record_until_silence(
                        max_seconds=float(st.session_state.voice_max_seconds),
                    )
                process_voice_audio(audio_path=recorded_path)
            except Exception as exception:
                st.error(
                    body=(
                        "ضبط صدا ناموفق بود. میکروفون را بررسی کنید یا از ضبط مرورگر استفاده کنید. "
                        f"({exception})"
                    )
                )

        browser_audio = st.audio_input(label=constants.VOICE_BROWSER_LABEL)
        if browser_audio is not None:
            audio_bytes = browser_audio.getvalue()
            audio_token = f"{getattr(browser_audio, 'name', 'browser.wav')}:{len(audio_bytes)}"
            if st.button(label=constants.VOICE_BROWSER_SEND):
                if st.session_state.voice_sent_token == audio_token:
                    st.info(body=constants.VOICE_BROWSER_ALREADY)
                else:
                    try:
                        browser_name = str(getattr(browser_audio, "name", "") or "browser.wav")
                        if Path(browser_name).suffix.lower() not in {
                            ".wav",
                            ".mp3",
                            ".m4a",
                            ".ogg",
                            ".webm",
                        }:
                            browser_name = "browser.wav"
                        saved_path = recorder.save_audio_bytes(
                            file_name=browser_name,
                            file_bytes=audio_bytes,
                        )
                        process_voice_audio(audio_path=saved_path)
                        st.session_state.voice_sent_token = audio_token
                    except Exception as exception:
                        st.error(
                            body=(
                                "ارسال صدای مرورگر ناموفق بود. "
                                f"({exception})"
                            )
                        )

        if st.session_state.voice_notice:
            st.warning(body=st.session_state.voice_notice)

        if st.session_state.voice_last_transcript:
            st.markdown(body=f"**{constants.VOICE_TRANSCRIPT_LABEL}:**")
            st.write(st.session_state.voice_last_transcript)
            if st.session_state.voice_used_whisper:
                st.caption(
                    body=(
                        f"{constants.VOICE_USED_MODEL_LABEL}: "
                        f"{st.session_state.voice_used_whisper}"
                    )
                )

        render_voice_player()


def generate_assistant_reply(
    *,
    title_hint: str = "",
    persist: bool = True,
) -> str:
    """
    Generate an assistant reply for the current messages.

    Assumes the latest user turn is already appended to session messages.
    Returns the assistant text (empty string when the model returns nothing).
    """

    if not ensure_ollama_ready():
        raise RuntimeError(st.session_state.ollama_status_message)

    _free_whisper_if_chat_needs_ram()

    if not st.session_state.model_ready:
        ok = prepare_selected_model(model_name=st.session_state.model_name)
        if not ok:
            raise RuntimeError(st.session_state.model_status_message)

    try:
        assistant_answer, _elapsed_time, _prompt_tokens, _completion_tokens = chat(
            messages=st.session_state.messages,
            model_name=st.session_state.model_name,
        )
    except Exception:
        st.session_state.ollama_ready = False
        st.session_state.model_ready = False
        raise

    if not assistant_answer:
        return ""

    st.session_state.messages.append(
        {
            llm_utility.KEY_NAME_ROLE: llm_utility.ROLE_ASSISTANT,
            llm_utility.KEY_NAME_CONTENT: assistant_answer,
        }
    )

    if persist:
        persist_current_conversation(title_hint=title_hint)

    return assistant_answer


def get_assistant_answer(
    user_prompt: str,
    *,
    title_hint: str = "",
    persist: bool = True,
) -> tuple[str, str]:
    """
    Get assistant answer from Ollama and optionally persist history.

    Returns:
        answer text, elapsed time text
    """

    if not ensure_ollama_ready():
        raise RuntimeError(st.session_state.ollama_status_message)

    user_message: dict = {
        llm_utility.KEY_NAME_ROLE: llm_utility.ROLE_USER,
        llm_utility.KEY_NAME_CONTENT: user_prompt,
    }
    st.session_state.messages.append(user_message)

    try:
        assistant_answer = generate_assistant_reply(
            title_hint=title_hint,
            persist=persist,
        )
    except Exception:
        if (
            st.session_state.messages
            and st.session_state.messages[-1].get(llm_utility.KEY_NAME_ROLE)
            == llm_utility.ROLE_USER
        ):
            st.session_state.messages.pop()
        raise

    if not assistant_answer:
        if (
            st.session_state.messages
            and st.session_state.messages[-1].get(llm_utility.KEY_NAME_ROLE)
            == llm_utility.ROLE_USER
        ):
            st.session_state.messages.pop()
        return constants.ERROR_NO_ANSWER, ""

    return assistant_answer, ""
