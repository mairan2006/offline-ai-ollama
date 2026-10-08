<div dir="rtl">

# ۳) فایل‌ها و توابع مهم

## نقشهٔ فایل‌ها

| فایل | نقش کوتاه |
|------|-----------|
| `streamlit_app.py` | نقطهٔ ورود؛ `main()` |
| `chatbot_constants.py` | متن‌های UI، CSS (`STREAMLIT_STYLE`)، انواع فایل |
| `chatbot_functions.py` | تقریباً تمام منطق UI و orchestration |
| `model_constants.py` | کاتالوگ مدل‌ها و آستانه‌های رم |
| `dt_utility.py` | ابزار عمومی متن/زمان/پیام کنسول |
| `dt_llm_utility.py` | نقش‌ها، کلیدهای پیام، system prompt |
| `dtx_dotenv.py` | خواندن `.env` |
| `dtx_ollama.py` | کلاینت چت Ollama |
| `dt_ollama_manager.py` | استارت Ollama، دانلود، unload، قانون رم |
| `dt_history.py` | SQLite تاریخچه |
| `dt_files.py` | ذخیره آپلود و استخراج متن |
| `dt_analysis.py` | تحلیل فایل بر اساس پرامپت |
| `dt_recorder.py` | ضبط میکروفون تا سکوت |
| `dtx_whisper.py` | STT با faster-whisper / openai-whisper |
| `dt_tts.py` | روتر موتور TTS |
| `dt_tts_edge.py` | TTS آنلاین Edge |
| `dt_tts_offline.py` | TTS آفلاین ویندوز (SAPI) |
| `.streamlit/config.toml` | تم و تنظیمات سرور |
| `.env.example` | نمونهٔ متغیرهای محیطی |
| `requirements.txt` | وابستگی‌های Python |
| `PLAN.md` / `HANDOFF.md` / `README.md` | برنامه، تحویل، شروع سریع |

---

## `streamlit_app.py`

### `main()`

ترتیب اجرا:

1. `set_page_config` + `initial_session_state`
2. اطمینان از Ollama و آماده‌سازی مدل
3. `render_sidebar`
4. نمایش پیام‌ها یا empty state
5. `render_voice_player` + `render_composer`
6. `st.chat_input(..., accept_file="multiple", accept_audio=True, submit_mode="stop")`
7. `handle_chat_input_value` روی مقدار ارسالی

---

## `chatbot_constants.py`

ثابت‌های فارسی UI، HTML برند/empty chat، و رشتهٔ بزرگ CSS با کلاس‌های `.oa-*` و استایل سایدبار/دیالوگ/composer.

نمونهٔ ثابت‌های مهم:

- `DEFAULT_MODEL_NAME` — از `.env` کلید `OLLAMA_MODEL`
- `CHAT_FILE_TYPES` — پسوندهای مجاز پیوست
- `STREAMLIT_STYLE` — ظاهر تیره + RTL + دکمه‌های تاریخچه/دیالوگ
- برچسب‌های تاریخچه، صوت، دانلود، خطاها

توابع ندارد؛ فقط ثابت.

---

## `chatbot_functions.py`

لایهٔ اصلی UI. گروه‌بندی توابع:

### پیکربندی و session

| تابع | توضیح |
|------|--------|
| `set_page_config` | عنوان صفحه، layout، تزریق CSS |
| `initial_session_state` | مقداردهی اولیهٔ کلیدهای session + `history.init_db()` |
| `ensure_ollama_ready` | کش وضعیت Ollama؛ در صورت نیاز استارت |
| `refresh_model_options` | گزینه‌های مدل برای selectbox |
| `start_new_conversation` / `clear_chat_history` | ریست چت جاری |
| `ensure_conversation_exists` | ساخت ردیف SQLite در صورت نیاز |
| `persist_current_conversation` | ذخیرهٔ `messages` در DB |
| `load_conversation` | بارگذاری یک گفتگو از DB |
| `prepare_selected_model` | آماده‌سازی مدل با قانون رم |

### تاریخچه در سایدبار

| تابع | توضیح |
|------|--------|
| `_history_export_filename` | نام امن فایل JSON |
| `_trigger_json_download` | دانلود از طریق `components.html` |
| `open_history_delete_dialog` | دیالوگ تأیید حذف تکی/همه |
| `render_history_section` | دکمه‌های باز / export / حذف |

### مدل و دانلود

| تابع | توضیح |
|------|--------|
| `apply_selected_model` | سوییچ به مدل دانلودشده |
| `_on_model_select_change` | اگر مدل نبود → باز کردن مدال دانلود |
| `open_model_download_dialog` | UI پیشرفت دانلود |
| `_render_download_progress` | درصد و وضعیت job |
| `render_model_selector` | selectbox سایدبار |

### Composer و چت

| تابع | توضیح |
|------|--------|
| `render_composer` | پیوست‌ها، آیکن صوت، مدال دانلود، ضبط مرورگر در حالت خاص |
| `parse_chat_input` / `handle_chat_input_value` | تجزیهٔ خروجی `chat_input` |
| `store_uploaded_files` / `clear_pending_attachments` | مدیریت پیوست |
| `render_attachment_preview` | چیپ‌های فایل |
| `run_chat_turn_with_ui` | یک نوبت چت با UI وضعیت/Stop |
| `handle_chat_submission` | ارسال متن (+ فایل اختیاری) |
| `generate_assistant_reply` / `get_assistant_answer` | فراخوانی مدل و ذخیره |
| `render_chat_messages` | رندر حباب‌های چت |
| `render_sidebar` | برند، گفتگوی جدید، مدل، تاریخچه، تنظیمات |

### صوت و فایل

| تابع | توضیح |
|------|--------|
| `run_voice_conversation_turn` | یک نوبت صحبت با mic سیستم |
| `render_voice_call_icon` / `_inject_voice_proxy_in_composer` | آیکن هدفون در composer |
| `process_voice_audio` | STT → LLM → TTS → پخش |
| `render_voice_player` | پخش‌کنندهٔ پاسخ صوتی |
| `render_voice_conversation_section` | UI کامل تب/بخش صوت (legacy/expander) |
| `render_file_analysis_section` | تحلیل فایل با دکمه‌های صریح (مسیر قدیمی‌تر) |
| `add_analysis_result_to_chat` | افزودن نتیجه به پیام‌ها |
| `_build_file_prompt_turn` | ساخت نوبت چت از نتیجهٔ فایل |

---

## `model_constants.py`

| نماد / تابع | توضیح |
|-------------|--------|
| `MODEL_CATALOG` | دیکشنری مدل‌ها: عنوان، دسته، توضیح، حجم دانلود، رم تقریبی |
| `RAM_SAFETY_MARGIN_BYTES` | حاشیه امن (~۲ GB) |
| `RAM_ABSOLUTE_MIN_FREE_BYTES` | کف رم آزاد |
| `DEFAULT_MODEL_RAM_BYTES` / `DEFAULT_MODEL_DOWNLOAD_BYTES` | پیش‌فرض وقتی مدل در کاتالوگ نیست |
| `CATALOG_MODEL_NAMES` | لیست کلیدها |

---

## `dt_utility.py`

ابزار عمومی مستقل از Streamlit:

| تابع | توضیح |
|------|--------|
| `fix_text` | نرمال‌سازی فاصله/متن |
| `get_formated_now` | برچسب زمانی برای نام فایل |
| `format_seconds` | نمایش مدت زمان |
| `display_*_message` | پیام‌های رنگی کنسول با Rich |
| `clear_screen` / `display_divider` | کمکی CLI |

---

## `dt_llm_utility.py`

قرارداد پیام‌های چت:

- نقش‌ها: `ROLE_USER` / `ROLE_ASSISTANT` / `ROLE_SYSTEM`
- کلیدها: `KEY_NAME_ROLE` / `KEY_NAME_CONTENT`
- `SYSTEM_PROMPT` / `SYSTEM_MESSAGE` — پیام سیستمی فارسی دستیار

---

## `dtx_dotenv.py`

| تابع | توضیح |
|------|--------|
| `get_key_value(key, default)` | بارگذاری `.env` و برگرداندن مقدار با پیش‌فرض |

---

## `dtx_ollama.py`

| تابع | توضیح |
|------|--------|
| `get_offline_client` | ساخت `ollama.Client` روی `OLLAMA_HOST` |
| `chat` | چت متنی چندپیامی؛ پارامتر دما |
| `chat_with_image` | چت vision با مسیر/بایت تصویر |

ثابت‌ها: `TEMPERATURE`, `MODEL_NAME`, `BASE_URL_OFFLINE`.

---

## `dt_ollama_manager.py`

مدیریت چرخهٔ عمر Ollama و رم.

| تابع | توضیح |
|------|--------|
| `is_ollama_running` | پینگ API |
| `find_ollama_executable` / `start_ollama` | پیدا کردن و اجرای باینری |
| `ensure_ollama_running` | استارت در صورت نیاز + پیام فارسی |
| `list_downloaded_models` / `is_model_downloaded` | مدل‌های روی دیسک |
| `get_model_details` / `get_model_display_options` | جزئیات و لیبل UI |
| `start_model_download` / `_download_worker` / `pull_model` | دانلود پس‌زمینه با progress |
| `get_download_job` / `clear_finished_download_job` | وضعیت job |
| `list_loaded_models` / `unload_model` / `unload_all_loaded_models` | مدیریت VRAM/RAM Ollama |
| `get_available_ram_bytes` / `format_bytes` | خواندن رم |
| `estimate_model_ram_bytes` / `can_fit_model_in_ram` | برآورد و تصمیم |
| `prepare_model_for_use` | نقطهٔ ورود آماده‌سازی امن مدل |

---

## `dt_history.py`

SQLite در `data/chat_history.db`.

| تابع | توضیح |
|------|--------|
| `init_db` | ساخت جداول `conversations` و `messages` |
| `create_conversation` | گفتگوی جدید |
| `list_conversations` | لیست اخیر برای سایدبار |
| `get_conversation` / `get_messages` | خواندن یک گفتگو |
| `save_messages` | جایگزینی پیام‌ها + به‌روزرسانی عنوان |
| `delete_conversation` / `delete_all_conversations` | حذف |
| `export_conversation_json` | خروجی JSON برای دانلود |
| `_build_title_from_messages` | ساخت عنوان کوتاه از متن |

---

## `dt_files.py`

| تابع | توضیح |
|------|--------|
| `detect_file_kind` | `image` / `pdf` / `text` / `audio` / ناشناخته |
| `save_uploaded_file` | ذخیره در `temp` با timestamp |
| `extract_text_from_txt` / `extract_text_from_pdf` / `extract_text` | استخراج متن |
| `truncate_text` | سقف طول برای پرامپت مدل |

---

## `dt_analysis.py`

| تابع | توضیح |
|------|--------|
| `apply_prompt_to_file` | **ورودی اصلی فاز I**: پرامپت کاربر + مسیر فایل |
| `_prompt_wants_summary` / `_prompt_wants_translate_*` | تشخیص intent از متن فارسی/انگلیسی |
| `_apply_text_prompt` | خلاصه/ترجمه/چندمرحله‌ای روی متن |
| `analyze_image` | توضیح تصویر با مدل vision |
| `summarize_document` | خلاصه PDF/متن |
| `translate_text` / `translate_document` | ترجمه |
| `transcribe_audio` | STT فایل صوتی از مسیر تحلیل |
| `_ask_ollama` | کمک‌کنندهٔ فراخوانی چت با مدیریت رم |

---

## `dt_recorder.py`

| تابع | توضیح |
|------|--------|
| `get_default_input_device_name` | نام mic پیش‌فرض |
| `record_until_silence` | ضبط mono ۱۶kHz تا سکوت پس از گفتار یا سقف زمان |
| `save_audio` | ذخیره فریم‌ها به WAV ۱۶-bit |
| `save_audio_bytes` | ذخیره بایت‌های مرورگر/آپلود |

ثابت مهم: `THRESHOLD` (آستانهٔ دامنه برای تشخیص گفتار).

---

## `dtx_whisper.py`

| تابع | توضیح |
|------|--------|
| `estimate_ram_bytes` / `choose_model_for_ram` | انتخاب tiny/base/small/medium بر اساس رم |
| `release_model` / `is_model_loaded` | کش مدل در حافظهٔ پروسس |
| `_load_model` | اولویت `faster-whisper` روی CUDA/CPU؛ fallback به `openai-whisper` |
| `prepare_whisper_audio` / `convert_audio_to_wav` | آماده‌سازی ورودی (ffmpeg در صورت نیاز) |
| `transcribe` | API اصلی STT فارسی با اصلاحات ساده |
| `apply_simple_persian_fixes` | دیکشنری کوچک اصلاح اشتباهات رایج |

---

## `dt_tts.py` / `dt_tts_edge.py` / `dt_tts_offline.py`

### `dt_tts.py` (روتر)

| تابع | توضیح |
|------|--------|
| `normalize_engine` | `edge` یا `offline` |
| `synthesize_persian` | فراخوانی موتور انتخابی |
| `list_offline_voices` / `has_persian_offline_voice` | پروکسی به ماژول آفلاین |

### `dt_tts_edge.py`

| تابع | توضیح |
|------|--------|
| `clean_text_for_speech` / `fix_text_for_speech` | آماده‌سازی متن و سقف طول |
| `convert_text_to_speech` / `synthesize_persian` | ساخت MP3 با `edge-tts` |
| `VOICES_FEMALE` / `VOICES_MALE` | صداهای فارسی (مثلاً Dilara / Farid) |

### `dt_tts_offline.py`

| تابع | توضیح |
|------|--------|
| `list_system_voices` | صداهای SAPI ویندوز |
| `find_best_offline_voice_id` | ترجیح فارسی |
| `convert_text_to_speech` / `synthesize_persian` | خروجی WAV آفلاین |
| `has_persian_system_voice` | تشخیص وجود Voice فارسی |

---

## سایر فایل‌های پیکربندی

### `.streamlit/config.toml`

تم تیره، رنگ‌ها، غیرفعال کردن آمار مرورگر.

### `.env.example`

```env
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=gemma3:4b
```

### `.gitignore`

معمولاً `.env`، دیتابیس محلی، کش، و فایل‌های موقت را کنار می‌گذارد.

### `.cursor/rules/persian-rtl.mdc`

قانون workspace برای متن فارسی RTL در پاسخ‌ها و مستندات کاربرمحور.

---

## وابستگی فراخوانی (خلاصه)

```text
streamlit_app
  └─ chatbot_functions
       ├─ chatbot_constants
       ├─ dt_ollama_manager ── dtx_ollama, model_constants, dtx_dotenv
       ├─ dt_history
       ├─ dt_analysis ── dt_files, dtx_whisper, dtx_ollama, dt_ollama_manager
       ├─ dt_recorder
       ├─ dtx_whisper
       └─ dt_tts ── dt_tts_edge / dt_tts_offline
```

</div>
