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
    def __init__(self, data_file):
        """
        Inicializa el bot con la ruta del archivo de datos.
        """
        self.data_file = data_file
        self.data = self.load_data()
        self.driver = None

    def load_data(self):
        """
        Carga los datos del perfil desde el archivo JSON.
        """
        if not os.path.exists(self.data_file):
            print(f"Error: El archivo {self.data_file} no existe.")
            return None

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print("Datos cargados exitosamente.")
            return data
        except json.JSONDecodeError:
            print("Error: El archivo de datos no tiene un formato JSON válido.")
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

    def login(self):
        """
        Navega a la página de inicio de sesión y simula el login.
        Nota: Esto es una simulación ya que no tenemos credenciales reales válidas.
        """
        if not self.driver:
            print("El navegador no está iniciado.")
            return

        login_url = "https://www.cuidadodesalud.gov/login"
        print(f"Navegando a {login_url}...")
        self.driver.get(login_url)

        if not self.ask_confirmation("Iniciar sesión con las credenciales cargadas"):
            return

        try:
            # Esperar a que los campos de usuario y contraseña estén presentes
            # Estos selectores son hipotéticos y deben actualizarse con los reales del sitio
            # WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "username-field-id")))

            print(f"Ingresando usuario: {self.data.get('username')}")
            # user_field = self.driver.find_element(By.ID, "username-field-id")
            # user_field.send_keys(self.data.get('username'))

            print("Ingresando contraseña...")
            # pass_field = self.driver.find_element(By.ID, "password-field-id")
            # pass_field.send_keys(self.data.get('password'))

            # submit_button = self.driver.find_element(By.ID, "login-button-id")
            # submit_button.click()

            print("Login simulado completado (acciones de Selenium comentadas por seguridad/falta de selectores reales).")
            time.sleep(2) # Simular tiempo de carga

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
        # Aquí iría la lógica para interactuar con los campos del formulario
        # Ejemplo:
        # self.driver.find_element(By.NAME, "firstName").send_keys(self.data.get("first_name"))
        # self.driver.find_element(By.NAME, "lastName").send_keys(self.data.get("last_name"))

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
                # Aquí se volvería a ejecutar el llenado del formulario en el navegador

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
                # Aquí también se podría actualizar el campo en el navegador en tiempo real
                # self.driver.find_element(By.NAME, field_map[field]).clear()
                # self.driver.find_element(By.NAME, field_map[field]).send_keys(new_value)

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

        # Lógica de scraping/navegación para filtrar planes
        # ...

        print("Búsqueda de planes completada.")

    def run(self):
        """
        Ejecuta el flujo principal del bot.
        """
        if not self.data:
            print("No se pueden ejecutar las acciones sin datos.")
            return

        self.start_driver()

        try:
            self.login()
            self.fill_profile()
            self.verify_plans()

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
