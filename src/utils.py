import json
import os
import logging
import traceback
import random
import string
import time
from selenium.webdriver.common.by import By
from src import config

def setup_logging():
    """
    Configura el sistema de logging para escribir en archivo y consola.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logging.info("=== Iniciando Sesión del Bot ===")

def load_json_file(filepath):
    """
    Carga datos desde un archivo JSON.
    """
    if not os.path.exists(filepath):
        logging.warning(f"El archivo {filepath} no existe.")
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.info(f"Datos cargados exitosamente desde {filepath}.")
        return data
    except json.JSONDecodeError:
        logging.error(f"El archivo {filepath} no tiene un formato JSON válido.")
        return None

def ask_confirmation(action_description):
    """
    Solicita confirmación al usuario antes de realizar una acción.
    """
    logging.info(f"Solicitando confirmación para: {action_description}")
    while True:
        response = input(f"\n¿Desea proceder con: '{action_description}'? (s/n): ").lower().strip()
        if response == 's':
            logging.info("Usuario confirmó la acción.")
            return True
        elif response == 'n':
            logging.info("Usuario canceló la acción.")
            return False
        else:
            print("Respuesta no válida. Por favor ingrese 's' o 'n'.")

def request_human_help(error_message, driver=None):
    """
    Solicita intervención manual cuando ocurre un error.
    """
    logging.error(f"¡ERROR DETECTADO! {error_message}")
    logging.error(traceback.format_exc())

    print("\n" + "!"*50)
    print("SOLICITUD DE AYUDA HUMANA")
    print(f"Error: {error_message}")
    print("Por favor, realice las correcciones necesarias en el navegador.")
    print("!"*50 + "\n")

    while True:
        response = input("Escriba 'r' para reintentar la acción, 'c' para continuar al siguiente paso, o 'exit' para salir: ").lower().strip()
        if response == 'r':
            logging.info("El usuario seleccionó REINTENTAR.")
            return 'retry'
        elif response == 'c':
            logging.info("El usuario seleccionó CONTINUAR (saltar error).")
            return 'continue'
        elif response == 'exit':
            logging.info("El usuario seleccionó SALIR.")
            if driver:
                driver.quit()
            exit()
        else:
            print("Opción no válida.")

def generate_strong_password():
    """
    Genera una contraseña segura que cumple con los requisitos:
    - 8 a 20 caracteres
    - Letras mayúsculas y minúsculas
    - 1 o más números
    """
    length = 12
    chars = string.ascii_letters + string.digits

    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice(string.digits)
    ]

    password += [random.choice(chars) for _ in range(length - len(password))]
    random.shuffle(password)

    return "".join(password)

def close_popups(driver):
    """
    Intenta cerrar popups conocidos que puedan bloquear clicks.
    """
    try:
        # Selectores comunes de botones de cierre en popups (Qualtrics, etc)
        close_buttons = driver.find_elements(By.CSS_SELECTOR, ".close, .close-button, [aria-label='Close'], .QSIPopOverCloseButton")
        for btn in close_buttons:
            if btn.is_displayed():
                logging.info("Cerrando popup detectado...")
                force_click(driver, btn)
                time.sleep(1)
    except:
        pass

def force_click(driver, element):
    """
    Intenta hacer click en un elemento usando Selenium standard, y si falla, usa JavaScript.
    Maneja scroll para evitar 'element click intercepted'.
    """
    try:
        # Intentar scroll al centro antes de clickear
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", element)
        time.sleep(0.5)
        element.click()
        return True
    except Exception as e:
        logging.warning(f"Click estándar falló ({str(e).splitlines()[0]}), intentando JS click.")
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e_js:
            logging.error(f"JS Click también falló: {e_js}")
            return False

def select_option_by_text(driver, text, scope_element=None):
    """
    Busca un elemento visible que contenga el texto dado y le hace click forzado.
    Útil para dropdowns customizados.

    Args:
        driver: Selenium WebDriver
        text: Texto a buscar
        scope_element: (Opcional) WebElement para restringir la búsqueda (usando .//)
    """
    try:
        close_popups(driver)

        # Construir XPath basado en si hay un scope o es global
        if scope_element:
            # Búsqueda escopada (más rápida y específica)
            xpath = f".//*[contains(text(), '{text}')]"
            elements = scope_element.find_elements(By.XPATH, xpath)
            visible_elements = [el for el in elements if el.is_displayed()]
        else:
            # Búsqueda global optimizada: Intentar primero excluyendo header/nav/footer
            # Esto evita iterar sobre elementos irrelevantes y hacer llamadas lentas a is_displayed()
            xpath_optimized = f"//*[contains(text(), '{text}') and not(ancestor::header) and not(ancestor::nav) and not(ancestor::footer)]"
            elements = driver.find_elements(By.XPATH, xpath_optimized)
            visible_elements = [el for el in elements if el.is_displayed()]

            # Si no se encuentra nada en el contenido principal, buscar en todo el DOM (fallback)
            if not visible_elements:
                logging.info(f"No se encontró texto '{text}' en contenido principal, buscando en todo el DOM...")
                xpath_global = f"//*[contains(text(), '{text}')]"
                elements = driver.find_elements(By.XPATH, xpath_global)
                visible_elements = [el for el in elements if el.is_displayed()]

        if visible_elements:
            # Intenta click en el último (a menudo el más profundo/relevante en el DOM) o el primero
            target = visible_elements[-1]
            logging.info(f"Encontrado elemento con texto '{text}', intentando click.")
            return force_click(driver, target)
        else:
            logging.warning(f"No se encontraron elementos visibles con texto '{text}'.")
            return False
    except Exception as e:
        logging.error(f"Error buscando opción por texto '{text}': {e}")
        return False
