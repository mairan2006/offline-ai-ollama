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
SELECT_YOUR_MODEL: Final[str] = "مدل را انتخاب کنید:"
MODEL_DETAILS_LABEL: Final[str] = "جزئیات مدل انتخاب‌شده"
DOWNLOAD_SIZE_LABEL: Final[str] = "حجم دانلود تقریبی"
RAM_NEED_LABEL: Final[str] = "رم تقریبی موردنیاز"
MODEL_CATEGORY_LABEL: Final[str] = "دسته"
MODEL_DESCRIPTION_LABEL: Final[str] = "توضیحات"
DOWNLOADED_YES: Final[str] = "وضعیت: دانلود شده و روی سیستم موجود است"
DOWNLOADED_NO: Final[str] = "وضعیت: هنوز دانلود نشده (با انتخاب، دانلود شروع می‌شود)"
USER_PROMPT_PLACEHOLDER: Final[str] = "لطفا سوال خودتان را اینجا بنویسید..."
CLEAR_CHAT: Final[str] = "گفتگوی جدید"
REFRESH_MODELS: Final[str] = "بروزرسانی لیست مدل‌ها"
HISTORY_HEADER: Final[str] = "تاریخچه گفتگوها"
HISTORY_SELECT_LABEL: Final[str] = "گفتگوی قبلی را انتخاب کنید (با انتخاب، فوری بارگذاری می‌شود):"
HISTORY_DELETE: Final[str] = "حذف گفتگوی انتخاب‌شده"
HISTORY_DELETE_ALL: Final[str] = "حذف همه تاریخچه"
HISTORY_EMPTY: Final[str] = "هنوز گفتگوی ذخیره‌شده‌ای وجود ندارد."
HISTORY_LOADED: Final[str] = "گفتگو بارگذاری شد."
HISTORY_DELETED: Final[str] = "گفتگو حذف شد."
HISTORY_NEW: Final[str] = "گفتگوی جدید شروع شد."
HISTORY_NONE_OPTION: Final[str] = "— انتخاب کنید —"
ELAPSED_TIME_LABEL: Final[str] = "زمان پاسخ"
PROMPT_TOKENS_LABEL: Final[str] = "توکن ورودی"
COMPLETION_TOKENS_LABEL: Final[str] = "توکن خروجی"
ERROR_OLLAMA_CONNECTION: Final[str] = (
    "اتصال به Ollama برقرار نشد. برنامه تلاش کرد آن را روشن کند ولی موفق نشد!"
)
ERROR_NO_ANSWER: Final[str] = "پاسخی از مدل دریافت نشد!"
OLLAMA_STATUS_LABEL: Final[str] = "وضعیت Ollama:"
CHECKING_OLLAMA: Final[str] = "در حال بررسی و آماده‌سازی Ollama..."
RAM_STATUS_LABEL: Final[str] = "وضعیت رم:"
MODEL_STATUS_LABEL: Final[str] = "وضعیت مدل:"
PREPARING_MODEL: Final[str] = "در حال آماده‌سازی مدل (دانلود/رم)..."
DOWNLOADING_MODEL: Final[str] = "در حال دانلود مدل..."
