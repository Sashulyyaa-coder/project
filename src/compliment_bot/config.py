from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

from dotenv import load_dotenv


class ConfigError(Exception):


@dataclass(frozen=True)
class Settings:
    bot_token: str = field(repr=False)
    admin_ids: frozenset[int] = frozenset()


def _parse_admin_ids(raw: str) -> frozenset[int]:
    ids: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.add(int(part))
        except ValueError:
            raise ConfigError(
                f"ADMIN_IDS: значение «{part}» не является числом. "
                "Ожидается список Telegram ID через запятую, например: 123456789,987654321"
            ) from None
    return frozenset(ids)


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    if env is None:
        load_dotenv()
        env = os.environ

    token = env.get("BOT_TOKEN", "").strip()
    if not token:
        raise ConfigError(
            "Не задан BOT_TOKEN. Создайте файл .env по образцу .env.example "
            "и укажите токен, полученный у @BotFather."
        )

    return Settings(
        bot_token=token,
        admin_ids=_parse_admin_ids(env.get("ADMIN_IDS", "")),
    )


if __name__ == "__main__":
    try:
        settings = load_settings()
    except ConfigError as error:
        raise SystemExit(f"Ошибка настроек: {error}")
    print(
        f"Настройки загружены. Токен задан (длина {len(settings.bot_token)}), "
        f"администраторов: {len(settings.admin_ids)}"
    )
