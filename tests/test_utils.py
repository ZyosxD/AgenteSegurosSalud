import unittest
import string
import sys
from unittest.mock import MagicMock

# Mock selenium before importing src.utils
sys.modules['selenium'] = MagicMock()
sys.modules['selenium.webdriver'] = MagicMock()
sys.modules['selenium.webdriver.common'] = MagicMock()
sys.modules['selenium.webdriver.common.by'] = MagicMock()

from src.utils import generate_strong_password

class TestUtils(unittest.TestCase):
    def test_generate_strong_password_default_length(self):
        password = generate_strong_password()
        self.assertEqual(len(password), 12)

    def test_generate_strong_password_custom_length(self):
        for length in [8, 15, 20]:
            password = generate_strong_password(length)
            self.assertEqual(len(password), length)

    def test_generate_strong_password_clamping(self):
        self.assertEqual(len(generate_strong_password(5)), 8)
        self.assertEqual(len(generate_strong_password(25)), 20)

    def test_generate_strong_password_complexity(self):
        # Run multiple times to ensure requirements are always met
        for _ in range(100):
            password = generate_strong_password()
            has_upper = any(c in string.ascii_uppercase for c in password)
            has_lower = any(c in string.ascii_lowercase for c in password)
            has_digit = any(c in string.digits for c in password)

            self.assertTrue(has_upper, f"Password {password} missing uppercase")
            self.assertTrue(has_lower, f"Password {password} missing lowercase")
            self.assertTrue(has_digit, f"Password {password} missing digit")

    def test_generate_strong_password_characters(self):
        allowed_chars = set(string.ascii_letters + string.digits)
        password = generate_strong_password(20)
        for char in password:
            self.assertIn(char, allowed_chars)

if __name__ == '__main__':
    unittest.main()
