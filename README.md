<div dir="rtl">

# هوش مصنوعی آفلاین · Ollama + Streamlit

دستیار فارسی آفلاین با سبک کدنویسی فولدر مرجع DT.

## فاز فعلی

**فاز E** — مکالمهٔ صوتی (ضبط، Whisper، پاسخ مدل، Edge TTS)  
فاز D (تحلیل فایل) هم در همین برنامه هست.

## اجرا

```powershell
cd C:\Users\Maira\source\offline-ai-ollama
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run .\streamlit_app.py
```

پیش‌نیاز: Ollama روشن باشد و مدل در `.env` موجود باشد (پیش‌فرض: `gemma3:4b`).

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
dt_tts_edge.py
dtx_whisper.py
dtx_dotenv.py
dtx_ollama.py
data/chat_history.db   # محلی؛ در git نیست
PLAN.md
```

جزئیات فازها و تیک‌ها: `PLAN.md`

</div>
