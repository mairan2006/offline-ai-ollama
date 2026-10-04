"""
Offline AI Streamlit App - Phase A

For Running:
> streamlit run ./streamlit_app.py
"""

import streamlit as st

import chatbot_constants as constants
import chatbot_functions as functions


def main() -> None:
    """Main Streamlit application."""

    functions.set_page_config()
    functions.initial_session_state()

    ollama_ok = functions.ensure_ollama_ready()
    functions.render_sidebar()

    st.header(body=f"👋 {constants.PAGE_HEADER}", divider="rainbow")

    if not ollama_ok:
        st.error(body=st.session_state.ollama_status_message)
        st.info(body=constants.ERROR_OLLAMA_CONNECTION)
        return

    functions.render_chat_messages()

    user_prompt = st.chat_input(placeholder=constants.USER_PROMPT_PLACEHOLDER)
    if not user_prompt:
        return

    user_prompt = user_prompt.strip()
    if not user_prompt:
        return

    with st.chat_message(name="user"):
        st.markdown(body=user_prompt)

    with st.chat_message(name="assistant"):
        with st.spinner(text="در حال فکر کردن..."):
            try:
                assistant_answer, elapsed_text = functions.get_assistant_answer(
                    user_prompt=user_prompt,
                )
                st.markdown(body=assistant_answer)
                if elapsed_text:
                    st.caption(body=elapsed_text)
            except Exception as exception:
                message = str(exception).strip() or constants.ERROR_OLLAMA_CONNECTION
                st.error(body=message)


if __name__ == "__main__":
    main()
