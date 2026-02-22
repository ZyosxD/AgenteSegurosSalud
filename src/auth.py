import time
import json
import os
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
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

            # Intentar localizar el contenedor principal para evitar clicks en el header/footer
            try:
                main_content = driver.find_element(By.CSS_SELECTOR, "main, #root, .ds-l-container, #main-content")
            except:
                main_content = None # Fallback global

            # --- INTERACCIÓN REAL CON FORMULARIO ---
            try:
                wait = WebDriverWait(driver, 15)

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
                            # Estrategia alternativa usando utils.select_option_by_text y force_click
                            logging.info("No se encontró <select> estándar. Buscando alternativas custom...")

                            # Buscar el trigger: Botón o div con texto "Seleccione" dentro del contenido principal
                            trigger_found = utils.select_option_by_text(driver, "Seleccione", scope_element=main_content)
                            if not trigger_found:
                                # Intenta buscar triggers por role listbox o combobox
                                logging.info("Buscando trigger por rol...")
                                triggers = driver.find_elements(By.CSS_SELECTOR, "[role='combobox'], [role='listbox']")
                                for t in triggers:
                                    if t.is_displayed():
                                        utils.force_click(driver, t)
                                        trigger_found = True
                                        break

                            if trigger_found:
                                time.sleep(1)
                                # Buscar opción del estado y clickearla, restringido al main content si es posible
                                state_selected_successfully = utils.select_option_by_text(driver, state, scope_element=main_content)

                        # Click en Continuar
                        if state_selected_successfully:
                            try:
                                continue_btn = driver.find_element(By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'continu')]")
                                utils.force_click(driver, continue_btn)
                                logging.info("Click en botón Continuar/Continue. Esperando transición de página...")
                                try:
                                    # Espera dinámica: continúa en cuanto el botón desaparece del DOM (cambio de página)
                                    wait.until(EC.staleness_of(continue_btn))
                                except (TimeoutException, StaleElementReferenceException):
                                    # Si hay timeout o ya es stale, seguimos; el siguiente bloque validará la nueva página
                                    pass
                            except:
                                logging.info("No se encontró botón explícito de continuar, esperando transición automática...")

                    except Exception as e:
                         logging.warning(f"No se pudo seleccionar el estado automáticamente: {e}")
                         utils.request_human_help("Seleccione el estado manualmente y presione continuar.", driver=driver)

                # 2. Formulario de Datos Personales
                logging.info("Esperando carga del formulario de registro...")

                # Bucle de espera más inteligente y robusto para el formulario
                possible_first_name_locators = [
                    (By.ID, "firstName"),
                    (By.NAME, "firstName"),
                    (By.XPATH, "//input[contains(@aria-label, 'nombre')]"),
                    (By.XPATH, "//label[contains(text(), 'nombre')]/following-sibling::input"),
                    (By.XPATH, "//label[contains(text(), 'First name')]/following-sibling::input")
                ]

                form_loaded = False
                first_name_element = None

                for _ in range(3): # 3 intentos de espera
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
                     # Intentamos recuperar de nuevo por si el usuario lo arregló
                     try:
                         first_name_element = driver.find_element(By.ID, "firstName")
                     except:
                         pass

                logging.info("Llenando campos de datos personales...")

                # Helper function para intentar llenar campos con varios selectores y estrategias
                def robust_fill(driver, locators, value, is_password=False):
                    for loc in locators:
                        try:
                            el = driver.find_element(*loc)
                            # Scroll to element to ensure it is clickable/visible
                            driver.execute_script("arguments[0].scrollIntoView(true);", el)
                            time.sleep(0.5)

                            # Wait for clickability
                            try:
                                WebDriverWait(driver, 5).until(EC.element_to_be_clickable(loc))
                            except:
                                pass # Try anyway even if wait fails

                            el.clear()
                            el.send_keys(value)

                            # Verificación opcional para campos normales
                            if not is_password and el.get_attribute('value') != value:
                                logging.warning(f"send_keys falló, intentando JS injection para {loc}")
                                driver.execute_script("arguments[0].value = arguments[1];", el, value)
                                driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", el)

                            return True
                        except:
                            continue
                    return False

                # Nombre
                if not robust_fill(driver, [(By.ID, "firstName"), (By.NAME, "firstName")], new_user_data.get('first_name')):
                    if first_name_element: # Fallback al elemento encontrado antes
                        first_name_element.send_keys(new_user_data.get('first_name'))

                # Apellido
                robust_fill(driver, [(By.ID, "lastName"), (By.NAME, "lastName")], new_user_data.get('last_name'))

                # Email
                robust_fill(driver, [(By.ID, "email"), (By.NAME, "email")], new_user_data.get('email'))

                # Generar Contraseña Segura
                logging.info("Generando contraseña segura...")
                strong_password = utils.generate_strong_password()
                new_user_data['password'] = strong_password # Actualizar datos en memoria para guardar después
                logging.info(f"Contraseña generada: {strong_password[:2]}...{strong_password[-2:]}")

                # Contraseña - Agregamos estrategia JS por si acaso es un campo complejo
                logging.info("Intentando llenar campo de contraseña...")
                # Agregamos selectores adicionales específicos para password
                pwd_locators = [
                    (By.ID, "password"),
                    (By.NAME, "password"),
                    (By.CSS_SELECTOR, "input[type='password']"),
                    (By.XPATH, "//input[@type='password']")
                ]

                if robust_fill(driver, pwd_locators, strong_password, is_password=True):
                    logging.info("Campo contraseña llenado.")
                else:
                    logging.warning("No se pudo llenar la contraseña por métodos estándar. Intentando inyección JS directa.")
                    try:
                        pwd_el = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                        driver.execute_script("arguments[0].value = arguments[1];", pwd_el, strong_password)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", pwd_el)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", pwd_el)
                        logging.info("Contraseña inyectada vía JS.")
                    except Exception as e_pwd:
                        logging.error(f"Fallo total llenando contraseña: {e_pwd}")

                # Confirmación (si existe)
                robust_fill(driver, [(By.ID, "confirmPassword"), (By.NAME, "confirmPassword")], strong_password, is_password=True)

                # Preguntas de seguridad
                try:
                    logging.info("Intentando llenar preguntas de seguridad...")
                    # Estrategia mejorada: Buscar SOLO después del campo de password para no volver al header/state

                    # Usamos XPath relativo al campo de password que acabamos de llenar
                    # Buscamos cualquier elemento clicable que parezca un dropdown (select, button, div con role)
                    # QUE ESTÉ DESPUÉS del input password.

                    xpath_triggers = """
                    //input[@type='password']/following::*[
                        self::select or
                        self::button[@aria-haspopup='listbox'] or
                        self::div[@role='combobox'] or
                        contains(@class, 'dropdown-trigger') or
                        contains(text(), 'Seleccione') or
                        contains(text(), 'Select')
                    ]
                    """

                    triggers = driver.find_elements(By.XPATH, xpath_triggers)

                    # Filtramos solo los visibles
                    visible_triggers = [t for t in triggers if t.is_displayed()]

                    # Tomamos hasta 3 (asumiendo que son las 3 preguntas)
                    questions_to_fill = visible_triggers[:3]
                    security_data = new_user_data.get('security_questions', [])

                    if not questions_to_fill:
                        logging.warning("No se encontraron dropdowns de preguntas después del campo password.")

                    for i, trigger in enumerate(questions_to_fill):
                        try:
                            logging.info(f"Interactuando con pregunta {i+1}...")
                            # Scroll y Click para abrir
                            utils.force_click(driver, trigger)
                            time.sleep(1)

                            # Buscar opciones y seleccionar la segunda (index 1)
                            # Buscamos elementos role="option" o li en general
                            options = driver.find_elements(By.CSS_SELECTOR, "[role='option'], li")
                            visible_options = [o for o in options if o.is_displayed()]

                            if len(visible_options) > 1:
                                target_option = visible_options[1] # Segunda opción (la primera suele ser "Seleccione...")
                                utils.force_click(driver, target_option)
                                logging.info(f"Opción seleccionada para pregunta {i+1}.")

                                # Llenar respuesta
                                # Buscamos el input de texto más cercano después del trigger
                                try:
                                    # Encontrar el input inmediatamente siguiente al trigger
                                    answer_input = trigger.find_element(By.XPATH, "following::input[@type='text'][1]")

                                    ans = "Respuesta"
                                    if i < len(security_data):
                                        ans = security_data[i].get('answer', "Respuesta")

                                    utils.force_click(driver, answer_input) # Focus
                                    answer_input.send_keys(ans)
                                    logging.info(f"Respuesta {i+1} llenada.")
                                except Exception as e_ans:
                                    logging.warning(f"No se pudo llenar respuesta {i+1}: {e_ans}")

                        except Exception as e_q:
                            logging.warning(f"Error en flujo de pregunta {i+1}: {e_q}")

                except Exception as e:
                     logging.warning(f"Error general llenando preguntas de seguridad: {e}")

                # Checkbox de Términos
                try:
                    # Buscar por ID o label for, restringiendo búsqueda
                    terms_chk = driver.find_element(By.XPATH, "//input[@type='checkbox']")
                    driver.execute_script("arguments[0].scrollIntoView(true);", terms_chk)
                    if not terms_chk.is_selected():
                        utils.force_click(driver, terms_chk)
                        # Si click directo falla, intentar label
                        if not terms_chk.is_selected():
                             driver.find_element(By.XPATH, "//label[contains(., 'Entiendo') or contains(., 'I understand')]").click()
                    logging.info("Términos aceptados.")
                except:
                    logging.warning("No se encontró checkbox de términos.")

                # Click en Crear Cuenta
                try:
                    create_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Crear') or contains(text(), 'Create')]")
                    driver.execute_script("arguments[0].scrollIntoView(true);", create_btn)
                    utils.force_click(driver, create_btn)
                    logging.info("Click en botón Crear Cuenta.")
                except:
                    logging.info("No se encontró botón Crear Cuenta explícito.")

            except Exception as e:
                logging.warning(f"Error automatizando el formulario: {e}")


            # --------------------------------------

            # Mensaje de ayuda humana mejorado
            remaining_tasks = "Revise: Contraseña, Preguntas de Seguridad, Términos y Botón Crear."
            logging.info(f"Automatización parcial completada. {remaining_tasks}")

            logging.info("Esperando verificación de cuenta (OTP)...")
            print("\n--- Verificación de Cuenta ---")
            print("1. Complete cualquier campo faltante en el navegador (Captcha, Preguntas, etc).")
            print("2. Haga clic en 'Crear Cuenta' si no se hizo.")
            print("3. Si el sistema solicita un código, ingréselo aquí. Si no, presione Enter para continuar.")
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
