import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aiogram import Dispatcher  # noqa: E402

from compliment_bot import main as bot_main  # noqa: E402
from compliment_bot.config import ConfigError  # noqa: E402


class MainTests(unittest.TestCase):
    def test_returns_1_when_settings_are_invalid(self):
        with mock.patch.object(bot_main, "load_settings", side_effect=ConfigError("нет токена")):
            self.assertEqual(bot_main.main(), 1)

    def test_returns_1_when_token_has_wrong_format(self):
        with mock.patch.dict(os.environ, {"BOT_TOKEN": "not-a-token"}):
            with mock.patch.object(bot_main, "load_settings") as load:
                from compliment_bot.config import Settings
                load.return_value = Settings(bot_token="not-a-token")
                self.assertEqual(bot_main.main(), 1)

    def test_create_dispatcher(self):
        self.assertIsInstance(bot_main.create_dispatcher(), Dispatcher)


if __name__ == "__main__":
    unittest.main()
