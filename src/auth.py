import time
import json
import os
import logging
from src import config, utils

def save_registered_user(new_user_data):
    """
    Guarda los datos del usuario registrado en una base de datos local.
    """
    db_file = config.DB_FILE
    logging.info(f"Guardando registro en {db_file}...")

    try:
        if os.path.exists(db_file):
            with open(db_file, 'r', encoding='utf-8') as f:
                users_db = json.load(f)
        else:
            users_db = []

        user_record = new_user_data.copy()
        user_record['registration_date'] = time.strftime("%Y-%m-%d %H:%M:%S")

        existing_user_index = next((index for (index, d) in enumerate(users_db) if d["email"] == user_record["email"]), None)

        if existing_user_index is not None:
            users_db[existing_user_index] = user_record
            logging.info(f"Actualizando registro existente para {user_record['email']}.")
        else:
            users_db.append(user_record)
            logging.info(f"Añadiendo nuevo registro para {user_record['email']}.")

        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(users_db, f, indent=4)
        logging.info("Base de datos actualizada correctamente.")

    except Exception as e:
        utils.request_human_help(f"Error al guardar en base de datos: {e}", driver=None)

def create_account(driver, new_user_data):
    """
    Maneja el flujo de creación de una nueva cuenta.
    """
    if not new_user_data:
        logging.warning("No hay datos de nuevo usuario disponibles.")
        return

    create_url = config.URL_CREATE_ACCOUNT

    while True:
        try:
            logging.info(f"Navegando a {create_url}...")
            if driver:
                driver.get(create_url)

            if not utils.ask_confirmation("Iniciar proceso de registro con datos cargados"):
                return

            logging.info("Llenando formulario de registro...")
            logging.info(f"Datos: {new_user_data.get('first_name')} {new_user_data.get('last_name')}, {new_user_data.get('email')}")

            # Simulación de llenado (Placeholder para selectores reales)
            # ... lógica de selenium ...

            logging.info("Simulando envío del formulario...")
            time.sleep(2)

            logging.info("Esperando verificación de cuenta (OTP)...")
            print("\n--- Verificación de Cuenta ---")
            otp_code = input("Por favor, ingrese el código de verificación recibido (email/teléfono): ")

            if otp_code:
                logging.info(f"Código OTP {otp_code} ingresado por el usuario.")
                # ... enviar código ...
                logging.info("Cuenta creada exitosamente (simulado).")
                save_registered_user(new_user_data)
                break # Salir del bucle si todo sale bien
            else:
                logging.warning("No se ingresó código OTP.")
                if utils.request_human_help("Código OTP faltante", driver=driver) != 'retry':
                    break

        except Exception as e:
            action = utils.request_human_help(f"Error en creación de cuenta: {e}", driver=driver)
            if action == 'continue':
                break

def login(driver, data):
    """
    Navega a la página de inicio de sesión y simula el login con 2FA.
    """
    if not data:
        logging.warning("No hay datos de usuario para login.")
        return

    login_url = config.URL_LOGIN

    while True:
        try:
            logging.info(f"Navegando a {login_url}...")
            if driver:
                driver.get(login_url)

            if not utils.ask_confirmation("Iniciar sesión con las credenciales cargadas"):
                return

            logging.info(f"Ingresando credenciales para usuario: {data.get('username')}")
            # ... lógica selenium ...

            time.sleep(1)
            logging.info("Solicitando código 2FA al usuario...")

            otp_code = input("Ingrese el código de verificación de inicio de sesión (SMS/Email): ")

            if otp_code:
                logging.info(f"Código 2FA {otp_code} recibido.")
                # ... enviar código ...
                logging.info("Login completado exitosamente (simulado).")
                break
            else:
                logging.warning("Login incompleto: falta código 2FA.")
                if utils.request_human_help("Falta código 2FA", driver=driver) != 'retry':
                    break

        except Exception as e:
            action = utils.request_human_help(f"Error en Login: {e}", driver=driver)
            if action == 'continue':
                break
