<div dir="rtl">

# هوش مصنوعی آفلاین · Ollama + Python

دستیار هوش مصنوعی **کاملاً آفلاین** با مدل‌های محلی Ollama.

## امکانات

- چت استریم در خط فرمان
- پرسش از فایل‌های محلی (RAG سبک با embeddingهای Ollama)
- رابط وب Streamlit

## پیش‌نیاز

1. [Ollama](https://ollama.com) نصب و در حال اجرا باشد
2. پایتون ۳٫۱۰ یا بالاتر
3. مدل چت (روی سیستم شما از قبل هست):

```bash
ollama pull gemma3:4b
```

برای RAG:

```bash
ollama pull nomic-embed-text
```

## نصب

```bash
cd C:\Users\Maira\source\offline-ai-ollama
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## استفاده

وضعیت:

```bash
python main.py status
```

چت:

```bash
python main.py chat
```

یک سؤال:

```bash
python main.py ask "سلام، خودت را معرفی کن"
```

ایندکس اسناد (`data/docs`) و پرسش با RAG:

```bash
python main.py index
python main.py ask --rag "قابلیت‌های این پروژه چیست؟"
python main.py chat --rag
```

رابط وب:

```bash
streamlit run ui.py
```

## ساختار

```
offline-ai-ollama/
  main.py          # خط فرمان
  ui.py            # Streamlit
  config.py
  app/
    ollama_client.py
    rag.py
  data/docs/       # فایل‌های .txt / .md
```

مدل پیش‌فرض را در `.env` با `OLLAMA_MODEL` عوض کنید.

</div>
