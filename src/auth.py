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
                wait = WebDriverWait(driver, 15) # Aumentado tiempo de espera

                # 1. Selección de Estado (Primer paso)
                logging.info("Buscando selector de estado...")
                state = new_user_data.get('state')

                state_selected_successfully = False

                if state:
                    try:
                        # Intentamos encontrar un dropdown (Select) clásico
                        try:
                            state_dropdown = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "select")))
                            select = Select(state_dropdown)
                            try:
                                select.select_by_value(state)
                                logging.info(f"Estado '{state}' seleccionado por valor.")
                            except:
                                select.select_by_visible_text(state)
                                logging.info(f"Estado '{state}' seleccionado por texto.")
                            state_selected_successfully = True
                        except:
                            # Estrategia alternativa: Puede ser un dropdown estilo custom (div/ul) o un botón
                            logging.info("No se encontró <select> estándar. Buscando alternativas por texto...")
                            # Intentar encontrar un elemento clicable que contenga "Seleccione" o "Select"
                            dropdown_trigger = driver.find_element(By.XPATH, "//*[contains(text(), 'Seleccione') or contains(text(), 'Select')]")
                            dropdown_trigger.click()
                            time.sleep(1)
                            # Intentar click en la opción del estado
                            state_option = driver.find_element(By.XPATH, f"//*[contains(text(), '{state}')]")
                            state_option.click()
                            state_selected_successfully = True

                        # Click en Continuar
                        if state_selected_successfully:
                            try:
                                continue_btn = driver.find_element(By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'continu')]")
                                continue_btn.click()
                                logging.info("Click en botón Continuar/Continue.")
                                time.sleep(5) # Esperar transición de página
                            except:
                                logging.info("No se encontró botón explícito de continuar, esperando transición automática...")

                    except Exception as e:
                         logging.warning(f"No se pudo seleccionar el estado automáticamente: {e}")
                         # Fallback crítico: Pedir ayuda pero NO fallar el flujo completo inmediatamente
                         utils.request_human_help("Seleccione el estado manualmente y presione continuar.", driver=driver)

                # 2. Formulario de Datos Personales
                logging.info("Esperando carga del formulario de registro...")

                # Bucle de espera más inteligente para el formulario
                form_loaded = False
                for _ in range(3): # 3 intentos de espera
                    try:
                        wait.until(EC.visibility_of_element_located((By.ID, "firstName")))
                        form_loaded = True
                        break
                    except:
                        logging.info("Esperando campo 'firstName'...")
                        time.sleep(2)

                if not form_loaded:
                     logging.warning("No se detectó la carga automática del formulario. Verifique si se requiere acción manual.")
                     utils.request_human_help("Asegúrese de estar en la página de registro (Nombre, Email, etc).", driver=driver)

                logging.info("Llenando campos de datos personales...")
                # Nombre y Apellido
                driver.find_element(By.ID, "firstName").send_keys(new_user_data.get('first_name'))
                driver.find_element(By.ID, "lastName").send_keys(new_user_data.get('last_name'))

                # Email
                driver.find_element(By.ID, "email").send_keys(new_user_data.get('email'))

                # Contraseña
                driver.find_element(By.ID, "password").send_keys(new_user_data.get('password'))
                # Confirmación de contraseña (si existe)
                try:
                    driver.find_element(By.ID, "confirmPassword").send_keys(new_user_data.get('password'))
                except:
                    pass

                logging.info("Campos principales llenados.")

            except Exception as e:
                logging.warning(f"Error automatizando el formulario: {e}")
                # Permitimos caer al bloque de verificación manual

            # --------------------------------------

            logging.info("Por favor, revise que los datos en el navegador sean correctos y haga clic en 'Crear Cuenta' si no se hizo automáticamente.")

            logging.info("Esperando verificación de cuenta (OTP)...")
            print("\n--- Verificación de Cuenta ---")
            print("Si el sistema solicita un código, ingréselo aquí. Si no, presione Enter para continuar.")
            otp_code = input("Código de verificación (o Enter para saltar): ")

            if otp_code:
                logging.info(f"Código OTP {otp_code} ingresado por el usuario.")
                try:
                    driver.find_element(By.ID, "otpCode").send_keys(otp_code)
                    driver.find_element(By.ID, "verifyButton").click()
                except:
                    logging.info("No se encontró campo automático para OTP.")

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

                # Intentar encontrar botón de login
                try:
                    login_btn = driver.find_element(By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'iniciar')]")
                    login_btn.click()
                except:
                     logging.info("No se pudo hacer click automático en Login. Hágalo manualmente.")

            except Exception as e:
                logging.warning(f"Error interactuando con campos de login: {e}")

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
