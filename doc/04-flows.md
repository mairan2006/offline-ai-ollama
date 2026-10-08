<div dir="rtl">

# ۴) جریان‌های اصلی برنامه

## ۴.۱ چت متنی ساده

1. کاربر متن را در `st.chat_input` می‌فرستد.
2. `handle_chat_input_value` → اگر پیوست نباشد، `handle_chat_submission` / `run_chat_turn_with_ui`.
3. پیام کاربر به `messages` اضافه می‌شود.
4. `generate_assistant_reply` / `get_assistant_answer` → `dtx_ollama.chat`.
5. پاسخ در UI استریم/نمایش و با `persist_current_conversation` در SQLite ذخیره می‌شود.
6. عنوان گفتگو از اولین پیام کاربر (یا `title_hint`) ساخته می‌شود.

## ۴.۲ پیوست فایل با `+` و پرامپت

1. کاربر فایل را از `chat_input` انتخاب می‌کند → در `pending_attachments` نگه داشته می‌شود.
2. چیپ‌های پیش‌نمایش با `render_attachment_preview` دیده می‌شوند.
3. کاربر می‌نویسد چه کار شود (مثلاً «خلاصه کن و به انگلیسی ترجمه کن»).
4. `apply_prompt_to_file` نوع فایل را تشخیص می‌دهد و intent پرامپت را می‌خواند.
5. نتیجه به‌صورت نوبت(های) چت به تاریخچه اضافه می‌شود؛ پیوست پاک می‌شود.

انواع پشتیبانی‌شده (خلاصه): تصویر، PDF، txt/md/csv، صوت mp3/wav/m4a/ogg.

## ۴.۳ مکالمه صوتی

دو مسیر ورودی:

| مسیر | منبع | ماژول |
|------|------|--------|
| میکروفون سیستم | `sounddevice` تا سکوت | `dt_recorder.record_until_silence` |
| مرورگر | `st.audio_input` / mic چت | `save_audio_bytes` |

سپس:

1. `process_voice_audio` → `dtx_whisper.transcribe` (با انتخاب مدل بر اساس رم)
2. آزادسازی Whisper در صورت نیاز رم چت
3. پاسخ مدل چت
4. TTS از طریق `dt_tts.synthesize_persian` (Edge یا آفلاین)
5. پخش با `render_voice_player`؛ ذخیره در تاریخچه با پیشوند `🎤 [صوتی]`

آیکن هدفون کنار composer با JS به دکمهٔ مخفی Streamlit وصل است (`_inject_voice_proxy_in_composer`).

## ۴.۴ تاریخچه

- لیست: دکمه‌های سایدبار (`render_history_section`)
- باز کردن: `load_conversation`
- ذخیره: `save_messages` / `persist_current_conversation`
- خروجی: `export_conversation_json` + دانلود مرورگر
- حذف تکی / همه: فقط بعد از تأیید در `open_history_delete_dialog`

## ۴.۵ انتخاب و دانلود مدل

1. تغییر مدل در selectbox سایدبار → اگر دانلود نشده، `download_dialog_model` ست می‌شود.
2. `open_model_download_dialog` دانلود پس‌زمینه را نشان می‌دهد (`start_model_download` + thread).
3. پس از اتمام، کاربر می‌تواند «استفاده از این مدل» را بزند → `apply_selected_model` → `prepare_model_for_use`.

## ۴.۶ آماده‌سازی مدل (رم)

`prepare_model_for_use`:

1. اگر مدل روی دیسک نیست → پیام نیاز به دانلود
2. `can_fit_model_in_ram` با حاشیه امن
3. در کمبود: unload مدل‌های Ollama، آزاد کردن Whisper
4. پیشنهاد مدل سبک‌تر در صورت شکست
5. در موفقیت: مدل برای چت آماده علامت می‌خورد

</div>
