import json
import os
import logging
import traceback
import random
import string
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
    chars = string.ascii_letters + string.digits # Alphanumeric only per typical strict rules, can add punctuation if allowed

    # Ensure at least one of each required type
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice(string.digits)
    ]

    # Fill the rest
    password += [random.choice(chars) for _ in range(length - len(password))]

    # Shuffle
    random.shuffle(password)

    return "".join(password)
