"""Точка входа: запуск Telegram-бота."""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramNetworkError,
    TelegramUnauthorizedError,
)
from aiogram.utils.token import TokenValidationError

from .config import ConfigError, Settings, load_settings

logger = logging.getLogger("compliment_bot")


def setup_logging(level: int = logging.INFO) -> None:
    """Настраивает формат логов: время, уровень, источник, сообщение."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def create_dispatcher() -> Dispatcher:
    """Создаёт диспетчер. Сюда будут подключаться роутеры с обработчиками команд."""
    return Dispatcher()


async def run(settings: Settings) -> None:
    """Запускает опрос Telegram (long polling) и работает до остановки."""
    bot = Bot(token=settings.bot_token)
    dispatcher = create_dispatcher()
    try:
        me = await bot.get_me()
        logger.info("Бот запущен: @%s", me.username)
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


def main() -> int:
    """Читает настройки и запускает бота. Возвращает код выхода процесса."""
    setup_logging()
    try:
        settings = load_settings()
    except ConfigError as error:
        logger.error("Ошибка настроек: %s", error)
        return 1

    try:
        asyncio.run(run(settings))
    except TokenValidationError:
        logger.error("Токен имеет неверный формат. Проверьте BOT_TOKEN в файле .env.")
        return 1
    except TelegramUnauthorizedError:
        logger.error("Telegram не принял токен. Проверьте BOT_TOKEN в файле .env.")
        return 1
    except TelegramNetworkError as error:
        logger.error("Нет связи с Telegram: %s", error)
        return 1
    except TelegramAPIError as error:
        logger.error("Telegram отклонил запрос: %s", error)
        return 1
    except KeyboardInterrupt:
        pass
    return 0
