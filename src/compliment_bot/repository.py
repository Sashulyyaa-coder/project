"""Слой доступа к данным (Repository): весь SQL бота находится только здесь."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

STYLES = ("warm", "funny", "grandma")
DEFAULT_STYLE = "warm"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id              INTEGER NOT NULL UNIQUE,
    first_name         TEXT    NOT NULL DEFAULT '',
    style              TEXT    NOT NULL DEFAULT 'warm'
                       CHECK (style IN ('warm', 'funny', 'grandma')),
    last_compliment_id INTEGER,
    created_at         TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS compliments (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    style     TEXT    NOT NULL CHECK (style IN ('warm', 'funny', 'grandma')),
    text      TEXT    NOT NULL CHECK (length(trim(text)) > 0),
    keywords  TEXT    NOT NULL DEFAULT '',
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_compliments_style ON compliments (style, is_active);
"""


@dataclass(frozen=True)
class User:
    id: int
    tg_id: int
    first_name: str
    style: str
    last_compliment_id: int | None


@dataclass(frozen=True)
class Compliment:
    id: int
    style: str
    text: str
    keywords: tuple[str, ...]
    is_active: bool


def _split_keywords(raw: str) -> tuple[str, ...]:
    return tuple(word.strip().lower() for word in raw.split(",") if word.strip())


def _to_user(row: sqlite3.Row) -> User:
    return User(row["id"], row["tg_id"], row["first_name"], row["style"], row["last_compliment_id"])


def _to_compliment(row: sqlite3.Row) -> Compliment:
    return Compliment(row["id"], row["style"], row["text"], _split_keywords(row["keywords"]),
                      bool(row["is_active"]))


class Repository:
    """Работа с SQLite. Таблицы создаются автоматически при первом открытии."""

    def __init__(self, path: str | Path = "data/bot.sqlite3") -> None:
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)

    def close(self) -> None:
        self._conn.close()

    # ---- пользователи -------------------------------------------------
    def get_user(self, tg_id: int) -> User | None:
        row = self._conn.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,)).fetchone()
        return _to_user(row) if row else None

    def get_or_create_user(self, tg_id: int, first_name: str = "") -> User:
        """Возвращает пользователя, при первом обращении создаёт со стилем по умолчанию."""
        with self._conn:
            self._conn.execute(
                "INSERT OR IGNORE INTO users (tg_id, first_name, style) VALUES (?, ?, ?)",
                (tg_id, first_name, DEFAULT_STYLE),
            )
        user = self.get_user(tg_id)
        assert user is not None
        return user

    def set_style(self, tg_id: int, style: str) -> None:
        if style not in STYLES:
            raise ValueError(f"Неизвестный стиль: {style}")
        with self._conn:
            self._conn.execute("UPDATE users SET style = ? WHERE tg_id = ?", (style, tg_id))

    def set_last_compliment(self, tg_id: int, compliment_id: int) -> None:
        with self._conn:
            self._conn.execute("UPDATE users SET last_compliment_id = ? WHERE tg_id = ?",
                               (compliment_id, tg_id))

    # ---- шаблоны комплиментов -------------------------------------------
    def add_compliment(self, style: str, text: str, keywords: str = "") -> int:
        if style not in STYLES:
            raise ValueError(f"Неизвестный стиль: {style}")
        if not text.strip():
            raise ValueError("Текст комплимента не может быть пустым")
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO compliments (style, text, keywords) VALUES (?, ?, ?)",
                (style, text.strip(), keywords),
            )
        return int(cur.lastrowid)

    def list_compliments(self, style: str | None = None, only_active: bool = True) -> list[Compliment]:
        """Шаблоны выбранного стиля (или всех стилей, если style не указан)."""
        query = "SELECT * FROM compliments WHERE 1 = 1"
        params: list[object] = []
        if style is not None:
            query += " AND style = ?"
            params.append(style)
        if only_active:
            query += " AND is_active = 1"
        query += " ORDER BY id"
        return [_to_compliment(r) for r in self._conn.execute(query, params).fetchall()]

    def get_compliment(self, compliment_id: int) -> Compliment | None:
        row = self._conn.execute("SELECT * FROM compliments WHERE id = ?", (compliment_id,)).fetchone()
        return _to_compliment(row) if row else None

    def set_compliment_active(self, compliment_id: int, active: bool) -> bool:
        """Включает или отключает шаблон. Возвращает False, если шаблона нет."""
        with self._conn:
            cur = self._conn.execute("UPDATE compliments SET is_active = ? WHERE id = ?",
                                     (1 if active else 0, compliment_id))
        return cur.rowcount > 0
