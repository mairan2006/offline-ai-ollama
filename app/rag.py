"""Lightweight local RAG over text files using Ollama embeddings."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

import config
from app.ollama_client import embed


@dataclass
class Chunk:
    source: str
    text: str


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_documents(docs_dir: Path | None = None) -> list[tuple[str, str]]:
    root = docs_dir or config.DOCS_DIR
    root.mkdir(parents=True, exist_ok=True)
    docs: list[tuple[str, str]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".txt", ".md", ".markdown"}:
            docs.append((path.name, _read_text_file(path)))
    return docs


def chunk_text(
    text: str,
    *,
    chunk_size: int = config.CHUNK_SIZE,
    overlap: int = config.CHUNK_OVERLAP,
) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def build_chunks(docs_dir: Path | None = None) -> list[Chunk]:
    chunks: list[Chunk] = []
    for source, text in load_documents(docs_dir):
        for part in chunk_text(text):
            chunks.append(Chunk(source=source, text=part))
    return chunks


def _cosine_sim(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    query_norm = query / (np.linalg.norm(query) + 1e-12)
    matrix_norm = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-12)
    return matrix_norm @ query_norm


def build_index(docs_dir: Path | None = None, index_path: Path | None = None) -> int:
    chunks = build_chunks(docs_dir)
    if not chunks:
        raise RuntimeError(
            f"No .txt/.md documents found in {(docs_dir or config.DOCS_DIR)}"
        )
    vectors = embed([c.text for c in chunks])
    path = index_path or config.INDEX_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        embeddings=np.asarray(vectors, dtype=np.float32),
        sources=np.asarray([c.source for c in chunks], dtype=object),
        texts=np.asarray([c.text for c in chunks], dtype=object),
    )
    return len(chunks)


def load_index(index_path: Path | None = None) -> tuple[np.ndarray, list[Chunk]]:
    path = index_path or config.INDEX_PATH
    if not path.exists():
        raise RuntimeError(
            "Index not found. Run: python main.py index"
        )
    data = np.load(path, allow_pickle=True)
    embeddings = data["embeddings"]
    sources = data["sources"].tolist()
    texts = data["texts"].tolist()
    chunks = [Chunk(source=s, text=t) for s, t in zip(sources, texts, strict=True)]
    return embeddings, chunks


def retrieve(query: str, *, top_k: int = config.TOP_K) -> list[tuple[Chunk, float]]:
    embeddings, chunks = load_index()
    query_vec = np.asarray(embed([query])[0], dtype=np.float32)
    scores = _cosine_sim(query_vec, embeddings)
    order = np.argsort(scores)[::-1][:top_k]
    return [(chunks[i], float(scores[i])) for i in order]


def format_context(hits: list[tuple[Chunk, float]]) -> str:
    blocks: list[str] = []
    for i, (chunk, score) in enumerate(hits, start=1):
        blocks.append(
            f"[{i}] source={chunk.source} score={score:.3f}\n{chunk.text}"
        )
    return "\n\n".join(blocks)
