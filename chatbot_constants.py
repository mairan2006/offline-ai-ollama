"""
Chatbot Constants
"""

from typing import Final

import dt_llm_utility as llm_utility
from dtx_dotenv import get_key_value

AI: Final[str] = "دستیار"
USER: Final[str] = "شما"

SYSTEM_MESSAGE: Final[dict] = llm_utility.SYSTEM_MESSAGE

DEFAULT_MODEL_NAME: Final[str] = get_key_value(
    key="OLLAMA_MODEL",
    default="gemma3:4b",
).replace(" ", "").lower()

STREAMLIT_STYLE: Final[str] = """
<style>
    @import url('https://fonts.cdnfonts.com/css/iransansx');

    html, body, p, h1, h2, h3, h4, h5, h6, input, textarea {
        font-family: 'IRANSansX', tahoma !important;
    }

    [role=radiogroup], pre, code {
        direction: ltr;
        text-align: left;
    }

    .block-container, section, input, textarea,
    [data-testid="stSidebar"], [data-testid="stChatInput"] {
        direction: rtl;
        text-align: right;
    }

    [data-testid="stChatInput"] textarea {
        direction: rtl;
        text-align: right;
    }
</style>
"""

ABOUT: Final[str] = """
<p style="direction: rtl; text-align: justify;">
    هوش مصنوعی آفلاین با Ollama
</p>
"""

SETTINGS: Final[str] = "تنظیمات"
PAGE_TITLE: Final[str] = "هوش مصنوعی آفلاین"
PAGE_HEADER: Final[str] = "به هوش مصنوعی آفلاین خوش آمدید"
SELECTED_MODEL: Final[str] = "مدل فعلی:"
SELECT_YOUR_MODEL: Final[str] = "مدل انتخاب‌شده (فاز A - ثابت):"
USER_PROMPT_PLACEHOLDER: Final[str] = "لطفا سوال خودتان را اینجا بنویسید..."
CLEAR_CHAT: Final[str] = "پاک کردن گفتگو"
ELAPSED_TIME_LABEL: Final[str] = "زمان پاسخ"
PROMPT_TOKENS_LABEL: Final[str] = "توکن ورودی"
COMPLETION_TOKENS_LABEL: Final[str] = "توکن خروجی"
ERROR_OLLAMA_CONNECTION: Final[str] = (
    "اتصال به Ollama برقرار نشد. برنامه تلاش کرد آن را روشن کند ولی موفق نشد!"
)
ERROR_NO_ANSWER: Final[str] = "پاسخی از مدل دریافت نشد!"
OLLAMA_STATUS_LABEL: Final[str] = "وضعیت Ollama:"
CHECKING_OLLAMA: Final[str] = "در حال بررسی و آماده‌سازی Ollama..."
