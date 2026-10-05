"""
Chatbot Functions
"""

from pathlib import Path
from typing import Optional

import streamlit as st

import chatbot_constants as constants
import dt_analysis as analysis
import dt_files as files
import dt_history as history
import dt_llm_utility as llm_utility
import dt_recorder as recorder
import dt_tts_edge as tts_edge
import dtx_whisper as whisper_module
import model_constants as model_constants
from dt_ollama_manager import (
    can_fit_model_in_ram,
    ensure_ollama_running,
    format_bytes,
    get_available_ram_bytes,
    get_model_details,
    get_model_display_options,
    prepare_model_for_use,
)
from dt_utility import format_seconds
from dtx_ollama import chat


def set_page_config() -> None:
    """Set Streamlit page config and RTL style."""

    st.set_page_config(
        page_title=constants.PAGE_TITLE,
        page_icon="👋",
        layout="centered",
    )
    st.markdown(body=constants.STREAMLIT_STYLE, unsafe_allow_html=True)


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

    if "file_analysis_result" not in st.session_state:
        st.session_state.file_analysis_result = ""

    if "file_analysis_source" not in st.session_state:
        st.session_state.file_analysis_source = ""

    if "voice_whisper_model" not in st.session_state:
        st.session_state.voice_whisper_model = "auto"

    if "voice_edge_voice" not in st.session_state:
        st.session_state.voice_edge_voice = tts_edge.VOICES_FEMALE[0]

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


def start_new_conversation() -> None:
    """Start a fresh in-memory conversation (saved on first reply)."""

    st.session_state.messages = [constants.SYSTEM_MESSAGE.copy()]
    st.session_state.conversation_id = None
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


def persist_current_conversation() -> None:
    """Save current messages into SQLite."""

    conversation_id = ensure_conversation_exists()
    history.save_messages(
        conversation_id=conversation_id,
        messages=st.session_state.messages,
        model_name=st.session_state.model_name,
    )


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
    st.session_state.history_notice = constants.HISTORY_LOADED


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


def render_history_section() -> None:
    """Render conversation history controls in sidebar."""

    st.markdown(body=f"**{constants.HISTORY_HEADER}**")

    conversations = history.list_conversations(limit=50)
    if not conversations:
        st.caption(body=constants.HISTORY_EMPTY)
    else:
        labels = [constants.HISTORY_NONE_OPTION]
        ids: list[Optional[int]] = [None]
        for item in conversations:
            label = (
                f"#{item['id']} | {item['title']} | {item['model_name']} | "
                f"{item['updated_at']}"
            )
            labels.append(label)
            ids.append(int(item["id"]))

        # Keep dropdown synced with currently loaded conversation.
        current_index = 0
        if st.session_state.conversation_id is not None:
            for index, conversation_id in enumerate(ids):
                if conversation_id == st.session_state.conversation_id:
                    current_index = index
                    break

        selected_label = st.selectbox(
            label=constants.HISTORY_SELECT_LABEL,
            options=labels,
            index=current_index,
        )
        selected_id = ids[labels.index(selected_label)]

        # Load immediately on dropdown change (no separate load button).
        if (
            selected_id is not None
            and selected_id != st.session_state.conversation_id
        ):
            load_conversation(conversation_id=selected_id)
            st.rerun()

        if st.button(label=constants.HISTORY_DELETE, use_container_width=True):
            if selected_id is None and st.session_state.conversation_id is None:
                st.session_state.history_notice = "لطفا یک گفتگو انتخاب کنید."
            else:
                target_id = selected_id or st.session_state.conversation_id
                history.delete_conversation(conversation_id=int(target_id))
                if st.session_state.conversation_id == target_id:
                    start_new_conversation()
                st.session_state.history_notice = constants.HISTORY_DELETED
                st.rerun()

    if st.button(label=constants.HISTORY_DELETE_ALL, use_container_width=True):
        history.delete_all_conversations()
        start_new_conversation()
        st.session_state.history_notice = "همه تاریخچه حذف شد."
        st.rerun()

    if st.session_state.history_notice:
        st.caption(body=st.session_state.history_notice)

    current_id = st.session_state.conversation_id
    if current_id is None:
        st.caption(body="گفتگوی فعلی: هنوز ذخیره نشده (بعد از اولین پاسخ ذخیره می‌شود)")
    else:
        st.caption(body=f"گفتگوی فعلی: #{current_id}")


def render_sidebar() -> None:
    """Render sidebar settings including model dropdown and history."""

    with st.sidebar:
        st.header(body=constants.SETTINGS)

        st.write(constants.OLLAMA_STATUS_LABEL)
        if st.session_state.ollama_ready:
            st.success(body=st.session_state.ollama_status_message)
        elif st.session_state.ollama_status_message:
            st.error(body=st.session_state.ollama_status_message)
        else:
            st.warning(body=constants.CHECKING_OLLAMA)

        available_ram = get_available_ram_bytes()
        st.write(constants.RAM_STATUS_LABEL)
        st.caption(body=f"رم آزاد فعلی: {format_bytes(available_ram)}")
        st.caption(
            body=(
                f"حاشیه امن سیستم: "
                f"{format_bytes(model_constants.RAM_SAFETY_MARGIN_BYTES)}"
            )
        )

        if st.session_state.ollama_ready:
            if not st.session_state.model_options_cache:
                refresh_model_options()

            options = st.session_state.model_options_cache
            labels = [item[1] for item in options]
            names = [item[0] for item in options]

            current_name = st.session_state.model_name
            if current_name in names:
                current_index = names.index(current_name)
            else:
                current_index = 0

            selected_label = st.selectbox(
                label=constants.SELECT_YOUR_MODEL,
                options=labels,
                index=current_index,
                help="در لیست فقط نام و حجم دانلود آمده؛ توضیح کامل پایین نمایش داده می‌شود.",
            )
            selected_name = names[labels.index(selected_label)]
            selected_downloaded = options[labels.index(selected_label)][2]
            details = get_model_details(model_name=selected_name)

            st.markdown(body=f"**{constants.MODEL_DETAILS_LABEL}**")
            st.markdown(body=f"**{details['title']}** (`{details['name']}`)")
            st.write(f"{constants.MODEL_CATEGORY_LABEL}: {details['category']}")
            st.write(
                f"{constants.DOWNLOAD_SIZE_LABEL}: **{details['download_label']}**"
            )
            st.write(f"{constants.RAM_NEED_LABEL}: **{details['ram_label']}**")
            if selected_downloaded:
                st.success(body=constants.DOWNLOADED_YES)
            else:
                st.warning(body=constants.DOWNLOADED_NO)

            st.markdown(body=f"**{constants.MODEL_DESCRIPTION_LABEL}:**")
            st.info(body=details["description"])

            fits, ram_msg, _ = can_fit_model_in_ram(model_name=selected_name)
            if fits:
                st.caption(body=ram_msg)
            else:
                st.warning(body=ram_msg)

            if selected_name != st.session_state.model_name:
                previous_model = st.session_state.model_name
                st.session_state.model_name = selected_name
                st.session_state.model_ready = False

                ok = prepare_selected_model(model_name=selected_name)
                if ok:
                    st.success(body=st.session_state.model_status_message)
                    st.info(
                        body=(
                            f"مدل از «{previous_model}» به «{selected_name}» تغییر کرد."
                        )
                    )
                    if st.session_state.conversation_id is not None:
                        persist_current_conversation()
                else:
                    st.error(body=st.session_state.model_status_message)
                    st.session_state.model_name = previous_model
                    st.session_state.model_ready = False
                    st.rerun()

            st.write(f"{constants.SELECTED_MODEL}")
            st.info(body=st.session_state.model_name)

            st.write(constants.MODEL_STATUS_LABEL)
            if st.session_state.model_ready and st.session_state.model_status_message:
                st.success(body=st.session_state.model_status_message)
            elif st.session_state.model_status_message:
                st.warning(body=st.session_state.model_status_message)

            if st.button(label=constants.REFRESH_MODELS):
                refresh_model_options()
                st.session_state.model_ready = False
                st.rerun()

        st.divider()
        render_history_section()

        st.markdown(body=constants.ABOUT, unsafe_allow_html=True)

        if st.button(label=constants.CLEAR_CHAT):
            start_new_conversation()
            st.rerun()


def add_analysis_result_to_chat(result_text: str, source_name: str) -> None:
    """Append analysis result into current chat and persist."""

    user_note = f"نتیجه تحلیل فایل «{source_name}» را به گفتگو اضافه کردم."
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
    persist_current_conversation()


def render_file_analysis_section() -> None:
    """Render upload + analysis actions for image/pdf/text/audio."""

    with st.expander(label=constants.FILES_HEADER, expanded=False):
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
                        text, elapsed, unloaded = analysis.transcribe_audio(
                            audio_path=saved_path,
                            model_name=st.session_state.voice_whisper_model,
                        )
                        if unloaded:
                            st.session_state.model_ready = False
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

    import base64

    autoplay = bool(st.session_state.voice_autoplay)
    st.session_state.voice_autoplay = False
    encoded = base64.b64encode(audio_bytes).decode(encoding="ascii")
    autoplay_attr = "autoplay" if autoplay else ""
    st.markdown(
        body=(
            '<div dir="rtl">'
            f'<audio controls {autoplay_attr} style="width: 100%">'
            f'<source src="data:audio/mpeg;base64,{encoded}" type="audio/mpeg">'
            "</audio></div>"
        ),
        unsafe_allow_html=True,
    )


def process_voice_audio(audio_path: Path) -> None:
    """STT, chat answer, then Edge TTS playback."""

    st.session_state.voice_notice = ""

    with st.spinner(text=constants.VOICE_STT_SPINNER):
        text, _elapsed, unloaded = analysis.transcribe_audio(
            audio_path=audio_path,
            model_name=st.session_state.voice_whisper_model,
        )
    if unloaded:
        st.session_state.model_ready = False

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

    try:
        with st.spinner(text="در حال فکر کردن..."):
            answer, _elapsed_text = get_assistant_answer(user_prompt=text)
    except Exception as exception:
        st.session_state.voice_notice = str(exception)
        return

    if answer == constants.ERROR_NO_ANSWER:
        st.session_state.voice_notice = constants.ERROR_NO_ANSWER
        return

    try:
        with st.spinner(text=constants.VOICE_TTS_SPINNER):
            audio_file, _words, _tts_elapsed, truncated = tts_edge.synthesize_persian(
                text=answer,
                voice=st.session_state.voice_edge_voice,
            )
    except Exception as exception:
        st.session_state.voice_notice = (
            f"پاسخ متنی آماده شد، ولی ساخت صدا ناموفق بود: {exception}"
        )
        return

    st.session_state.voice_reply_bytes = Path(audio_file).read_bytes()
    st.session_state.voice_autoplay = True
    st.session_state.voice_notice = constants.VOICE_TRUNCATED if truncated else ""


def render_voice_conversation_section() -> None:
    """Persian voice conversation: record, STT, model answer, Edge playback."""

    with st.expander(label=constants.VOICE_HEADER, expanded=True):
        st.caption(body=constants.VOICE_HELP)
        st.caption(body=constants.VOICE_RAM_HINT)

        whisper_options = ["auto", "tiny", "base", "small", "medium", "turbo"]
        whisper_labels = {
            "auto": "خودکار — بهترین مدل با رم فعلی",
            "tiny": "tiny — خیلی سبک، فارسی ضعیف‌تر",
            "base": "base — سبک",
            "small": "small — پیشنهادی برای رم کم",
            "medium": "medium — دقیق‌تر (رم بیشتر)",
            "turbo": "turbo — دقیق‌ترین (رم زیاد)",
        }
        current_whisper = st.session_state.voice_whisper_model
        if current_whisper not in whisper_options:
            current_whisper = "auto"

        voice_options = [
            tts_edge.VOICES_FEMALE[0],
            tts_edge.VOICES_MALE[0],
        ]
        voice_labels = {
            tts_edge.VOICES_FEMALE[0]: constants.VOICE_EDGE_FEMALE,
            tts_edge.VOICES_MALE[0]: constants.VOICE_EDGE_MALE,
        }

        col_model, col_voice = st.columns(2)
        with col_model:
            st.session_state.voice_whisper_model = st.selectbox(
                label=constants.VOICE_WHISPER_LABEL,
                options=whisper_options,
                index=whisper_options.index(current_whisper),
                format_func=lambda name: whisper_labels.get(name, name),
            )
        with col_voice:
            current_voice = st.session_state.voice_edge_voice
            if current_voice not in voice_options:
                current_voice = tts_edge.VOICES_FEMALE[0]
            st.session_state.voice_edge_voice = st.selectbox(
                label=constants.VOICE_EDGE_LABEL,
                options=voice_options,
                index=voice_options.index(current_voice),
                format_func=lambda name: voice_labels.get(name, name),
            )

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
                st.error(body=str(exception))

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
                        st.error(body=str(exception))

        if st.session_state.voice_notice:
            st.warning(body=st.session_state.voice_notice)

        if st.session_state.voice_last_transcript:
            st.markdown(body=f"**{constants.VOICE_TRANSCRIPT_LABEL}:**")
            st.write(st.session_state.voice_last_transcript)

        render_voice_player()


def get_assistant_answer(user_prompt: str) -> tuple[str, str]:
    """
    Get assistant answer from Ollama and persist history.

    Returns:
        answer text, elapsed time text
    """

    if not ensure_ollama_ready():
        raise RuntimeError(st.session_state.ollama_status_message)

    _free_whisper_if_chat_needs_ram()

    if not st.session_state.model_ready:
        ok = prepare_selected_model(model_name=st.session_state.model_name)
        if not ok:
            raise RuntimeError(st.session_state.model_status_message)

    user_message: dict = {
        llm_utility.KEY_NAME_ROLE: llm_utility.ROLE_USER,
        llm_utility.KEY_NAME_CONTENT: user_prompt,
    }
    st.session_state.messages.append(user_message)

    try:
        assistant_answer, elapsed_time, prompt_tokens, completion_tokens = chat(
            messages=st.session_state.messages,
            model_name=st.session_state.model_name,
        )
    except Exception:
        st.session_state.messages.pop()
        st.session_state.ollama_ready = False
        st.session_state.model_ready = False
        raise

    if not assistant_answer:
        st.session_state.messages.pop()
        return constants.ERROR_NO_ANSWER, ""

    assistant_message: dict = {
        llm_utility.KEY_NAME_ROLE: llm_utility.ROLE_ASSISTANT,
        llm_utility.KEY_NAME_CONTENT: assistant_answer,
    }
    st.session_state.messages.append(assistant_message)

    persist_current_conversation()

    elapsed_text: str = (
        f"{constants.ELAPSED_TIME_LABEL}: {format_seconds(seconds=elapsed_time)} | "
        f"{constants.PROMPT_TOKENS_LABEL}: {prompt_tokens} | "
        f"{constants.COMPLETION_TOKENS_LABEL}: {completion_tokens}"
    )
    return assistant_answer, elapsed_text
