"""Streamlit UI for offline chat / RAG with Ollama."""

from __future__ import annotations

import streamlit as st

import config
from app.ollama_client import build_messages, chat_stream, health
from app.rag import build_index, format_context, retrieve


st.set_page_config(page_title="هوش مصنوعی آفلاین", page_icon="🧠", layout="centered")
st.markdown(
    """
    <style>
      .stApp, [data-testid="stSidebar"], [data-testid="stChatInput"] {
        direction: rtl;
        text-align: right;
      }
      pre, code, .stCode, [data-testid="stChatInput"] textarea {
        direction: ltr;
        text-align: left;
      }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("هوش مصنوعی آفلاین")
st.caption("مدل‌های محلی با Ollama · بدون نیاز به اینترنت ابری")


@st.cache_data(ttl=30)
def get_health():
    return health()


with st.sidebar:
    st.header("تنظیمات")
    try:
        info = get_health()
        models = info["models"] or [config.OLLAMA_MODEL]
        default_idx = (
            models.index(config.OLLAMA_MODEL) if config.OLLAMA_MODEL in models else 0
        )
        model = st.selectbox("مدل", models, index=default_idx)
        st.success(f"اتصال برقرار: {info['host']}")
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()

    use_rag = st.toggle("استفاده از اسناد محلی (RAG)", value=False)
    top_k = st.slider("تعداد تکه‌های مرتبط", 1, 8, config.TOP_K)
    if st.button("بازسازی ایندکس اسناد"):
        with st.spinner("در حال ایندکس..."):
            try:
                count = build_index()
                st.success(f"{count} تکه ایندکس شد")
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))
    if st.button("پاک کردن گفتگو"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("سؤالت را بنویس...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
        if m["role"] in {"user", "assistant"}
    ]
    context = None
    if use_rag:
        try:
            hits = retrieve(prompt, top_k=top_k)
            context = format_context(hits)
            with st.expander("متن بازیابی‌شده از اسناد"):
                st.text(context)
        except Exception as exc:  # noqa: BLE001
            st.warning(str(exc))

    messages = build_messages(history, prompt, context=context)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        parts: list[str] = []
        for token in chat_stream(messages, model=model):
            parts.append(token)
            placeholder.markdown("".join(parts))
        answer = "".join(parts)
    st.session_state.messages.append({"role": "assistant", "content": answer})
