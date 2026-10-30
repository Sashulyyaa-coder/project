# Исходный код бота

## Структура

```
src/
└── compliment_bot/      # пакет бота
    ├── __init__.py
    └── config.py        # загрузка настроек (BOT_TOKEN, ADMIN_IDS) из .env
```

Планируемые модули (см. [Architecture](https://github.com/Sashulyyaa-coder/project/wiki/Architecture)): обработчики команд, сервис подбора комплиментов, слой доступа к данным (Repository), планировщик.

## Настройка

1. Требуется Python 3.11 или новее.
2. Установите зависимости из корня репозитория:
   ```
   python3 -m pip install -r requirements.txt
   ```
3. Скопируйте `.env.example` в `.env` и заполните `BOT_TOKEN` (токен от @BotFather) и при необходимости `ADMIN_IDS`.

## Проверка настроек

Из корня репозитория:

```
PYTHONPATH=src python3 -m compliment_bot.config
```

Если настройки в порядке, будет выведено «Настройки загружены». Если `BOT_TOKEN` не задан или `ADMIN_IDS` содержит не числа, будет понятное сообщение об ошибке.
