"""
Chat history persistence with SQLite.
"""

from __future__ import annotations

import json
import sqlite3

from pathlib import Path
from typing import (
    Final,
    Optional,
)
from datetime import datetime

import dt_utility as utility

VERSION: Final[str] = "1.0.0"

ROOT_DIR: Final[Path] = Path(__file__).resolve().parent
DATA_DIR: Final[Path] = ROOT_DIR / "data"
DB_PATH: Final[Path] = DATA_DIR / "chat_history.db"

ROLE_SYSTEM: Final[str] = "system"
ROLE_USER: Final[str] = "user"
ROLE_ASSISTANT: Final[str] = "assistant"


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database=str(DB_PATH))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    """Create history tables if needed."""

    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                model_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                    ON DELETE CASCADE
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def create_conversation(
    model_name: str,
    title: str = "گفتگوی جدید",
) -> int:
    """Create a new conversation and return its id."""

    init_db()
    now = _now()
    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO conversations (title, model_name, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (title, model_name, now, now),
        )
        connection.commit()
        conversation_id = int(cursor.lastrowid)
        return conversation_id
    finally:
        connection.close()


def list_conversations(limit: int = 50) -> list[dict]:
    """Return recent conversations, newest first."""

    init_db()
    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT id, title, model_name, created_at, updated_at
            FROM conversations
            ORDER BY datetime(updated_at) DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def get_conversation(conversation_id: int) -> Optional[dict]:
    """Return one conversation row."""

    init_db()
    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT id, title, model_name, created_at, updated_at
            FROM conversations
            WHERE id = ?
            """,
            (conversation_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        connection.close()


def get_messages(conversation_id: int) -> list[dict]:
    """Return messages for a conversation as role/content dicts."""

    init_db()
    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (conversation_id,),
        )
        rows = cursor.fetchall()
        return [{"role": row["role"], "content": row["content"]} for row in rows]
    finally:
        connection.close()


def save_messages(
    conversation_id: int,
    messages: list[dict],
    model_name: Optional[str] = None,
    title_hint: Optional[str] = None,
) -> str:
    """
    Replace all messages of a conversation with the given list.
    Also update title from hint or first user message when possible.

    Returns:
        final conversation title
    """

    init_db()
    now = _now()
    connection = _connect()
    try:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM messages WHERE conversation_id = ?",
            (conversation_id,),
        )

        saved_count = 0
        for message in messages:
            role = str(message.get("role", "")).strip().lower()
            content = str(message.get("content", ""))
            if role not in {ROLE_SYSTEM, ROLE_USER, ROLE_ASSISTANT}:
                continue
            cursor.execute(
                """
                INSERT INTO messages (conversation_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (conversation_id, role, content, now),
            )
            saved_count += 1

        title = _build_title_from_messages(
            messages=messages,
            title_hint=title_hint,
        )
        if model_name:
            cursor.execute(
                """
                UPDATE conversations
                SET title = ?, model_name = ?, updated_at = ?
                WHERE id = ?
                """,
                (title, model_name, now, conversation_id),
            )
        else:
            cursor.execute(
                """
                UPDATE conversations
                SET title = ?, updated_at = ?
                WHERE id = ?
                """,
                (title, now, conversation_id),
            )

        connection.commit()
        if saved_count == 0:
            raise RuntimeError("هیچ پیامی برای ذخیره در تاریخچه باقی نماند.")
        return title
    finally:
        connection.close()


def _truncate_title(text: str, max_len: int = 40) -> str:
    text = utility.fix_text(text=text)
    if not text:
        return "گفتگوی جدید"
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


def _build_title_from_messages(
    messages: list[dict],
    title_hint: Optional[str] = None,
) -> str:
    if title_hint:
        return _truncate_title(text=title_hint)

    for message in messages:
        if str(message.get("role", "")).lower() != ROLE_USER:
            continue
        text = utility.fix_text(text=str(message.get("content", "")))
        if not text:
            continue
        if text.startswith("📎"):
            return _truncate_title(text=text)
        if text.startswith("نتیجه تحلیل فایل"):
            return _truncate_title(text=text)
        if text.startswith("🎤"):
            return _truncate_title(text=text)
        return _truncate_title(text=text)
    return "گفتگوی جدید"


def delete_conversation(conversation_id: int) -> None:
    """Delete one conversation and its messages."""

    init_db()
    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM messages WHERE conversation_id = ?",
            (conversation_id,),
        )
        cursor.execute(
            "DELETE FROM conversations WHERE id = ?",
            (conversation_id,),
        )
        connection.commit()
    finally:
        connection.close()


def delete_all_conversations() -> None:
    """Delete all conversations and messages."""

    init_db()
    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM messages")
        cursor.execute("DELETE FROM conversations")
        connection.commit()
    finally:
        connection.close()


def export_conversation_json(conversation_id: int) -> str:
    """Export one conversation as JSON string."""

    conversation = get_conversation(conversation_id=conversation_id)
    messages = get_messages(conversation_id=conversation_id)
    payload = {
        "conversation": conversation,
        "messages": messages,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    utility.display_just_one_error_message(
        message=utility.ERROR_MESSAGE_MODULE_IS_NOT_EXECUTED_DIRECTLY,
    )
