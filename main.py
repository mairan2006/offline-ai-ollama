"""CLI for offline chat and document Q&A via Ollama."""

from __future__ import annotations

import argparse
import sys

import config
from app.ollama_client import build_messages, chat_stream, ensure_running, health
from app.rag import build_index, format_context, retrieve


def cmd_status(_: argparse.Namespace) -> int:
    info = health()
    print(f"Host:  {info['host']}")
    print(f"Chat:  {info['chat_model']}  ({'ok' if info['chat_ready'] else 'missing'})")
    print(f"Embed: {info['embed_model']}")
    print("Models:")
    for name in info["models"] or ["(none)"]:
        print(f"  - {name}")
    return 0


def cmd_chat(args: argparse.Namespace) -> int:
    ensure_running()
    history: list[dict[str, str]] = []
    print(f"Offline chat · model={args.model or config.OLLAMA_MODEL}")
    print("Type /exit to quit, /clear to reset history.\n")

    while True:
        try:
            user_text = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if not user_text:
            continue
        if user_text in {"/exit", "/quit", "exit", "quit"}:
            return 0
        if user_text == "/clear":
            history.clear()
            print("History cleared.\n")
            continue

        context = None
        if args.rag:
            hits = retrieve(user_text, top_k=args.top_k)
            context = format_context(hits)

        messages = build_messages(history, user_text, context=context)
        print("AI> ", end="", flush=True)
        answer_parts: list[str] = []
        for token in chat_stream(messages, model=args.model):
            print(token, end="", flush=True)
            answer_parts.append(token)
        print("\n")
        answer = "".join(answer_parts)
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": answer})
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    ensure_running()
    context = None
    if args.rag:
        hits = retrieve(args.question, top_k=args.top_k)
        context = format_context(hits)
        if args.show_context:
            print("--- context ---")
            print(context)
            print("---------------")
    messages = build_messages([], args.question, context=context)
    for token in chat_stream(messages, model=args.model):
        print(token, end="", flush=True)
    print()
    return 0


def cmd_index(_: argparse.Namespace) -> int:
    ensure_running()
    count = build_index()
    print(f"Indexed {count} chunks -> {config.INDEX_PATH}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Offline AI with Ollama + Python",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=f"Chat model (default: {config.OLLAMA_MODEL})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Check Ollama and local models")
    p_status.set_defaults(func=cmd_status)

    p_chat = sub.add_parser("chat", help="Interactive streaming chat")
    p_chat.add_argument("--rag", action="store_true", help="Answer using local docs")
    p_chat.add_argument("--top-k", type=int, default=config.TOP_K)
    p_chat.set_defaults(func=cmd_chat)

    p_ask = sub.add_parser("ask", help="One-shot question")
    p_ask.add_argument("question")
    p_ask.add_argument("--rag", action="store_true")
    p_ask.add_argument("--show-context", action="store_true")
    p_ask.add_argument("--top-k", type=int, default=config.TOP_K)
    p_ask.set_defaults(func=cmd_ask)

    p_index = sub.add_parser("index", help="Build RAG index from data/docs")
    p_index.set_defaults(func=cmd_index)
    return parser


def _configure_stdio() -> None:
    """Avoid Windows cp1252 crashes on Persian / Unicode output."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
