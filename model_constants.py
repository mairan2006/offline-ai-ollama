"""
Offline model catalog and size/RAM estimates.
"""

from typing import Final

VERSION: Final[str] = "2.0.0"

# Catalog of recommended offline Ollama models.
# download_bytes ~= approximate download/disk size
# approx_ram_bytes ~= conservative RAM needed while running
MODEL_CATALOG: Final[dict[str, dict]] = {
    # ---- خیلی سبک ----
    "llama3.2:1b": {
        "title": "Llama 3.2 1B",
        "category": "خیلی سبک",
        "download_bytes": 1_300_000_000,
        "approx_ram_bytes": 2_000_000_000,
        "description": (
            "مدل بسیار سبک و سریع Meta. برای سیستم‌های ضعیف، تست سریع، "
            "و پاسخ‌های کوتاه مناسب است. کیفیت فارسی متوسط."
        ),
    },
    "qwen2.5:0.5b": {
        "title": "Qwen 2.5 0.5B",
        "category": "خیلی سبک",
        "download_bytes": 400_000_000,
        "approx_ram_bytes": 1_200_000_000,
        "description": (
            "فوق‌العاده سبک از Alibaba. مناسب آزمایش سریع و دستگاه‌های کم‌رم. "
            "برای کارهای پیچیده توصیه نمی‌شود."
        ),
    },
    "qwen2.5:1.5b": {
        "title": "Qwen 2.5 1.5B",
        "category": "خیلی سبک",
        "download_bytes": 1_000_000_000,
        "approx_ram_bytes": 2_200_000_000,
        "description": (
            "سبک و نسبتاً خوب برای چت ساده و کارهای روزمره. "
            "چندزبانه است و برای شروع گزینه مناسبی است."
        ),
    },
    "smollm2:1.7b": {
        "title": "SmolLM2 1.7B",
        "category": "خیلی سبک",
        "download_bytes": 1_100_000_000,
        "approx_ram_bytes": 2_300_000_000,
        "description": (
            "مدل کوچک Hugging Face. سرعت بالا برای چت سبک و آزمایش قابلیت‌ها."
        ),
    },
    "tinydolphin": {
        "title": "TinyDolphin",
        "category": "خیلی سبک",
        "download_bytes": 650_000_000,
        "approx_ram_bytes": 1_500_000_000,
        "description": (
            "مدل خیلی کوچک و سریع برای تست اولیه محیط Ollama."
        ),
    },
    # ---- سبک / متعادل ----
    "llama3.2:3b": {
        "title": "Llama 3.2 3B",
        "category": "سبک",
        "download_bytes": 2_000_000_000,
        "approx_ram_bytes": 3_500_000_000,
        "description": (
            "تعادل خوب بین سرعت و کیفیت. برای چت عمومی، خلاصه‌سازی کوتاه "
            "و کارهای روزمره مناسب است."
        ),
    },
    "gemma3:1b": {
        "title": "Gemma 3 1B",
        "category": "سبک",
        "download_bytes": 800_000_000,
        "approx_ram_bytes": 2_000_000_000,
        "description": (
            "نسخه سبک Gemma 3 از Google. سریع و کم‌حجم؛ برای سیستم‌های محدود."
        ),
    },
    "gemma3:4b": {
        "title": "Gemma 3 4B",
        "category": "متعادل",
        "download_bytes": 3_300_000_000,
        "approx_ram_bytes": 4_500_000_000,
        "description": (
            "پیش‌فرض پیشنهادی این پروژه. کیفیت خوب برای فارسی، چت عمومی، "
            "و استفاده‌های روزمره. نسبت به حجمش عملکرد قابل قبولی دارد."
        ),
    },
    "qwen2.5:3b": {
        "title": "Qwen 2.5 3B",
        "category": "سبک",
        "download_bytes": 1_900_000_000,
        "approx_ram_bytes": 3_500_000_000,
        "description": (
            "مدل چندزبانه سبک. برای چت، ترجمه ساده و کارهای عمومی مناسب است."
        ),
    },
    "phi3:mini": {
        "title": "Phi-3 Mini",
        "category": "سبک",
        "download_bytes": 2_200_000_000,
        "approx_ram_bytes": 3_800_000_000,
        "description": (
            "مدل کوچک مایکروسافت با تمرکز روی استدلال. برای کدنویسی سبک و "
            "پرسش‌های تحلیلی کوتاه خوب است."
        ),
    },
    "phi4-mini": {
        "title": "Phi-4 Mini",
        "category": "متعادل",
        "download_bytes": 2_500_000_000,
        "approx_ram_bytes": 4_000_000_000,
        "description": (
            "نسل جدیدتر Phi. کیفیت بهتر نسبت به Phi-3 در بسیاری از کارها."
        ),
    },
    "mistral:7b": {
        "title": "Mistral 7B",
        "category": "متوسط",
        "download_bytes": 4_100_000_000,
        "approx_ram_bytes": 7_000_000_000,
        "description": (
            "مدل محبوب و قوی برای چت و تولید متن. رم بیشتری نسبت به مدل‌های "
            "۳-۴B نیاز دارد."
        ),
    },
    "llama3.1:8b": {
        "title": "Llama 3.1 8B",
        "category": "متوسط",
        "download_bytes": 4_700_000_000,
        "approx_ram_bytes": 8_000_000_000,
        "description": (
            "کیفیت بالاتر برای گفتگو، خلاصه و کمک برنامه‌نویسی. "
            "حداقل حدود ۸ گیگابایت رم آزاد توصیه می‌شود."
        ),
    },
    "qwen2.5:7b": {
        "title": "Qwen 2.5 7B",
        "category": "متوسط",
        "download_bytes": 4_700_000_000,
        "approx_ram_bytes": 7_500_000_000,
        "description": (
            "چندزبانه و قوی‌تر از نسخه ۳B. گزینه خوب اگر رم کافی دارید."
        ),
    },
    "gemma3:12b": {
        "title": "Gemma 3 12B",
        "category": "سنگین",
        "download_bytes": 8_100_000_000,
        "approx_ram_bytes": 12_000_000_000,
        "description": (
            "کیفیت بالاتر Gemma 3. برای سیستم‌های قوی‌تر؛ رم و فضای دیسک بیشتری "
            "لازم دارد."
        ),
    },
    "deepseek-r1:1.5b": {
        "title": "DeepSeek R1 1.5B",
        "category": "استدلال / سبک",
        "download_bytes": 1_100_000_000,
        "approx_ram_bytes": 2_500_000_000,
        "description": (
            "مدل استدلال سبک. برای فکر کردن مرحله‌به‌مرحله روی مسائل ساده مفید است."
        ),
    },
    "deepseek-r1:7b": {
        "title": "DeepSeek R1 7B",
        "category": "استدلال / متوسط",
        "download_bytes": 4_700_000_000,
        "approx_ram_bytes": 8_000_000_000,
        "description": (
            "نسخه قوی‌تر استدلال DeepSeek. برای مسائل تحلیلی بهتر است ولی سنگین‌تر است."
        ),
    },
    "deepseek-coder:1.3b": {
        "title": "DeepSeek Coder 1.3B",
        "category": "کدنویسی / سبک",
        "download_bytes": 800_000_000,
        "approx_ram_bytes": 2_000_000_000,
        "description": (
            "مخصوص برنامه‌نویسی و سبک. برای تکمیل کد کوتاه و توضیح تکه کدها."
        ),
    },
    "deepseek-coder:6.7b": {
        "title": "DeepSeek Coder 6.7B",
        "category": "کدنویسی / متوسط",
        "download_bytes": 3_800_000_000,
        "approx_ram_bytes": 7_000_000_000,
        "description": (
            "مدل کدنویسی قوی‌تر. اگر کار اصلی‌ات برنامه‌نویسی است گزینه خوبی است."
        ),
    },
    "codellama:7b": {
        "title": "Code Llama 7B",
        "category": "کدنویسی / متوسط",
        "download_bytes": 3_800_000_000,
        "approx_ram_bytes": 7_000_000_000,
        "description": (
            "مدل کدنویسی Meta. مناسب توضیح کد، بازنویسی و کمک در پروژه‌های متوسط."
        ),
    },
    "llava:7b": {
        "title": "LLaVA 7B",
        "category": "تصویر / متوسط",
        "download_bytes": 4_500_000_000,
        "approx_ram_bytes": 8_000_000_000,
        "description": (
            "مدل بینایی-زبانی برای توضیح عکس. در فاز فایل/تصویر مفید خواهد بود."
        ),
    },
    "moondream": {
        "title": "Moondream",
        "category": "تصویر / سبک",
        "download_bytes": 1_700_000_000,
        "approx_ram_bytes": 3_500_000_000,
        "description": (
            "مدل بینایی سبک برای توضیح تصاویر با مصرف کمتر نسبت به LLaVA."
        ),
    },
    "nomic-embed-text": {
        "title": "Nomic Embed Text",
        "category": "امبدینگ",
        "download_bytes": 270_000_000,
        "approx_ram_bytes": 800_000_000,
        "description": (
            "مدل امبدینگ برای جستجو در اسناد (RAG). برای چت معمولی استفاده نمی‌شود."
        ),
    },
    "mxbai-embed-large": {
        "title": "MxBai Embed Large",
        "category": "امبدینگ",
        "download_bytes": 670_000_000,
        "approx_ram_bytes": 1_500_000_000,
        "description": (
            "امبدینگ با کیفیت بالاتر برای جستجوی معنایی در متن‌ها و اسناد."
        ),
    },
}

# Preferred free RAM kept for Windows/system stability.
RAM_SAFETY_MARGIN_BYTES: Final[int] = 2_000_000_000

# Absolute minimum free RAM after model estimate (used only after cleanup).
RAM_ABSOLUTE_MIN_FREE_BYTES: Final[int] = 750_000_000

# Fallback estimate when model is unknown.
DEFAULT_MODEL_RAM_BYTES: Final[int] = 4_000_000_000
DEFAULT_MODEL_DOWNLOAD_BYTES: Final[int] = 2_000_000_000

CATALOG_MODEL_NAMES: Final[list[str]] = list(MODEL_CATALOG.keys())
