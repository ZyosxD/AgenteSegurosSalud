import time
import sys
import os
from unittest.mock import MagicMock, patch

# Ensure the root directory is in sys.path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock selenium modules because they might not be installed
mock_selenium = MagicMock()
sys.modules["selenium"] = mock_selenium
sys.modules["selenium.webdriver"] = mock_selenium
sys.modules["selenium.webdriver.common"] = mock_selenium
sys.modules["selenium.webdriver.common.by"] = mock_selenium
sys.modules["selenium.webdriver.support"] = mock_selenium
sys.modules["selenium.webdriver.support.ui"] = mock_selenium
sys.modules["selenium.webdriver.support.expected_conditions"] = mock_selenium

from src.utils import close_popups
from selenium.webdriver.common.by import By

def benchmark_close_popups():
    driver = MagicMock()

    # Create 3 mock buttons that are displayed
    mock_btn = MagicMock()
    mock_btn.is_displayed.return_value = True

    # driver.find_elements should return these 3 buttons
    driver.find_elements.return_value = [mock_btn, mock_btn, mock_btn]

    # Mock force_click to do nothing (we want to measure the sleep)
    with patch('src.utils.force_click') as mock_force_click:
        start_time = time.time()
        close_popups(driver)
        end_time = time.time()

    duration = end_time - start_time
    print(f"Execution time for 3 popups: {duration:.4f} seconds")
    return duration

if __name__ == "__main__":
    benchmark_close_popups()
