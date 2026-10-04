"""Project configuration loaded from environment / .env."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are a helpful offline AI assistant. Answer clearly and concisely.",
)
DOCS_DIR = ROOT / "data" / "docs"
INDEX_PATH = ROOT / "data" / "index.npz"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
TOP_K = 4
