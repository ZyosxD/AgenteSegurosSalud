import json
import os
import time
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
        Inicializa el bot con las rutas de los archivos de datos.
        """
        self.data_file = data_file
        self.new_user_file = new_user_file
        self.data = self.load_json_file(self.data_file)
        self.new_user_data = self.load_json_file(self.new_user_file)
        self.driver = None

    def load_json_file(self, filepath):
        """
        Carga datos desde un archivo JSON.
        """
        if not os.path.exists(filepath):
            print(f"Advertencia: El archivo {filepath} no existe.")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Datos cargados exitosamente desde {filepath}.")
            return data
        except json.JSONDecodeError:
            print(f"Error: El archivo {filepath} no tiene un formato JSON válido.")
            return None

    def start_driver(self):
        """
        Inicia el WebDriver de Selenium (Chrome).
        """
        print("Iniciando navegador...")
        chrome_options = Options()
        # chrome_options.add_argument("--headless") # Descomentar para modo sin cabeza
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-extensions")

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("Navegador iniciado.")
        except Exception as e:
            print(f"Error al iniciar el navegador: {e}")

    def ask_confirmation(self, action_description):
        """
        Solicita confirmación al usuario antes de realizar una acción.
        """
        while True:
            response = input(f"\n¿Desea proceder con: '{action_description}'? (s/n): ").lower().strip()
            if response == 's':
                return True
            elif response == 'n':
                print("Acción cancelada por el usuario.")
                return False
            else:
                print("Respuesta no válida. Por favor ingrese 's' o 'n'.")

    def create_account(self):
        """
        Maneja el flujo de creación de una nueva cuenta.
        """
        if not self.new_user_data:
            print("No hay datos de nuevo usuario disponibles en 'data/newuser.txt'.")
            return

        create_url = "https://www.cuidadodesalud.gov/create-account"
        print(f"Navegando a {create_url} para crear cuenta...")

        if self.driver:
            self.driver.get(create_url)

        if not self.ask_confirmation("Iniciar proceso de registro con datos cargados"):
            return

        try:
            print("Llenando formulario de registro...")
            print(f"Nombre: {self.new_user_data.get('first_name')} {self.new_user_data.get('last_name')}")
            print(f"Email: {self.new_user_data.get('email')}")

            # Simulación de llenado de campos
            # self.driver.find_element(By.ID, "firstname").send_keys(self.new_user_data.get('first_name'))
            # self.driver.find_element(By.ID, "lastname").send_keys(self.new_user_data.get('last_name'))
            # self.driver.find_element(By.ID, "email").send_keys(self.new_user_data.get('email'))
            # ... questions ...

            print("Simulando envío del formulario de registro...")
            # submit_btn = self.driver.find_element(By.ID, "create-account-btn")
            # submit_btn.click()
            time.sleep(2)

            print("\n--- Verificación de Cuenta ---")
            print("El sistema probablemente ha enviado un código de verificación.")
            otp_code = input("Por favor, ingrese el código de verificación recibido (email/teléfono): ")

            if otp_code:
                print(f"Ingresando código {otp_code} en el sistema...")
                # otp_field = self.driver.find_element(By.ID, "otp-field")
                # otp_field.send_keys(otp_code)
                # verify_btn.click()
                print("Código enviado. Cuenta creada exitosamente (simulado).")
            else:
                print("No se ingresó código. Proceso detenido.")

        except Exception as e:
            print(f"Error durante la creación de cuenta: {e}")

    def login(self):
        """
        Navega a la página de inicio de sesión y simula el login con 2FA.
        """
        if not self.data:
            print("No hay datos de usuario para login.")
            return

        if not self.driver:
            print("El navegador no está iniciado.")
            return

        login_url = "https://www.cuidadodesalud.gov/login"
        print(f"Navegando a {login_url}...")
        self.driver.get(login_url)

        if not self.ask_confirmation("Iniciar sesión con las credenciales cargadas"):
            return

        try:
            print(f"Ingresando usuario: {self.data.get('username')}")
            # user_field = self.driver.find_element(By.ID, "username-field-id")
            # user_field.send_keys(self.data.get('username'))

            print("Ingresando contraseña...")
            # pass_field = self.driver.find_element(By.ID, "password-field-id")
            # pass_field.send_keys(self.data.get('password'))

            print("Simulando click en botón de Login...")
            # submit_button = self.driver.find_element(By.ID, "login-button-id")
            # submit_button.click()
            time.sleep(1)

            # Manejo de 2FA
            print("\n--- Verificación de Dos Pasos (2FA) ---")
            print("El sistema requiere verificación adicional.")
            otp_code = input("Ingrese el código de verificación de inicio de sesión (SMS/Email): ")

            if otp_code:
                print(f"Ingresando código {otp_code}...")
                # otp_field = self.driver.find_element(By.ID, "2fa-code-field")
                # otp_field.send_keys(otp_code)
                # verify_btn.click()
                print("Login verificado y completado (simulado).")
            else:
                print("No se ingresó código. Login incompleto.")

        except Exception as e:
            print(f"Error durante el inicio de sesión: {e}")

    def fill_profile(self):
        """
        Llena el perfil del usuario si es necesario.
        """
        if not self.ask_confirmation("Llenar información del perfil"):
            print("Saltando llenado de perfil.")
            return

        print("Llenando formulario de perfil...")

        # Bucle de verificación y corrección
        while True:
            # Verificar con el usuario si los datos son correctos
            print(f"Nombre ingresado: {self.data.get('first_name')} {self.data.get('last_name')}")
            print(f"Dirección: {self.data.get('address')}, {self.data.get('city')}, {self.data.get('state')}")

            if self.ask_confirmation("¿Son correctos estos datos en el formulario?"):
                print("Datos de perfil confirmados.")
                break
            else:
                self.redo_form()
                print("Reintentando llenado con nuevos datos...")

    def redo_form(self):
        """
        Permite al usuario reingresar datos manualmente si la automatización no es satisfactoria.
        """
        print("\n--- Corrección Manual de Datos ---")
        fields_to_update = ["first_name", "last_name", "address", "city", "state", "zip_code", "income"]

        for field in fields_to_update:
            current_value = self.data.get(field)
            new_value = input(f"Ingrese valor para '{field}' (Actual: {current_value}): ").strip()
            if new_value:
                self.data[field] = new_value

        print("Datos actualizados en memoria (y simuladamente en el formulario).")

    def verify_plans(self):
        """
        Verifica planes disponibles basados en las preferencias.
        """
        print("\nVerificando planes disponibles...")
        if not self.ask_confirmation("Buscar planes que coincidan con las necesidades"):
            return

        preferences = self.data.get("plan_preferences", {})
        print(f"Buscando planes con Nivel: {preferences.get('metal_level')} y Prima Máxima: ${preferences.get('max_premium')}")

        print("Búsqueda de planes completada.")

    def run(self):
        """
        Ejecuta el flujo principal del bot con menú de selección.
        """
        print("\n=== Bot de Automatización CuidadoDeSalud.gov ===")
        print("1. Iniciar Sesión (Login)")
        print("2. Crear Nueva Cuenta")

        choice = input("\nSeleccione una opción (1 o 2): ").strip()

        self.start_driver()

        try:
            if choice == '1':
                self.login()
                # Después del login, típicamente se llena el perfil o verifica planes
                self.fill_profile()
                self.verify_plans()
            elif choice == '2':
                self.create_account()
                # Después de crear cuenta, ¿quizás llenar perfil?
                if self.ask_confirmation("¿Desea continuar al llenado de perfil con los datos de usuario existente?"):
                     self.fill_profile()
                     self.verify_plans()
            else:
                print("Opción no válida. Saliendo.")

            print("\nProceso finalizado con éxito.")

        except KeyboardInterrupt:
            print("\nEjecución interrumpida por el usuario.")
        except Exception as e:
            print(f"\nOcurrió un error inesperado: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                print("Navegador cerrado.")

if __name__ == "__main__":
    bot = HealthCareBot("data/namefull.txt")
    bot.run()
