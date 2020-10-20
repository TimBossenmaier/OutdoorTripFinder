import unittest
from app.entities.user import User


class UserModelTestCase(unittest.TestCase):

    def test_password_setter(self):
        u = User("testUser", "user@test.com", "cat", 1, "Admin")
        self.assertTrue(u.password_hash is not None)

    def test_password_verification(self):
        u = User("testUser", "user@test.com", "cat", 1, "Admin")
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User("testUser", "user@test.com", "cat", 1, "Admin")
        u2 = User("testUser", "user@test.com", "dog", 1, "Admin")
        self.assertTrue(u.password_hash != u2.password_hash)
