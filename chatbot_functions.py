"""
Chatbot Functions
"""

import streamlit as st

import chatbot_constants as constants
import dt_llm_utility as llm_utility
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


def clear_chat_history() -> None:
    """Clear chat history and keep system message."""

    st.session_state.messages = [constants.SYSTEM_MESSAGE.copy()]


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


def render_sidebar() -> None:
    """Render sidebar settings including model dropdown."""

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
                    # Keep conversation continuity; user can clear manually.
                    st.info(
                        body=(
                            f"مدل از «{previous_model}» به «{selected_name}» تغییر کرد."
                        )
                    )
                else:
                    st.error(body=st.session_state.model_status_message)
                    # Revert selection if preparation failed.
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

        st.markdown(body=constants.ABOUT, unsafe_allow_html=True)

        if st.button(label=constants.CLEAR_CHAT):
            clear_chat_history()
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


def get_assistant_answer(user_prompt: str) -> tuple[str, str]:
    """
    Get assistant answer from Ollama.

    Returns:
        answer text, elapsed time text
    """

    if not ensure_ollama_ready():
        raise RuntimeError(st.session_state.ollama_status_message)

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

    elapsed_text: str = (
        f"{constants.ELAPSED_TIME_LABEL}: {format_seconds(seconds=elapsed_time)} | "
        f"{constants.PROMPT_TOKENS_LABEL}: {prompt_tokens} | "
        f"{constants.COMPLETION_TOKENS_LABEL}: {completion_tokens}"
    )
    return assistant_answer, elapsed_text
