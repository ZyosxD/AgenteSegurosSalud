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
                wait = WebDriverWait(driver, 15)

                # 1. Selección de Estado (Primer paso)
                logging.info("Buscando selector de estado...")
                state = new_user_data.get('state')
                state_selected_successfully = False

                if state:
                    try:
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
                            logging.info("No se encontró <select> estándar. Buscando alternativas por texto...")
                            dropdown_trigger = driver.find_element(By.XPATH, "//*[contains(text(), 'Seleccione') or contains(text(), 'Select')]")
                            dropdown_trigger.click()
                            time.sleep(1)
                            state_option = driver.find_element(By.XPATH, f"//*[contains(text(), '{state}')]")
                            state_option.click()
                            state_selected_successfully = True

                        if state_selected_successfully:
                            try:
                                continue_btn = driver.find_element(By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'continu')]")
                                continue_btn.click()
                                logging.info("Click en botón Continuar/Continue.")
                                time.sleep(5)
                            except:
                                logging.info("No se encontró botón explícito de continuar, esperando transición automática...")

                    except Exception as e:
                         logging.warning(f"No se pudo seleccionar el estado automáticamente: {e}")
                         utils.request_human_help("Seleccione el estado manualmente y presione continuar.", driver=driver)

                # 2. Formulario de Datos Personales
                logging.info("Esperando carga del formulario de registro...")

                possible_first_name_locators = [
                    (By.ID, "firstName"),
                    (By.NAME, "firstName"),
                    (By.XPATH, "//input[contains(@aria-label, 'nombre')]"),
                    (By.XPATH, "//label[contains(text(), 'nombre')]/following-sibling::input"),
                    (By.XPATH, "//label[contains(text(), 'First name')]/following-sibling::input")
                ]

                form_loaded = False
                first_name_element = None

                for _ in range(3):
                    for locator in possible_first_name_locators:
                        try:
                            first_name_element = wait.until(EC.visibility_of_element_located(locator))
                            logging.info(f"Formulario detectado usando selector: {locator}")
                            form_loaded = True
                            break
                        except:
                            continue
                    if form_loaded:
                        break
                    logging.info("Aún esperando campo 'Primer Nombre'...")
                    time.sleep(2)

                if not form_loaded:
                     logging.warning("No se detectó la carga automática del formulario. Verifique si se requiere acción manual.")
                     utils.request_human_help("Asegúrese de estar en la página de registro (Nombre, Email, etc).", driver=driver)
                     try:
                         first_name_element = driver.find_element(By.ID, "firstName")
                     except:
                         pass

                logging.info("Llenando campos de datos personales...")

                def robust_fill(driver, locators, value):
                    for loc in locators:
                        try:
                            el = driver.find_element(*loc)
                            el.clear()
                            el.send_keys(value)
                            return True
                        except:
                            continue
                    return False

                # Nombre
                if not robust_fill(driver, [(By.ID, "firstName"), (By.NAME, "firstName")], new_user_data.get('first_name')):
                    if first_name_element:
                        first_name_element.send_keys(new_user_data.get('first_name'))

                # Apellido
                robust_fill(driver, [(By.ID, "lastName"), (By.NAME, "lastName")], new_user_data.get('last_name'))

                # Email
                robust_fill(driver, [(By.ID, "email"), (By.NAME, "email")], new_user_data.get('email'))

                # Generar Contraseña Segura
                logging.info("Generando contraseña segura...")
                strong_password = utils.generate_strong_password()
                new_user_data['password'] = strong_password # Actualizar datos en memoria para guardar después

                # Contraseña
                robust_fill(driver, [(By.ID, "password"), (By.NAME, "password")], strong_password)

                # Confirmación (si existe)
                robust_fill(driver, [(By.ID, "confirmPassword"), (By.NAME, "confirmPassword")], strong_password)

                # Preguntas de seguridad
                try:
                    selects = driver.find_elements(By.TAG_NAME, "select")

                    question_selects = [s for s in selects if "question" in s.get_attribute("id").lower() or "pregunta" in s.get_attribute("id").lower() or "question" in s.get_attribute("name").lower()]

                    if not question_selects and len(selects) >= 3:
                        question_selects = selects[-3:]

                    security_data = new_user_data.get('security_questions', [])

                    for i, sel in enumerate(question_selects):
                        try:
                            select_obj = Select(sel)
                            select_obj.select_by_index(1) # Seleccionar la primera pregunta real

                            answer_input = sel.find_element(By.XPATH, "following::input[@type='text'][1]")

                            ans = "Respuesta"
                            if i < len(security_data):
                                ans = security_data[i].get('answer', "Respuesta")

                            answer_input.send_keys(ans)
                            logging.info(f"Pregunta de seguridad {i+1} llenada.")
                        except Exception as ex:
                            logging.warning(f"Error llenando pregunta {i+1}: {ex}")

                except Exception as e:
                     logging.warning(f"Error llenando preguntas de seguridad: {e}")

                # Checkbox de Términos
                try:
                    terms_checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox']")
                    if not terms_checkbox.is_selected():
                        try:
                            terms_checkbox.click()
                        except:
                            driver.find_element(By.XPATH, "//label[contains(., 'Entiendo') or contains(., 'I understand')]").click()
                    logging.info("Términos aceptados.")
                except:
                    logging.warning("No se encontró checkbox de términos.")

                # Click en Crear Cuenta
                try:
                    create_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Crear') or contains(text(), 'Create')]")
                    create_btn.click()
                    logging.info("Click en botón Crear Cuenta.")
                except:
                    logging.info("No se encontró botón Crear Cuenta explícito.")

            except Exception as e:
                logging.warning(f"Error automatizando el formulario: {e}")

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
