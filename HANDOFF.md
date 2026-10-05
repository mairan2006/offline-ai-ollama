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
5. TTS فعلاً **Edge**؛ بعداً گزینهٔ آفلاین در فاز F
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
| F TTS آفلاین به‌صورت گزینه + پایدارسازی | ⏳ بعدی |

آخرین کامیت روی `main`: فاز E  
`Complete Phase E voice chat with low-RAM Whisper and Edge TTS.`

## بدهی‌ها / باگ‌های باز

1. **Whisper فارسی:** پیش‌فرض فاز E مدل `small` است. در تست مصنوعی Edge→Whisper هنوز کمی غلط املایی می‌دهد، ولی قابل فهم است؛ با میکروفون واقعی معمولاً بهتر است. اگر رم کم است بعد از STT مدل از حافظه خارج می‌شود تا `gemma3:4b` جا بگیرد.
2. تست کامل عکس/PDF در فاز D انجام نشد؛ هنگام کار بعدی در صورت نیاز کامل شود.
3. دانلود بعضی مدل‌ها روی اینترنت کند ممکن است خطا بدهد؛ timeout/retry بعداً.
4. ضبط فاز E فایل `wav` می‌سازد و بدون ffmpeg به Whisper می‌رسد. برای `mp3`/`webm` از `imageio-ffmpeg` استفاده می‌شود.

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
dt_tts_edge.py
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

## فاز بعدی (F)

فاز F: گزینهٔ TTS آفلاین + پایدارسازی + README نهایی.

## نحوهٔ ادامه برای کاربر

1. در Cursor یک **Agent Chat جدید** باز کن
2. همین فولدر پروژه را باز داشته باش: `C:\Users\Maira\source\offline-ai-ollama`
3. بگو:

```text
ادامه پروژه از HANDOFF.md و PLAN.md
فعلا برو فاز F
(قوانین RTL، پوش فقط با دستور من، سبک DT)
```

</div>
