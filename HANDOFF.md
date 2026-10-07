<div dir="rtl">

# تحویل کار به Agent جدید

این فایل برای ادامهٔ پروژه در یک چت/Agent تازه است.  
قبل از هر کدنویسی، `PLAN.md` و همین فایل را بخوان.

## مسیرها

- پروژه: `C:\Users\Maira\source\offline-ai-ollama`
- ریپوی GitHub (Private): https://github.com/mairan2006/offline-ai-ollama
- اکانت: `mairan2006`
- فولدر مرجع سبک کد: `D:\Film\Learning\AI_LLM_DT\SourceCode`

## قوانین قطعی کاربر

1. پاسخ‌ها و توضیحات فارسی **راست‌به‌چپ** (`dir="rtl"`)
2. **کد نزن مگر برای همان فازی که کاربر گفته**
3. **پوش فقط وقتی کاربر بگوید «پوش»**
4. سبک کدنویسی مثل فولدر مرجع DT (`dt_` / `dtx_` / `*_constants.py` / type hint / RTL Streamlit)
5. TTS: Edge یا آفلاین (ویندوز)؛ بعداً در صورت نیاز گزینه‌های بیشتر
6. قبل از استارت هر مدل: چک رم + حاشیه امن + در صورت نیاز unload مدل قبلی
7. بعد از هر پوش موفق: تیک‌های `PLAN.md` را به‌روز کن

## وضعیت فازها

| فاز | وضعیت |
|---|---|
| A اسکلت Streamlit + چت + استارت Ollama | ✅ پوش شده |
| B کاتالوگ مدل / دانلود / رم | ✅ پوش شده |
| C هیستوری SQLite + لود فوری از دراپ‌دان | ✅ پوش شده |
| D تحلیل فایل (عکس/PDF/متن/صوت) | ✅ پوش شده (با بدهی فنی) |
| E مکالمه صوتی پیشرفته | ✅ پوش شده |
| F TTS آفلاین به‌صورت گزینه + پایدارسازی | ✅ پوش شده |
| G رفع بدهی هیستوری صوت/فایل | ✅ پوش شده |
| H UI شبیه Cursor (خلاصه و شیک) | ✅ پوش شده |
| I دکمهٔ + فایل و کار با پرامپت | ✅ پوش شده |

آخرین کامیت روی `main`: پولیش UI بعد از H/I  
`Polish chat UX: stop mode, history buttons, file multi-intent.`

## بدهی‌ها / باگ‌های باز

1. **Whisper فارسی:** با `faster-whisper` و انتخاب خودکار medium/turbo بهتر شده؛ هنوز کامل نیست.
2. تست کامل عکس/PDF در فاز D انجام نشد؛ هنگام کار بعدی در صورت نیاز کامل شود.
3. دانلود بعضی مدل‌ها روی اینترنت کند ممکن است خطا بدهد؛ timeout/retry بعداً.
4. ضبط فاز E فایل `wav` می‌سازد و بدون ffmpeg به Whisper می‌رسد. برای `mp3`/`webm` از `imageio-ffmpeg` استفاده می‌شود.
5. باکس پرامپت پهن‌تر/بالاتر شد؛ دراپ‌دان مدل کنار `+` + مدال دانلود هنوز در صف پلن است.

## ساختار مهم فعلی

```
streamlit_app.py
chatbot_constants.py
chatbot_functions.py
model_constants.py
dt_utility.py
dt_llm_utility.py
dt_ollama_manager.py
dt_history.py
dt_files.py
dt_analysis.py
dt_recorder.py
dt_tts.py
dt_tts_edge.py
dt_tts_offline.py
dtx_dotenv.py
dtx_ollama.py
dtx_whisper.py
PLAN.md
HANDOFF.md
data/chat_history.db   # محلی، gitignore
```

اجرا:

```powershell
cd C:\Users\Maira\source\offline-ai-ollama
.\.venv\Scripts\Activate.ps1
streamlit run .\streamlit_app.py
```

## فاز E (پوش شده)

از مرجع استفاده شده:
- `DT_APP_Python_Sound_Recorder-main` برای ضبط با تشخیص سکوت (`dt_recorder.py`)
- Whisper با `faster-whisper` کم‌رم (`dtx_whisper.py`، گزینه خودکار/`small`/`medium`)
- `DT_Learning_Python_AI_TTS_EDGE` برای TTS فارسی Edge (`dt_tts_edge.py`)

در UI بخش «مکالمه صوتی»:
- ضبط میکروفون سیستم تا سکوت، یا ضبط مرورگر
- Whisper → پاسخ مدل در همان تاریخچه → پخش Edge
- قبل از Whisper و قبل از مدل چت، قانون رم اعمال می‌شود

## فاز F (پوش شده)

- گزینهٔ TTS: Edge / آفلاین (ویندوز SAPI)
- README نهایی RTL
- بهبود STT: انتخاب خودکار medium/turbo + پرامپت فارسی قوی‌تر
- بدهی هیستوری صوت/تحلیل فایل عمداً برای بعد مانده است

## فاز G (پوش شده)

- دراپ‌دان تاریخچه با `id` پایدار + همگام‌سازی با صف pending (بدون خطای ویجت Streamlit)
- پیام/عنوان صوت با پیشوند `🎤 [صوتی]` و فایل با `📎 [فایل]`
- `title_hint` در `save_messages` / `get_assistant_answer`
- بعد از پاسخ صوتی موفق: `st.rerun()` برای به‌روز شدن سایدبار
- بهبود کوچک STT برای واژه‌های فنی مثل «سی شارپ»

## فاز H + I (پوش شده)

- UI نزدیک cursor.com: پس‌زمینه سیاه، composer گرد، فونت Vazirmatn
- تاریخچه به‌صورت **دکمه** در سایدبار (بدون تب جدید)
- دکمهٔ `+` روی `st.chat_input`؛ `submit_mode="stop"` + وضعیت «در حال فکر کردن»
- کار روی فایل فقط بعد از پرامپت کاربر؛ درخواست چندبخشی مثل خلاصه+ترجمه پشتیبانی می‌شود
- مدل در سایدبار؛ صوت در expander تنظیمات

## اقدام بعدی پیشنهادی

1. دراپ‌دان مدل کنار `+` + مدال دانلود با درصد پایدار

## نحوهٔ ادامه برای کاربر

```text
ادامه از HANDOFF.md و PLAN.md
برو سراغ مدل کنار + و مدال دانلود
```

</div>
