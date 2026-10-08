<div dir="rtl">

# ۵) نصب، پیکربندی و اجرا

## پیش‌نیازها

- Python 3.10+ (در محیط فعلی 3.14 هم تست شده)
- [Ollama](https://ollama.com) نصب و در PATH
- حداقل یک مدل محلی (مثلاً `gemma4:e4b-it-qat` یا مقدار `.env`)
- برای GPU Whisper: درایور NVIDIA + `torch` از ایندکس CUDA (نه PyPI خالص)
- اختیاری: اینترنت برای Edge TTS و اولین دانلود مدل‌های HuggingFace/Whisper

## نصب وابستگی‌ها

```powershell
cd E:\AI\LLMOps_test\offline-ai-ollama-main
pip install -r requirements.txt
# برای STT روی GPU:
pip install torch --index-url https://download.pytorch.org/whl/cu126
```

بستهٔ مهم در `requirements.txt`:

`streamlit`, `ollama`, `python-dotenv`, `psutil`, `pypdf`, `faster-whisper`, `openai-whisper`, `torch`, `sounddevice`, `edge-tts`, `pyttsx3`, `imageio-ffmpeg`, …

## فایل `.env`

از `.env.example` کپی کنید:

```env
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=gemma4:e4b-it-qat
```

## Streamlit

فایل `.streamlit/config.toml`:

- تم تیره (`base = "dark"`)
- `gatherUsageStats = false`
- `toolbarMode = "viewer"`

## اجرا

```powershell
streamlit run .\streamlit_app.py
```

یا headless:

```powershell
streamlit run .\streamlit_app.py --server.headless true
```

## قانون Cursor پروژه

فایل `.cursor/rules/persian-rtl.mdc`: توضیحات فارسی کاربرمحور باید RTL باشند (`dir="rtl"`).

## داده‌های محلی

- دیتابیس تاریخچه: `data/chat_history.db`
- نمونه‌های متن: `data/docs/sample-fa.txt`, `sample-en.txt`
- پوشه‌های `temp/` معمولاً برای خروجی موقت‌اند و نباید به git وابسته باشند

## عیب‌یابی سریع

| علامت | اقدام |
|--------|--------|
| خطای اتصال Ollama | سرویس را دستی استارت کنید؛ پورت `11434` |
| Whisper نصب نیست | `pip install faster-whisper` و در صورت نیاز `torch` CUDA |
| CUDA کار نمی‌کند | نسخهٔ `+cu126` نصب باشد؛ `torch.cuda.is_available()` |
| میکروفون سیستم سکوت | Volume/Unmute ویندوز؛ یا ضبط مرورگر |
| دکمهٔ دیالوگ سفید/نامرئی | CSS دیالوگ در `chatbot_constants.STREAMLIT_STYLE` |

</div>
