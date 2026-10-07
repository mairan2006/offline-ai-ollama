<div dir="rtl">

# هوش مصنوعی آفلاین · Ollama + Streamlit

دستیار فارسی آفلاین با سبک کدنویسی فولدر مرجع DT  
(`dt_` / `dtx_` / `*_constants.py` / type hint / RTL).

## فاز فعلی

**فاز H + I پیاده‌سازی شد** — UI شبیه Cursor + دکمهٔ `+` برای فایل و کار با پرامپت  
منتظر تست کاربر و دستور «پوش».

## قابلیت‌ها

- چت فارسی با مدل‌های Ollama
- مدیریت مدل (دانلود / وضعیت / قانون رم)
- تاریخچه گفتگو با SQLite
- تحلیل فایل: عکس، PDF، متن، صوت
- مکالمه صوتی: ضبط → Whisper → پاسخ مدل → پخش صدا
- TTS: **Edge** (آنلاین، کیفیت بهتر فارسی) یا **آفلاین** (صدای ویندوز / SAPI)
  - آفلاین فارسی فقط وقتی Voice فارسی ویندوز نصب باشد درست کار می‌کند؛ وگرنه پیام می‌دهد و در مکالمه به Edge برمی‌گردد

## اجرا

```powershell
cd C:\Users\Maira\source\offline-ai-ollama
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Whisper روی GPU (RTX / CUDA 12.x) — نسخهٔ PyPI فقط CPU است:
pip install torch --index-url https://download.pytorch.org/whl/cu126
streamlit run .\streamlit_app.py
```

### پیش‌نیازها

- Ollama نصب و قابل اجرا باشد
- مدل پیش‌فرض در `.env` (مثلاً `OLLAMA_MODEL=gemma3:4b`) یا از UI انتخاب شود
- برای STT روی GPU: درایور NVIDIA + نصب `torch` از ایندکس `cu126` (بالا)
- برای TTS آفلاین: صدای Speech ویندوز نصب باشد (ترجیحاً فارسی)
- برای Edge TTS: اینترنت لازم است
- برای فایل‌های صوتی غیر `wav`: بسته `imageio-ffmpeg` (در requirements هست)

## ساختار اصلی

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
dtx_whisper.py
dtx_dotenv.py
dtx_ollama.py
data/chat_history.db   # محلی؛ در git نیست
PLAN.md
HANDOFF.md
```

## نکات رم

قبل از لود هر مدل (چت یا Whisper):

1. رم آزاد خوانده می‌شود
2. نیاز مدل برآورد می‌شود
3. حاشیه امن سیستم نگه داشته می‌شود
4. در کمبود رم، مدل قبلی unload می‌شود
5. اگر باز هم کافی نباشد، استارت متوقف و پیام فارسی نشان داده می‌شود

در مکالمه صوتی، بعد از STT مدل Whisper آزاد می‌شود تا جای مدل چت باز شود.

## بدهی‌های باز

- هیستوری مکالمه صوتی و «افزودن نتیجه تحلیل فایل» نیاز به اصلاح بعدی دارد
- دقت Whisper فارسی هنوز کامل نیست (با `faster-whisper` بهتر شده)
- تست کامل‌تر عکس/PDF و timeout دانلود مدل‌ها بعداً

جزئیات فازها و تیک‌ها: `PLAN.md`  
تحویل به Agent بعدی: `HANDOFF.md`  
مستندات کامل (ماژول‌ها و توابع): پوشهٔ [`doc/`](doc/README.md)

</div>
