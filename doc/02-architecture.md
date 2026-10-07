<div dir="rtl">

# ۲) معماری

## لایه‌ها

```text
┌─────────────────────────────────────────┐
│  streamlit_app.py                        │  ورود، chat_input، orchestration
├─────────────────────────────────────────┤
│  chatbot_functions.py + chatbot_constants │  UI، session_state، دیالوگ‌ها
├─────────────────────────────────────────┤
│  dt_analysis / dt_history / dt_files     │  دامنه: فایل، تاریخچه، تحلیل
│  dt_recorder / dt_tts* / dt_ollama_mgr   │  صوت، TTS، رم و دانلود
├─────────────────────────────────────────┤
│  dtx_ollama / dtx_whisper / dtx_dotenv   │  کلاینت Ollama، STT، env
├─────────────────────────────────────────┤
│  Ollama API · Whisper · Edge/SAPI · SQLite│  بیرون از پروسهٔ Python
└─────────────────────────────────────────┘
```

## جریان سطح بالا

1. کاربر UI را باز می‌کند → `main()` کانفیگ و session را می‌سازد.
2. `ensure_ollama_ready()` اگر سرویس خاموش باشد سعی در استارت می‌کند.
3. `prepare_selected_model()` قانون رم را اعمال و مدل را آماده می‌کند.
4. سایدبار: گفتگوی جدید، انتخاب مدل، لیست تاریخچه، تنظیمات صوت.
5. ورودی اصلی `st.chat_input` (متن + فایل + صوت مرورگر) → `handle_chat_input_value`.
6. پاسخ مدل از `dtx_ollama.chat` / `chat_with_image` می‌آید و در SQLite ذخیره می‌شود.

## قانون رم (سراسری)

قبل از استارت/لود هر مدل (چت، vision، embedding، Whisper):

1. رم آزاد خوانده می‌شود (`psutil` از طریق `dt_ollama_manager`)
2. نیاز تقریبی مدل از کاتالوگ / جدول Whisper برآورد می‌شود
3. حاشیهٔ امن سیستم نگه داشته می‌شود (`RAM_SAFETY_MARGIN_BYTES`)
4. اگر کافی نبود: unload مدل(های) لودشده در Ollama و در صورت نیاز آزاد کردن Whisper
5. اگر باز هم کافی نبود: استارت متوقف و پیام فارسی نشان داده می‌شود

در مکالمه صوتی، بعد از STT معمولاً مدل Whisper آزاد می‌شود تا جای مدل چت باز شود.

## ذخیره‌سازی

| مسیر | نقش |
|------|-----|
| `data/chat_history.db` | SQLite گفتگوها و پیام‌ها (gitignore) |
| `temp/recordings/` | فایل‌های ضبط موقت |
| `temp/tts/` | خروجی صوت TTS |
| `temp/` آپلودها | فایل‌های پیوست موقت |
| `.env` | `OLLAMA_HOST`، `OLLAMA_MODEL` |

## Session state مهم (Streamlit)

- `messages` — لیست پیام‌های چت جاری
- `conversation_id` — شناسهٔ ردیف SQLite
- `model_name` / `model_ready` / `model_options_cache`
- `ollama_ready` / `ollama_status_message`
- `pending_attachments` — فایل‌های پیوست‌شده منتظر پرامپت
- `history_delete_pending` — صف دیالوگ تأیید حذف
- `download_dialog_model` — مدل در حال دانلود در مدال
- `voice_*` — تنظیمات و بافر صوت/TTS
- `composer_nonce` — ریست ویجت `chat_input` بعد از گفتگوی جدید

</div>
