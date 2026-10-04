<div dir="rtl">

# هوش مصنوعی آفلاین · Ollama + Streamlit

دستیار فارسی آفلاین با سبک کدنویسی فولدر مرجع DT.

## فاز فعلی

**فاز A** — اسکلت Streamlit + چت متنی ساده

## اجرا

```powershell
cd C:\Users\Maira\source\offline-ai-ollama
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run .\streamlit_app.py
```

پیش‌نیاز: Ollama روشن باشد و مدل در `.env` موجود باشد (پیش‌فرض: `gemma3:4b`).

## ساختار فاز A

```
streamlit_app.py
chatbot_constants.py
chatbot_functions.py
dt_utility.py
dt_llm_utility.py
dtx_dotenv.py
dtx_ollama.py
PLAN.md
```

جزئیات فازها و تیک‌ها: `PLAN.md`

</div>
