<div dir="rtl">

# هوش مصنوعی آفلاین · Ollama + Streamlit

دستیار فارسی آفلاین با سبک کدنویسی فولدر مرجع DT.

## فاز فعلی

**فاز B** — مدیریت مدل‌ها + دانلود + کنترل رم

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
dtx_dotenv.py
dtx_ollama.py
PLAN.md
```

جزئیات فازها و تیک‌ها: `PLAN.md`

</div>
