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
FILES_HEADER: Final[str] = "تحلیل فایل (عکس / PDF / متن / صوت)"
FILES_UPLOAD_LABEL: Final[str] = "فایل خود را انتخاب کنید"
FILES_ANALYZE_IMAGE: Final[str] = "تحلیل تصویر"
FILES_SUMMARIZE: Final[str] = "خلاصه / تحلیل متن"
FILES_TRANSLATE_FA: Final[str] = "ترجمه به فارسی"
FILES_TRANSLATE_EN: Final[str] = "ترجمه به انگلیسی"
FILES_TRANSCRIBE: Final[str] = "تبدیل صوت به متن"
FILES_ADD_TO_CHAT: Final[str] = "افزودن نتیجه به گفتگو"
FILES_RESULT_LABEL: Final[str] = "نتیجه تحلیل"
FILES_UNSUPPORTED: Final[str] = "این نوع فایل پشتیبانی نمی‌شود."
FILES_NO_FILE: Final[str] = "ابتدا یک فایل آپلود کنید."
VOICE_HEADER: Final[str] = "مکالمه صوتی"
VOICE_HELP: Final[str] = (
    "صحبت کنید. گفتار با Whisper کم‌رم (faster-whisper) به متن تبدیل می‌شود، "
    "مدل جواب می‌دهد، و Edge همان پاسخ را با صدای فارسی می‌خواند. "
    "چت آفلاین است؛ ساخت صدا با Edge به اینترنت نیاز دارد."
)
VOICE_WHISPER_LABEL: Final[str] = "مدل Whisper"
VOICE_EDGE_LABEL: Final[str] = "صدای پاسخ"
VOICE_SECONDS_LABEL: Final[str] = "حداکثر مدت ضبط (ثانیه)"
VOICE_RECORD_BUTTON: Final[str] = "ضبط با میکروفون سیستم (تا سکوت)"
VOICE_RECORD_HELP: Final[str] = (
    "الگوی Sound Recorder: بعد از شروع حرف زدن، با کمی سکوت ضبط تمام می‌شود."
)
VOICE_BROWSER_LABEL: Final[str] = "یا با میکروفون مرورگر ضبط کنید"
VOICE_BROWSER_SEND: Final[str] = "ارسال صدای مرورگر"
VOICE_BROWSER_ALREADY: Final[str] = "این صدا قبلاً ارسال شده. برای نوبت بعد دوباره ضبط کنید."
VOICE_TRANSCRIPT_LABEL: Final[str] = "متن شنیده‌شده"
VOICE_EMPTY_TRANSCRIPT: Final[str] = (
    "متنی از صدا استخراج نشد. واضح‌تر و کمی بلندتر فارسی صحبت کنید، "
    "یا مدل Whisper را روی small/medium بگذارید."
)
VOICE_RAM_HINT: Final[str] = (
    "برای دقت بهتر با رم کم: گزینه «خودکار» یا «small/medium» را بگذارید. "
    "قبل از شنیدن، مدل چت موقتاً از رم خارج می‌شود و بعد دوباره لود می‌شود. "
    "نزدیک میکروفون، واضح و بدون نویز صحبت کنید."
)
VOICE_RECORD_SPINNER: Final[str] = "در حال ضبط... بعد از سکوت، ضبط خودش تمام می‌شود."
VOICE_STT_SPINNER: Final[str] = "در حال تبدیل گفتار به متن با Whisper..."
VOICE_TTS_SPINNER: Final[str] = "در حال ساخت صدای پاسخ با Edge..."
VOICE_TRUNCATED: Final[str] = "پاسخ طولانی بود؛ برای پخش، بخش اول آن خوانده شد."
VOICE_NO_MIC: Final[str] = "میکروفون پیش‌فرض سیستم پیدا نشد. از ضبط مرورگر استفاده کنید."
VOICE_EDGE_FEMALE: Final[str] = "زن — Dilara"
VOICE_EDGE_MALE: Final[str] = "مرد — Farid"

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
