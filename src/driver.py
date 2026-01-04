import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from src import utils

def start_driver():
    """
    Inicia el WebDriver de Selenium (Chrome).
    """
    logging.info("Intentando iniciar el navegador...")
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info("Navegador iniciado correctamente.")
        return driver
    except Exception as e:
        logging.critical(f"Error fatal al iniciar el navegador: {e}")
        # Pass None as driver since it failed to start
        utils.request_human_help(str(e), driver=None)
        return None
