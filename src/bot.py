import logging
from src import config, utils, driver, auth, profile

class HealthCareBot:
    def __init__(self):
        """
        Inicializa el bot.
        """
        utils.setup_logging()
        self.data_file = config.DATA_FILE
        self.new_user_file = config.NEW_USER_FILE

        self.data = utils.load_json_file(self.data_file)
        self.new_user_data = utils.load_json_file(self.new_user_file)
        self.driver = None

    def run(self):
        """
        Ejecuta el flujo principal.
        """
        print("\n=== Bot de Automatización CuidadoDeSalud.gov ===")
        print("1. Iniciar Sesión (Login)")
        print("2. Crear Nueva Cuenta")

        choice = input("\nSeleccione una opción (1 o 2): ").strip()

        self.driver = driver.start_driver()

        try:
            if choice == '1':
                logging.info("Modo seleccionado: Login")
                auth.login(self.driver, self.data)
                profile.fill_profile(self.driver, self.data)
                profile.verify_plans(self.driver, self.data)
            elif choice == '2':
                logging.info("Modo seleccionado: Crear Cuenta")
                auth.create_account(self.driver, self.new_user_data)
                if utils.ask_confirmation("¿Desea continuar al llenado de perfil con los datos de usuario existente?"):
                     profile.fill_profile(self.driver, self.data)
                     profile.verify_plans(self.driver, self.data)
            else:
                logging.warning("Opción de menú no válida.")
                print("Opción no válida. Saliendo.")

            logging.info("=== Proceso finalizado con éxito ===")

        except KeyboardInterrupt:
            logging.warning("Ejecución interrumpida por el usuario (KeyboardInterrupt).")
        except Exception as e:
            logging.critical(f"Error no manejado en el bucle principal: {e}")
            utils.request_human_help(f"Error crítico: {e}", driver=self.driver)
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("Navegador cerrado.")
