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
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');

    :root {
        --oa-bg: #000000;
        --oa-surface: #0a0a0a;
        --oa-elevated: #141414;
        --oa-composer: #121212;
        --oa-border: #2a2a2a;
        --oa-text: #ededed;
        --oa-muted: #8a8a8a;
        --oa-font: 'Vazirmatn', Tahoma, sans-serif;
        --oa-icons: "Material Symbols Rounded", "Material Symbols Outlined",
            "Material Icons", sans-serif;
        --oa-composer-max: 960px;
    }

    html, body, .stApp, input, textarea, select, li, p, div,
    [data-testid="stMarkdownContainer"],
    [data-testid="stChatMessage"],
    [data-testid="stCaptionContainer"] {
        font-family: var(--oa-font) !important;
    }
    /* Do NOT force Vazirmatn on buttons — breaks Material icon ligatures (tofu/square). */
    button {
        font-family: inherit;
    }

    /* Material ligature icons — must NOT use Vazirmatn */
    [data-testid="stIconMaterial"],
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"],
    [data-testid="stExpanderIcon"],
    [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
    [data-testid="stChatInput"] [data-testid="stIconMaterial"],
    [data-testid="stChatInput"] span.material-symbols-rounded,
    [data-testid="stChatInput"] span.material-symbols-outlined,
    [data-testid="stChatInput"] button span {
        font-family: var(--oa-icons) !important;
        font-style: normal !important;
        font-weight: 400 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        -webkit-font-smoothing: antialiased;
        font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24;
    }

    .stApp { background: var(--oa-bg) !important; color: var(--oa-text) !important; }
    [data-testid="stHeader"] { background: transparent !important; }

    /* Hide only Deploy + ⋮ — keep sidebar expand control */
    [data-testid="stAppDeployButton"],
    .stAppDeployButton,
    #MainMenu,
    [data-testid="stMainMenu"],
    [data-testid="stToolbar"] [data-testid="stAppDeployButton"],
    [data-testid="stToolbar"] #MainMenu,
    [data-testid="stToolbar"] [data-testid="stMainMenu"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }
    /* Reopen-sidebar chevron when collapsed (do not hide with toolbar rules) */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stExpandSidebarButton"],
    [data-testid="stHeader"] [data-testid="stBaseButton-header"],
    [data-testid="stHeader"] button[kind="header"],
    [data-testid="stHeader"] button[kind="headerNoPadding"] {
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        z-index: 1000100 !important;
    }
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stExpandSidebarButton"] {
        position: fixed !important;
        top: 0.65rem !important;
        left: 0.65rem !important;
        right: auto !important;
        inset-inline-start: 0.65rem !important;
        inset-inline-end: auto !important;
        background: #141414 !important;
        border: 1px solid #2c2c2c !important;
        border-radius: 999px !important;
        width: 2.35rem !important;
        height: 2.35rem !important;
        min-width: 2.35rem !important;
        align-items: center !important;
        justify-content: center !important;
        color: #ededed !important;
    }
    [data-testid="stSidebarCollapsedControl"] [data-testid="stIconMaterial"],
    [data-testid="collapsedControl"] [data-testid="stIconMaterial"],
    [data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {
        color: #ededed !important;
        font-size: 1.25rem !important;
    }

    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: var(--oa-composer-max) !important;
    }

    .block-container, section, input, textarea,
    [data-testid="stSidebar"] {
        direction: rtl; text-align: right;
    }
    /* Keep chat_input LTR so + / mic / send stay in Streamlit's native order */
    [data-testid="stChatInput"] {
        direction: ltr !important;
        text-align: left !important;
    }
    [data-testid="stChatInput"] textarea {
        direction: rtl !important;
        text-align: right !important;
    }
    [role=radiogroup], pre, code, [data-testid="stCode"] {
        direction: ltr; text-align: left;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--oa-surface) !important;
        border-left: 1px solid #1a1a1a;
    }
    [data-testid="stSidebar"] .element-container {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        gap: 0.1rem !important;
        margin: 0 !important;
        align-items: center !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.05rem !important;
    }
    [data-testid="stSidebar"] .stButton { margin: 0 !important; }
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: none !important;
        border-radius: 6px !important;
        color: #9a9a9a !important;
        font-family: var(--oa-font) !important;
        font-size: 0.66rem !important;
        font-weight: 400 !important;
        line-height: 1.2 !important;
        text-align: right !important;
        justify-content: flex-start !important;
        padding: 0.08rem 0.28rem !important;
        min-height: 1.1rem !important;
        height: auto !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #161616 !important;
        color: #ececec !important;
    }
    [data-testid="stSidebar"] button[kind="primary"] {
        background: #e8e8e8 !important;
        color: #111 !important;
        border-radius: 999px !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        justify-content: center !important;
        padding: 0.42rem 0.75rem !important;
        min-height: 2rem !important;
        margin: 0.2rem 0 0.4rem 0 !important;
    }
    /* Trash: hidden until the history row is hovered (match by widget key) */
    [data-testid="stSidebar"] [class*="st-key-hist_del_"] {
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover
    [class*="st-key-hist_del_"] {
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }
    [data-testid="stSidebar"] [class*="st-key-hist_del_"] .stButton > button {
        justify-content: center !important;
        text-align: center !important;
        font-size: 0.65rem !important;
        min-height: 1.1rem !important;
        padding: 0 !important;
        border-radius: 999px !important;
        color: #888 !important;
    }
    [data-testid="stSidebar"] [class*="st-key-hist_del_"] .stButton > button:hover {
        color: #ff6b6b !important;
        background: rgba(255,80,80,0.12) !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarContent"],
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
    }
    .oa-side-brand {
        direction: rtl;
        text-align: center !important;
        font-weight: 700;
        font-size: 0.95rem;
        color: var(--oa-text);
        margin: 0.15rem 0 1.25rem 0;
        padding: 0.1rem 0;
        font-family: var(--oa-font);
        width: 100%;
        line-height: 1.4;
    }
    /* Streamlit does not nest the button inside this div — space via brand margin-bottom */
    .oa-new-chat-wrap {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] .st-key-sidebar_new_chat {
        position: relative !important;
        z-index: 30 !important;
        margin-top: 0.15rem !important;
        pointer-events: auto !important;
    }
    [data-testid="stSidebar"] .st-key-sidebar_new_chat .stButton > button {
        pointer-events: auto !important;
        cursor: pointer !important;
    }
    .oa-side-section {
        direction: rtl; color: #555; font-size: 0.58rem; font-weight: 600;
        letter-spacing: 0.08em; margin: 0.55rem 0 0.35rem 0;
        text-transform: uppercase; font-family: var(--oa-font);
        line-height: 1.4;
    }
    .oa-status-line { direction: rtl; color: #777; font-size: 0.7rem; margin-top: 0.4rem; }
    .oa-spacer-top { height: 8vh; }

    /* Multi-line prompt box, lifted toward vertical center */
    [data-testid="stBottom"] {
        background: transparent !important;
        padding-bottom: min(28vh, 240px) !important;
    }
    /* With chat messages: keep composer near the bottom */
    .stApp:has([data-testid="stChatMessage"]) [data-testid="stBottom"] {
        padding-bottom: 1.5rem !important;
    }
    [data-testid="stBottomBlockContainer"] {
        max-width: var(--oa-composer-max) !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        width: 100% !important;
    }
    [data-testid="stChatInput"] {
        background: transparent !important;
        border-top: none !important;
        padding-bottom: 0.35rem !important;
        max-width: var(--oa-composer-max) !important;
        width: 100% !important;
        margin: 0 auto !important;
    }
    [data-testid="stChatInput"] > div {
        background: #121212 !important;
        border: 1px solid #2c2c2c !important;
        border-radius: 24px !important;
        max-width: var(--oa-composer-max) !important;
        width: 100% !important;
        margin: 0 auto !important;
        min-height: 8.5rem !important;
        padding: 1rem 1rem 0.65rem 1rem !important;
        box-shadow: 0 10px 36px rgba(0, 0, 0, 0.4);
        box-sizing: border-box !important;
    }
    /* Native row is [textarea][+][?][mic+send]. Group all keys on the LEFT. */
    [data-testid="stChatInput"] > div > div {
        align-items: center !important;
    }
    [data-testid="stChatInput"] > div > div > div:nth-child(1) {
        order: 3 !important;
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }
    [data-testid="stChatInput"] > div > div > div:nth-child(2) {
        order: 1 !important;
    }
    [data-testid="stChatInput"] > div > div > div:nth-child(3) {
        order: 4 !important;
    }
    [data-testid="stChatInput"] > div > div > div:nth-child(4) {
        order: 2 !important;
    }
    [data-testid="stChatInput"] textarea {
        font-family: var(--oa-font) !important;
        font-size: 1.12rem !important;
        line-height: 1.65 !important;
        color: #ededed !important;
        min-height: 4.75rem !important;
        height: auto !important;
        max-height: 40vh !important;
        resize: none !important;
        overflow-y: auto !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #6a6a6a !important;
        font-family: var(--oa-font) !important;
        font-size: 1.1rem !important;
    }

    [data-testid="stChatInput"] button {
        min-height: 2rem !important;
        max-height: 2rem !important;
        width: 2rem !important;
        min-width: 2rem !important;
        padding: 0 !important;
        border-radius: 999px !important;
        color: rgba(237, 237, 237, 0.9) !important;
        background: transparent !important;
        border: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stChatInput"] button svg {
        width: 1.15rem !important;
        height: 1.15rem !important;
    }
    [data-testid="stChatInputFileUploadButton"] {
        display: inline-flex !important;
        align-items: center !important;
    }
    [data-testid="stChatInputFileUploadButton"] button {
        background: transparent !important;
        border: none !important;
        color: #cfcfcf !important;
    }
    /*
     * Keep + / mic / send together on one side (no margin-left:auto).
     * Real mic testid in Streamlit 1.63: stChatInputMicButton.
     */
    [data-testid="stChatInputMicButton"],
    [data-testid="stChatInput"] button[aria-label*="Record" i],
    [data-testid="stChatInput"] button[aria-label*="recording" i],
    [data-testid="stChatInputAudioButton"] {
        background: #ececec !important;
        color: #111111 !important;
        border: none !important;
        margin-left: 0 !important;
    }
    [data-testid="stChatInputMicButton"] [data-testid="stIconMaterial"],
    [data-testid="stChatInput"] button[aria-label*="Record" i] [data-testid="stIconMaterial"],
    [data-testid="stChatInput"] button[aria-label*="recording" i] [data-testid="stIconMaterial"],
    [data-testid="stChatInputAudioButton"] [data-testid="stIconMaterial"] {
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        font-size: 1.2rem !important;
        line-height: 1 !important;
    }
    [data-testid="stChatInputMicButton"] svg,
    [data-testid="stChatInput"] button[aria-label*="Record" i] svg,
    [data-testid="stChatInput"] button[aria-label*="recording" i] svg {
        fill: #111111 !important;
        color: #111111 !important;
    }
    /* Send / Stop */
    [data-testid="stChatInputSubmitButton"]:not(:disabled) {
        background: #ececec !important;
        color: #111111 !important;
        border: none !important;
        margin-left: 0 !important;
    }
    [data-testid="stChatInputSubmitButton"]:not(:disabled) [data-testid="stIconMaterial"] {
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
    }
    [data-testid="stChatInputSubmitButton"]:not(:disabled) svg {
        fill: #111111 !important;
        color: #111111 !important;
    }
    [data-testid="stChatInputSubmitButton"]:disabled {
        background: transparent !important;
        color: rgba(237, 237, 237, 0.3) !important;
        border: 1px solid #2a2a2a !important;
        margin-left: 0 !important;
    }

    /*
     * Real Streamlit voice button stays hidden (React-safe).
     * Visible #oa-voice-proxy is injected beside + / mic / send inside the box.
     */
    [data-testid="stElementContainer"]:has([class*="st-key-composer_voice_call"]),
    .element-container:has([class*="st-key-composer_voice_call"]),
    [class*="st-key-composer_voice_call"] {
        position: fixed !important;
        left: -10000px !important;
        top: 0 !important;
        width: 1px !important;
        height: 1px !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        border: none !important;
    }
    #oa-voice-proxy {
        width: 2rem !important;
        min-width: 2rem !important;
        height: 2rem !important;
        min-height: 2rem !important;
        max-height: 2rem !important;
        margin: 0 0.2rem 0 0 !important;
        padding: 0 !important;
        border: none !important;
        border-radius: 999px !important;
        background: #ececec !important;
        color: #111111 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        flex: 0 0 auto !important;
        line-height: 1 !important;
    }
    #oa-voice-proxy:hover {
        background: #ffffff !important;
    }
    #oa-voice-proxy .material-symbols-rounded,
    #oa-voice-proxy [data-testid="stIconMaterial"] {
        font-family: var(--oa-icons) !important;
        font-size: 1.15rem !important;
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        line-height: 1 !important;
        font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24;
    }

    .oa-chips { direction: rtl; display: flex; flex-wrap: wrap; gap: 0.35rem; margin: 0 0 0.5rem 0; }
    .oa-chip {
        display: inline-flex; gap: 0.3rem; padding: 0.25rem 0.55rem;
        border: 1px solid #2a2a2a; border-radius: 999px; background: #141414;
        color: #eee; font-size: 0.75rem; font-family: var(--oa-font);
    }
    .oa-chip small { color: #888; font-size: 0.65rem; }
    .oa-chip-remove {
        display: inline-flex; align-items: center; justify-content: center;
        width: 1.35rem; height: 1.35rem; border-radius: 999px;
        border: 1px solid #2a2a2a; background: #141414; color: #888 !important;
        text-decoration: none !important; font-size: 0.95rem; line-height: 1;
        margin-inline-start: 0.15rem;
    }
    .oa-chip-remove:hover {
        color: #ff6b6b !important; background: rgba(255,80,80,0.12);
    }

    /* Sidebar model select — under «گفتگوی جدید» */
    [data-testid="stSidebar"] .oa-side-model {
        margin: 0.35rem 0 0.55rem 0;
    }
    [data-testid="stSidebar"] .st-key-sidebar_model_select {
        margin: 0 !important;
    }
    [data-testid="stSidebar"] .st-key-sidebar_model_select label {
        display: none !important;
    }
    [data-testid="stSidebar"] .st-key-sidebar_model_select [data-baseweb="select"] > div {
        background: #121212 !important;
        border: 1px solid #2c2c2c !important;
        border-radius: 999px !important;
        min-height: 2rem !important;
        font-size: 0.8rem !important;
        font-family: var(--oa-font) !important;
        color: #ededed !important;
    }
    .oa-dl-head {
        direction: rtl;
        text-align: right;
        font-family: var(--oa-font);
        margin-bottom: 0.5rem;
        line-height: 1.5;
    }
    .oa-dl-head span { color: #888; font-size: 0.85rem; }
    .oa-dl-percent {
        direction: rtl;
        text-align: right;
        font-family: var(--oa-font);
        font-size: 0.9rem;
        color: #ddd;
        margin: 0.35rem 0;
    }

    .oa-attach-hint {
        direction: rtl;
        color: #7a7a7a;
        font-size: 0.75rem;
        margin: 0 0 0.35rem 0;
        font-family: var(--oa-font);
    }

    .oa-hist-list {
        direction: rtl;
        margin: 0.15rem 0 0.35rem 0;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
    }
    .oa-hist-row {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.12rem 0.1rem;
        border-radius: 6px;
        line-height: 1.25;
    }
    .oa-hist-row:hover { background: #141414; }
    .oa-hist-item {
        flex: 1;
        color: #9a9a9a !important;
        text-decoration: none !important;
        font-size: 0.72rem !important;
        font-weight: 400 !important;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .oa-hist-item:hover { color: #ececec !important; }
    .oa-hist-active {
        color: #f2f2f2 !important;
        font-weight: 500 !important;
    }
    .oa-hist-del {
        flex: 0 0 auto;
        color: #555 !important;
        text-decoration: none !important;
        font-size: 0.7rem !important;
        width: 1.2rem;
        height: 1.2rem;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 999px;
        opacity: 0.55;
    }
    .oa-hist-del:hover {
        opacity: 1;
        color: #ff6b6b !important;
        background: rgba(255,80,80,0.12);
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 2rem !important;
            max-width: 100% !important;
        }
        .oa-spacer-top { height: 2vh; }
        [data-testid="stBottom"] {
            padding-bottom: min(22vh, 180px) !important;
        }
        .stApp:has([data-testid="stChatMessage"]) [data-testid="stBottom"] {
            padding-bottom: 1rem !important;
        }
        [data-testid="stChatInput"],
        [data-testid="stChatInput"] > div,
        [data-testid="stBottomBlockContainer"] {
            max-width: 100% !important;
        }
        [data-testid="stChatInput"] > div {
            min-height: 7rem !important;
        }
        [data-testid="stChatInput"] textarea {
            font-size: 1rem !important;
            min-height: 3.75rem !important;
        }
    }
</style>
"""

ABOUT: Final[str] = """
<p class="oa-status-line">آفلاین · Ollama</p>
"""

BRAND_HTML: Final[str] = ""

EMPTY_CHAT_HTML: Final[str] = """
<div class="oa-empty-chat oa-spacer-top" aria-hidden="true"></div>
"""

SIDEBAR_BRAND_HTML: Final[str] = """
<div class="oa-side-brand" dir="rtl" style="text-align:center;">هوش مصنوعی آفلاین</div>
"""

SETTINGS: Final[str] = "تنظیمات"
PAGE_TITLE: Final[str] = "هوش مصنوعی آفلاین"
PAGE_HEADER: Final[str] = "هوش مصنوعی آفلاین"
PAGE_TAGLINE: Final[str] = ""
TOOLS_HEADER: Final[str] = "ابزارها"
TOOLS_TAB_FILES: Final[str] = "فایل"
TOOLS_TAB_VOICE: Final[str] = "صوت"
MODEL_DETAILS_EXPANDER: Final[str] = "جزئیات مدل"
SELECTED_MODEL: Final[str] = "مدل فعلی:"
SELECT_YOUR_MODEL: Final[str] = "مدل"
MODEL_DETAILS_LABEL: Final[str] = "جزئیات مدل انتخاب‌شده"
DOWNLOAD_SIZE_LABEL: Final[str] = "حجم دانلود تقریبی"
RAM_NEED_LABEL: Final[str] = "رم تقریبی موردنیاز"
MODEL_CATEGORY_LABEL: Final[str] = "دسته"
MODEL_DESCRIPTION_LABEL: Final[str] = "توضیحات"
DOWNLOADED_YES: Final[str] = "وضعیت: دانلود شده و روی سیستم موجود است"
DOWNLOADED_NO: Final[str] = "وضعیت: هنوز دانلود نشده"
DOWNLOAD_DIALOG_TITLE: Final[str] = "دانلود مدل"
DOWNLOAD_WAITING: Final[str] = "در حال آماده‌سازی دانلود..."
DOWNLOAD_DONE: Final[str] = "دانلود کامل شد."
DOWNLOAD_FAILED: Final[str] = "دانلود ناموفق بود."
DOWNLOAD_RETRY: Final[str] = "تلاش دوباره"
DOWNLOAD_USE_MODEL: Final[str] = "استفاده از این مدل"
DOWNLOAD_CLOSE: Final[str] = "بستن"
USER_PROMPT_PLACEHOLDER: Final[str] = "بپرسید، بسازید، یا فایل پیوست کنید..."
THINKING_STATUS: Final[str] = "در حال فکر کردن…"
THINKING_STATUS_DONE: Final[str] = "پاسخ آماده شد"
THINKING_STATUS_HINT: Final[str] = "مدل در حال آماده‌سازی پاسخ است. برای توقف، Stop را بزنید."
CLEAR_CHAT: Final[str] = "گفتگوی جدید"
REFRESH_MODELS: Final[str] = "بروزرسانی مدل‌ها"
HISTORY_HEADER: Final[str] = "گفتگوها"
HISTORY_SELECT_LABEL: Final[str] = "گفتگوی قبلی"
HISTORY_DELETE_ICON: Final[str] = "🗑"
COMPOSER_SEND: Final[str] = "↑"
COMPOSER_MIC: Final[str] = "🎤"
ATTACH_PREVIEW_LABEL: Final[str] = "پیوست‌شده"
ATTACH_REMOVE: Final[str] = "حذف پیوست"
ATTACH_WAITING: Final[str] = "فایل آماده است — بنویسید چه کاری انجام شود"
ATTACH_UNSUPPORTED: Final[str] = "این نوع فایل پشتیبانی نمی‌شود."
CHAT_FILE_TYPES: Final[tuple[str, ...]] = (
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
)
HISTORY_DELETE: Final[str] = "حذف گفتگوی انتخاب‌شده"
HISTORY_DELETE_ALL: Final[str] = "حذف همه تاریخچه"
HISTORY_EMPTY: Final[str] = "هنوز گفتگوی ذخیره‌شده‌ای وجود ندارد."
HISTORY_LOADED: Final[str] = "گفتگو بارگذاری شد."
HISTORY_DELETED: Final[str] = "گفتگو حذف شد."
HISTORY_NEW: Final[str] = "گفتگوی جدید شروع شد."
HISTORY_NONE_OPTION: Final[str] = "— انتخاب کنید —"
HISTORY_SAVED: Final[str] = "گفتگو در تاریخچه ذخیره شد."
HISTORY_SAVE_FAILED: Final[str] = "ذخیره تاریخچه ناموفق بود."
HISTORY_VOICE_PREFIX: Final[str] = "🎤 [صوتی]"
HISTORY_FILE_PREFIX: Final[str] = "📎 [فایل]"
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
VOICE_CALL_BUTTON: Final[str] = "مکالمه صوتی"
VOICE_CALL_ICON: Final[str] = ":material/headphones:"
VOICE_CALL_NEXT: Final[str] = "صحبت کنید"
VOICE_CALL_STOP: Final[str] = "پایان مکالمه"
VOICE_CALL_HINT: Final[str] = (
    "مکالمه صوتی: صحبت کنید؛ بعد از سکوت، پاسخ با صدا پخش می‌شود."
)
VOICE_CALL_ACTIVE_HINT: Final[str] = (
    "مکالمه صوتی فعال است. برای نوبت بعد دوباره آیکن هدفون را بزنید."
)
VOICE_CALL_NO_MODEL: Final[str] = "ابتدا مدل چت را آماده کنید، بعد مکالمه صوتی را شروع کنید."
VOICE_HELP: Final[str] = (
    "صحبت کنید. گفتار با Whisper کم‌رم به متن تبدیل می‌شود، مدل جواب می‌دهد، "
    "و پاسخ با Edge یا TTS آفلاین خوانده می‌شود. "
    "چت و Whisper آفلاین‌اند؛ Edge به اینترنت نیاز دارد."
)
VOICE_WHISPER_LABEL: Final[str] = "مدل Whisper"
VOICE_EDGE_LABEL: Final[str] = "صدای پاسخ"
VOICE_TTS_ENGINE_LABEL: Final[str] = "موتور گفتار (TTS)"
VOICE_TTS_EDGE: Final[str] = "Edge — کیفیت بهتر (نیاز به اینترنت)"
VOICE_TTS_OFFLINE: Final[str] = "آفلاین — صدای ویندوز (بدون اینترنت)"
VOICE_OFFLINE_HINT: Final[str] = (
    "اگر صدای فارسی در ویندوز نصب نباشد، متن فارسی با صدای انگلیسی خوانده می‌شود. "
    "برای کیفیت بهتر فارسی، Edge را انتخاب کنید یا Voice فارسی ویندوز را نصب کنید."
)
VOICE_OFFLINE_VOICE_LABEL: Final[str] = "صدای سیستم"
VOICE_OFFLINE_AUTO: Final[str] = "خودکار (ترجیح فارسی اگر موجود باشد)"
VOICE_OFFLINE_NO_VOICE: Final[str] = (
    "صدای سیستمی پیدا نشد. در تنظیمات ویندوز Speech یک صدا نصب کنید، "
    "یا موقتاً Edge را انتخاب کنید."
)
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
    "برای دقت بهتر: Whisper را روی «خودکار» یا «medium» بگذارید، "
    "نزدیک میکروفون واضح حرف بزنید و تا تمام شدن جمله کمی مکث کنید. "
    "قبل از شنیدن، مدل چت موقتاً از رم خارج می‌شود."
)
VOICE_USED_MODEL_LABEL: Final[str] = "مدل Whisper استفاده‌شده"
VOICE_RECORD_SPINNER: Final[str] = "در حال ضبط... بعد از سکوت، ضبط خودش تمام می‌شود."
VOICE_STT_SPINNER: Final[str] = "در حال تبدیل گفتار به متن با Whisper..."
VOICE_TTS_SPINNER: Final[str] = "در حال ساخت صدای پاسخ..."
VOICE_TTS_SPINNER_EDGE: Final[str] = "در حال ساخت صدای پاسخ با Edge..."
VOICE_TTS_SPINNER_OFFLINE: Final[str] = "در حال ساخت صدای پاسخ آفلاین (ویندوز)..."
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
