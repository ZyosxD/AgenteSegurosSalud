import time
import json
import os
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
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

            # --- INTERACCIÓN REAL CON FORMULARIO ---
            try:
                wait = WebDriverWait(driver, 10)

                # 1. Selección de Estado (Primer paso)
                logging.info("Buscando selector de estado...")
                state = new_user_data.get('state')
                if state:
                    try:
                        # Intentamos encontrar un dropdown (Select)
                        # Nota: El ID "stateDropdown" es una suposición. El usuario debe actualizarlo si falla.
                        state_dropdown = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "select")))
                        select = Select(state_dropdown)
                        select.select_by_value(state) # O select_by_visible_text si es necesario
                        logging.info(f"Estado '{state}' seleccionado.")

                        # Click en Continuar (si existe un botón específico para esto)
                        # continue_btn = driver.find_element(By.ID, "continueBtn")
                        # continue_btn.click()
                        time.sleep(2) # Esperar a que cargue el siguiente formulario
                    except Exception as e:
                         logging.warning(f"No se pudo seleccionar el estado automáticamente: {e}")

                # 2. Formulario de Datos Personales
                logging.info("Buscando campos de datos personales...")
                # Nombre y Apellido
                driver.find_element(By.ID, "firstName").send_keys(new_user_data.get('first_name'))
                driver.find_element(By.ID, "lastName").send_keys(new_user_data.get('last_name'))

                # Email
                driver.find_element(By.ID, "email").send_keys(new_user_data.get('email'))

                # Contraseña (si existe campo de confirmación, se asume 'password' y 'confirmPassword')
                driver.find_element(By.ID, "password").send_keys(new_user_data.get('password'))
                # driver.find_element(By.ID, "confirmPassword").send_keys(new_user_data.get('password'))

                # Preguntas de seguridad
                security_questions = new_user_data.get('security_questions', [])
                if security_questions and len(security_questions) > 0:
                     # Ejemplo para primera pregunta (puede variar si son dropdowns)
                     # driver.find_element(By.ID, "securityQuestion1").send_keys(security_questions[0]['answer'])
                     pass

                logging.info("Formulario llenado. Esperando confirmación para enviar...")

                # Botón de crear cuenta
                # btn = driver.find_element(By.ID, "createAccountButton")
                # btn.click()

            except Exception as e:
                logging.warning(f"No se pudieron encontrar algunos campos automáticamente: {e}")
                # No lanzamos error fatal aquí para permitir que request_human_help maneje la corrección manual

            # --------------------------------------

            logging.info("Por favor, revise que los datos en el navegador sean correctos y haga clic en 'Crear Cuenta' si no se hizo automáticamente.")

            logging.info("Esperando verificación de cuenta (OTP)...")
            print("\n--- Verificación de Cuenta ---")
            print("Si el sistema solicita un código, ingréselo aquí. Si no, presione Enter para continuar.")
            otp_code = input("Código de verificación (o Enter para saltar): ")

            if otp_code:
                logging.info(f"Código OTP {otp_code} ingresado por el usuario.")
                # Intentar ingresar el OTP si existe el campo
                try:
                    driver.find_element(By.ID, "otpCode").send_keys(otp_code)
                    driver.find_element(By.ID, "verifyButton").click()
                except:
                    logging.info("No se encontró campo automático para OTP, asumiendo ingreso manual o flujo diferente.")

            logging.info("Proceso de creación finalizado (según flujo del bot).")
            save_registered_user(new_user_data)
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

            # --- INTERACCIÓN REAL CON FORMULARIO LOGIN ---
            try:
                # Esperar a que el campo username sea visible
                wait = WebDriverWait(driver, 10)
                user_field = wait.until(EC.visibility_of_element_located((By.ID, "username")))
                user_field.clear()
                user_field.send_keys(data.get('username'))

                pass_field = driver.find_element(By.ID, "password")
                pass_field.clear()
                pass_field.send_keys(data.get('password'))

                login_btn = driver.find_element(By.ID, "loginBtn") # ID hipotético
                login_btn.click()

            except Exception as e:
                logging.warning(f"Error interactuando con campos de login (IDs pueden haber cambiado): {e}")

            # ---------------------------------------------

            logging.info("Solicitando código 2FA al usuario (si es requerido)...")

            otp_code = input("Ingrese el código de verificación 2FA (si se solicita), o Enter para continuar: ")

            if otp_code:
                logging.info(f"Código 2FA {otp_code} recibido.")
                try:
                    driver.find_element(By.ID, "securityCode").send_keys(otp_code)
                    driver.find_element(By.ID, "verifyBtn").click()
                except:
                     pass

            logging.info("Login completado.")
            break

        except Exception as e:
            action = utils.request_human_help(f"Error en Login: {e}", driver=driver)
            if action == 'continue':
                break
