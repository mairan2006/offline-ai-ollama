"""Thin wrapper around the Ollama Python client."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import ollama

import config


def client() -> ollama.Client:
    return ollama.Client(host=config.OLLAMA_HOST)


def ensure_running() -> None:
    """Raise a clear error if the local Ollama server is unreachable."""
    try:
        client().list()
    except Exception as exc:  # noqa: BLE001 - surface any connection failure
        raise RuntimeError(
            "Cannot reach Ollama. Start it with `ollama serve` "
            f"(host={config.OLLAMA_HOST})."
        ) from exc


def list_models() -> list[str]:
    response = client().list()
    models = getattr(response, "models", None) or response.get("models", [])
    names: list[str] = []
    for model in models:
        name = getattr(model, "model", None) or getattr(model, "name", None)
        if name is None and isinstance(model, dict):
            name = model.get("model") or model.get("name")
        if name:
            names.append(str(name))
    return names


def chat_stream(
    messages: list[dict[str, str]],
    *,
    model: str | None = None,
) -> Iterator[str]:
    stream = client().chat(
        model=model or config.OLLAMA_MODEL,
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        message = getattr(chunk, "message", None)
        if message is None and isinstance(chunk, dict):
            message = chunk.get("message", {})
        content = getattr(message, "content", None)
        if content is None and isinstance(message, dict):
            content = message.get("content", "")
        if content:
            yield content


def chat_once(
    messages: list[dict[str, str]],
    *,
    model: str | None = None,
) -> str:
    response = client().chat(
        model=model or config.OLLAMA_MODEL,
        messages=messages,
        stream=False,
    )
    message = getattr(response, "message", None)
    if message is None and isinstance(response, dict):
        message = response.get("message", {})
    content = getattr(message, "content", None)
    if content is None and isinstance(message, dict):
        content = message.get("content", "")
    return str(content or "")


def embed(texts: list[str], *, model: str | None = None) -> list[list[float]]:
    embed_model = model or config.OLLAMA_EMBED_MODEL
    vectors: list[list[float]] = []
    for text in texts:
        response = client().embeddings(model=embed_model, prompt=text)
        embedding = getattr(response, "embedding", None)
        if embedding is None and isinstance(response, dict):
            embedding = response.get("embedding")
        if not embedding:
            raise RuntimeError(f"Empty embedding from model {embed_model}")
        vectors.append(list(embedding))
    return vectors


def build_messages(
    history: list[dict[str, str]],
    user_text: str,
    *,
    system: str | None = None,
    context: str | None = None,
) -> list[dict[str, str]]:
    system_prompt = system or config.SYSTEM_PROMPT
    if context:
        system_prompt = (
            f"{system_prompt}\n\nUse the following context when relevant. "
            "If the answer is not in the context, say so.\n\n"
            f"Context:\n{context}"
        )
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})
    return messages


def health() -> dict[str, Any]:
    ensure_running()
    models = list_models()
    return {
        "host": config.OLLAMA_HOST,
        "chat_model": config.OLLAMA_MODEL,
        "embed_model": config.OLLAMA_EMBED_MODEL,
        "models": models,
        "chat_ready": any(
            config.OLLAMA_MODEL == m or m.startswith(f"{config.OLLAMA_MODEL}:")
            or config.OLLAMA_MODEL.startswith(m.split(":")[0])
            for m in models
        )
        or config.OLLAMA_MODEL in models,
    }
