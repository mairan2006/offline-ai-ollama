"""
Chatbot Functions
"""

import streamlit as st

import chatbot_constants as constants
import dt_llm_utility as llm_utility
from dt_ollama_manager import ensure_ollama_running
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


def ensure_ollama_ready() -> bool:
    """Check Ollama and start it if needed. Cache result in session."""

    if st.session_state.ollama_ready:
        return True

    with st.spinner(text=constants.CHECKING_OLLAMA):
        ok, message = ensure_ollama_running()

    st.session_state.ollama_ready = ok
    st.session_state.ollama_status_message = message
    return ok


def clear_chat_history() -> None:
    """Clear chat history and keep system message."""

    st.session_state.messages = [constants.SYSTEM_MESSAGE.copy()]


def render_sidebar() -> None:
    """Render sidebar settings."""

    with st.sidebar:
        st.header(body=constants.SETTINGS)
        st.write(f"{constants.SELECTED_MODEL}")
        st.info(body=st.session_state.model_name)
        st.caption(body=constants.SELECT_YOUR_MODEL)

        st.write(constants.OLLAMA_STATUS_LABEL)
        if st.session_state.ollama_ready:
            st.success(body=st.session_state.ollama_status_message)
        elif st.session_state.ollama_status_message:
            st.error(body=st.session_state.ollama_status_message)
        else:
            st.warning(body=constants.CHECKING_OLLAMA)

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
