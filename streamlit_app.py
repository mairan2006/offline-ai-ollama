"""
Offline AI Streamlit App - Phase H / I (Cursor-like UI + file attach)

For Running:
> streamlit run ./streamlit_app.py
"""

from __future__ import annotations

import streamlit as st

import chatbot_constants as constants
import chatbot_functions as functions


def main() -> None:
    """Main Streamlit application."""

    functions.set_page_config()
    functions.initial_session_state()

    ollama_ok = functions.ensure_ollama_ready()
    if ollama_ok and not st.session_state.model_options_cache:
        functions.refresh_model_options()

    if ollama_ok and not st.session_state.model_ready:
        functions.prepare_selected_model(model_name=st.session_state.model_name)

    functions.render_sidebar()

    if not ollama_ok:
        st.error(body=st.session_state.ollama_status_message)
        st.info(body=constants.ERROR_OLLAMA_CONNECTION)
        return

    if not st.session_state.model_ready:
        st.error(
            body=st.session_state.model_status_message
            or "مدل برای استفاده آماده نیست."
        )

    has_turns = any(
        message.get("role") != "system"
        for message in st.session_state.messages
    )

    if has_turns:
        functions.render_chat_messages()
        functions.render_voice_player()
    else:
        st.markdown(body=constants.EMPTY_CHAT_HTML, unsafe_allow_html=True)

    functions.render_composer()

    # submit_mode="stop": send arrow becomes Stop while the script runs.
    chat_value = st.chat_input(
        placeholder=constants.USER_PROMPT_PLACEHOLDER,
        accept_file="multiple",
        file_type=list(constants.CHAT_FILE_TYPES),
        max_upload_size=50,
        key="main_chat_input",
        submit_mode="stop",
    )

    if chat_value is None:
        return

    if not st.session_state.model_ready:
        ok = functions.prepare_selected_model(model_name=st.session_state.model_name)
        if not ok:
            st.error(
                body=st.session_state.model_status_message
                or "مدل برای استفاده آماده نیست."
            )
            return

    try:
        functions.handle_chat_input_value(chat_value=chat_value)
    except Exception as exception:
        st.error(body=str(exception).strip() or constants.ERROR_OLLAMA_CONNECTION)


if __name__ == "__main__":
    main()
