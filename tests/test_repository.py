import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from compliment_bot.repository import Repository  # noqa: E402


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repository(":memory:")

    def tearDown(self):
        self.repo.close()

    def test_new_user_gets_default_style(self):
        user = self.repo.get_or_create_user(100, "Аня")
        self.assertEqual((user.tg_id, user.first_name, user.style), (100, "Аня", "warm"))

    def test_get_or_create_does_not_duplicate(self):
        first = self.repo.get_or_create_user(100, "Аня")
        second = self.repo.get_or_create_user(100, "Аня")
        self.assertEqual(first.id, second.id)

    def test_set_style_persists(self):
        self.repo.get_or_create_user(100)
        self.repo.set_style(100, "funny")
        self.assertEqual(self.repo.get_user(100).style, "funny")

    def test_set_style_rejects_unknown_style(self):
        self.repo.get_or_create_user(100)
        with self.assertRaises(ValueError):
            self.repo.set_style(100, "angry")

    def test_list_compliments_by_style(self):
        self.repo.add_compliment("warm", "Ты молодец", "молодец, успех")
        self.repo.add_compliment("funny", "Ты огонь", "")
        warm = self.repo.list_compliments("warm")
        self.assertEqual([c.text for c in warm], ["Ты молодец"])
        self.assertEqual(warm[0].keywords, ("молодец", "успех"))

    def test_disabled_compliment_is_not_listed(self):
        cid = self.repo.add_compliment("warm", "Ты молодец")
        self.assertTrue(self.repo.set_compliment_active(cid, False))
        self.assertEqual(self.repo.list_compliments("warm"), [])
        self.assertEqual(len(self.repo.list_compliments("warm", only_active=False)), 1)

    def test_disable_unknown_compliment_returns_false(self):
        self.assertFalse(self.repo.set_compliment_active(999, False))

    def test_empty_text_is_rejected(self):
        with self.assertRaises(ValueError):
            self.repo.add_compliment("warm", "   ")

    def test_last_compliment_is_saved(self):
        self.repo.get_or_create_user(100)
        cid = self.repo.add_compliment("warm", "Ты молодец")
        self.repo.set_last_compliment(100, cid)
        self.assertEqual(self.repo.get_user(100).last_compliment_id, cid)

    def test_tables_are_created_in_new_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "nested", "bot.sqlite3")
            repo = Repository(path)
            repo.get_or_create_user(1)
            repo.close()
            self.assertTrue(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
