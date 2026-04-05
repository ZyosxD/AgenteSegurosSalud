import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure the root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock selenium
mock_selenium = MagicMock()
sys.modules["selenium"] = mock_selenium
sys.modules["selenium.webdriver"] = mock_selenium
sys.modules["selenium.webdriver.common"] = mock_selenium
sys.modules["selenium.webdriver.common.by"] = mock_selenium
sys.modules["selenium.webdriver.support"] = mock_selenium
sys.modules["selenium.webdriver.support.ui"] = mock_selenium
sys.modules["selenium.webdriver.support.expected_conditions"] = mock_selenium

from src.utils import close_popups

class TestClosePopups(unittest.TestCase):
    @patch('src.utils.force_click')
    @patch('src.utils.WebDriverWait')
    def test_close_popups_clicks_displayed_buttons(self, mock_wait, mock_force_click):
        driver = MagicMock()

        # Mock buttons
        btn1 = MagicMock()
        btn1.is_displayed.return_value = True
        btn2 = MagicMock()
        btn2.is_displayed.return_value = False
        btn3 = MagicMock()
        btn3.is_displayed.return_value = True

        driver.find_elements.return_value = [btn1, btn2, btn3]
        mock_force_click.return_value = True

        close_popups(driver)

        # Should call force_click for btn1 and btn3
        self.assertEqual(mock_force_click.call_count, 2)
        mock_force_click.assert_any_call(driver, btn1)
        mock_force_click.assert_any_call(driver, btn3)

        # Should call WebDriverWait for both clicked buttons
        self.assertEqual(mock_wait.call_count, 2)

    @patch('src.utils.force_click')
    @patch('src.utils.WebDriverWait')
    def test_close_popups_handles_exception(self, mock_wait, mock_force_click):
        driver = MagicMock()
        driver.find_elements.side_effect = Exception("Browser error")

        # Should not raise exception
        try:
            close_popups(driver)
        except Exception as e:
            self.fail(f"close_popups raised {e} unexpectedly!")

if __name__ == '__main__':
    unittest.main()
