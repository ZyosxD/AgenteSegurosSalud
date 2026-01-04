import json
import os
import time
import logging
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class HealthCareBot:
    def __init__(self, data_file, new_user_file="data/newuser.txt"):
        """
        Inicializa el bot con las rutas de los archivos de datos y configura el logging.
        """
        self.setup_logging()
        self.data_file = data_file
        self.new_user_file = new_user_file
        self.data = self.load_json_file(self.data_file)
        self.new_user_data = self.load_json_file(self.new_user_file)
        self.driver = None

    def setup_logging(self):
        """
        Configura el sistema de logging para escribir en archivo y consola.
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("bot_activity.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        logging.info("=== Iniciando Sesión del Bot ===")

    def request_human_help(self, error_message):
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
                if self.driver:
                    self.driver.quit()
                exit()
            else:
                print("Opción no válida.")

    def load_json_file(self, filepath):
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

    def start_driver(self):
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
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logging.info("Navegador iniciado correctamente.")
        except Exception as e:
            logging.critical(f"Error fatal al iniciar el navegador: {e}")
            self.request_human_help(str(e))

    def ask_confirmation(self, action_description):
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

    def create_account(self):
        """
        Maneja el flujo de creación de una nueva cuenta.
        """
        if not self.new_user_data:
            logging.warning("No hay datos de nuevo usuario disponibles.")
            return

        create_url = "https://www.cuidadodesalud.gov/create-account"

        while True:
            try:
                logging.info(f"Navegando a {create_url}...")
                if self.driver:
                    self.driver.get(create_url)

                if not self.ask_confirmation("Iniciar proceso de registro con datos cargados"):
                    return

                logging.info("Llenando formulario de registro...")
                logging.info(f"Datos: {self.new_user_data.get('first_name')} {self.new_user_data.get('last_name')}, {self.new_user_data.get('email')}")

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
                    self.save_registered_user()
                    break # Salir del bucle si todo sale bien
                else:
                    logging.warning("No se ingresó código OTP.")
                    if self.request_human_help("Código OTP faltante") != 'retry':
                        break

            except Exception as e:
                action = self.request_human_help(f"Error en creación de cuenta: {e}")
                if action == 'continue':
                    break
                # Si es 'retry', el bucle while reiniciará el proceso

    def save_registered_user(self):
        """
        Guarda los datos del usuario registrado en una base de datos local.
        """
        db_file = "data/user_database.json"
        logging.info(f"Guardando registro en {db_file}...")

        try:
            if os.path.exists(db_file):
                with open(db_file, 'r', encoding='utf-8') as f:
                    users_db = json.load(f)
            else:
                users_db = []

            user_record = self.new_user_data.copy()
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
            self.request_human_help(f"Error al guardar en base de datos: {e}")

    def login(self):
        """
        Navega a la página de inicio de sesión y simula el login con 2FA.
        """
        if not self.data:
            logging.warning("No hay datos de usuario para login.")
            return

        login_url = "https://www.cuidadodesalud.gov/login"

        while True:
            try:
                logging.info(f"Navegando a {login_url}...")
                if self.driver:
                    self.driver.get(login_url)

                if not self.ask_confirmation("Iniciar sesión con las credenciales cargadas"):
                    return

                logging.info(f"Ingresando credenciales para usuario: {self.data.get('username')}")
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
                    if self.request_human_help("Falta código 2FA") != 'retry':
                        break

            except Exception as e:
                action = self.request_human_help(f"Error en Login: {e}")
                if action == 'continue':
                    break

    def fill_profile(self):
        """
        Llena el perfil del usuario.
        """
        if not self.ask_confirmation("Llenar información del perfil"):
            logging.info("Usuario saltó el llenado de perfil.")
            return

        logging.info("Iniciando llenado de perfil...")

        while True:
            try:
                # Verificar con el usuario
                logging.info("Mostrando datos actuales para confirmación...")
                print(f"Nombre: {self.data.get('first_name')} {self.data.get('last_name')}")
                print(f"Dirección: {self.data.get('address')}")

                if self.ask_confirmation("¿Son correctos estos datos en el formulario?"):
                    logging.info("Datos de perfil confirmados por el usuario.")
                    break
                else:
                    logging.info("Usuario indicó datos incorrectos. Iniciando corrección manual.")
                    self.redo_form()
                    logging.info("Reintentando llenado con nuevos datos...")
            except Exception as e:
                 action = self.request_human_help(f"Error en llenado de perfil: {e}")
                 if action == 'continue':
                     break

    def redo_form(self):
        """
        Permite corrección manual de datos.
        """
        print("\n--- Corrección Manual de Datos ---")
        fields_to_update = ["first_name", "last_name", "address", "city", "state", "zip_code", "income"]

        for field in fields_to_update:
            current_value = self.data.get(field)
            new_value = input(f"Ingrese valor para '{field}' (Actual: {current_value}): ").strip()
            if new_value:
                self.data[field] = new_value
                logging.info(f"Campo '{field}' actualizado a: {new_value}")

        logging.info("Datos en memoria actualizados.")

    def verify_plans(self):
        """
        Verifica planes disponibles.
        """
        logging.info("Iniciando verificación de planes...")
        if not self.ask_confirmation("Buscar planes que coincidan con las necesidades"):
            return

        try:
            preferences = self.data.get("plan_preferences", {})
            logging.info(f"Criterios de búsqueda: Nivel {preferences.get('metal_level')}, Max Prima ${preferences.get('max_premium')}")
            # ... scraping logic ...
            logging.info("Búsqueda de planes finalizada.")
        except Exception as e:
            self.request_human_help(f"Error buscando planes: {e}")

    def run(self):
        """
        Ejecuta el flujo principal.
        """
        print("\n=== Bot de Automatización CuidadoDeSalud.gov ===")
        print("1. Iniciar Sesión (Login)")
        print("2. Crear Nueva Cuenta")

        choice = input("\nSeleccione una opción (1 o 2): ").strip()

        self.start_driver()

        try:
            if choice == '1':
                logging.info("Modo seleccionado: Login")
                self.login()
                self.fill_profile()
                self.verify_plans()
            elif choice == '2':
                logging.info("Modo seleccionado: Crear Cuenta")
                self.create_account()
                if self.ask_confirmation("¿Desea continuar al llenado de perfil con los datos de usuario existente?"):
                     self.fill_profile()
                     self.verify_plans()
            else:
                logging.warning("Opción de menú no válida.")
                print("Opción no válida. Saliendo.")

            logging.info("=== Proceso finalizado con éxito ===")

        except KeyboardInterrupt:
            logging.warning("Ejecución interrumpida por el usuario (KeyboardInterrupt).")
        except Exception as e:
            logging.critical(f"Error no manejado en el bucle principal: {e}")
            self.request_human_help(f"Error crítico: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("Navegador cerrado.")

if __name__ == "__main__":
    bot = HealthCareBot("data/namefull.txt")
    bot.run()
