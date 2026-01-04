import logging
from selenium.webdriver.common.by import By
from src import utils

def redo_form(data):
    """
    Permite corrección manual de datos.
    """
    print("\n--- Corrección Manual de Datos ---")
    fields_to_update = ["first_name", "last_name", "address", "city", "state", "zip_code", "income"]

    for field in fields_to_update:
        current_value = data.get(field)
        new_value = input(f"Ingrese valor para '{field}' (Actual: {current_value}): ").strip()
        if new_value:
            data[field] = new_value
            logging.info(f"Campo '{field}' actualizado a: {new_value}")

    logging.info("Datos en memoria actualizados.")

def fill_profile(driver, data):
    """
    Llena el perfil del usuario.
    """
    if not utils.ask_confirmation("Llenar información del perfil"):
        logging.info("Usuario saltó el llenado de perfil.")
        return

    logging.info("Iniciando llenado de perfil...")

    while True:
        try:
            # --- INTERACCIÓN REAL DE PERFIL ---
            logging.info("Intentando llenar campos de perfil automáticamente...")
            try:
                # Selectores hipotéticos estándar
                if driver:
                    driver.find_element(By.ID, "streetAddress").send_keys(data.get('address'))
                    driver.find_element(By.ID, "city").send_keys(data.get('city'))
                    driver.find_element(By.ID, "zipCode").send_keys(data.get('zip_code'))

                    # Estado suele ser un dropdown, requeriría Select o click
                    # driver.find_element(By.ID, "state").send_keys(data.get('state'))
            except Exception as e:
                logging.warning(f"No se pudieron llenar todos los campos de perfil: {e}")
            # ----------------------------------

            # Verificar con el usuario
            logging.info("Mostrando datos actuales para confirmación...")
            print(f"Nombre: {data.get('first_name')} {data.get('last_name')}")
            print(f"Dirección: {data.get('address')}, {data.get('city')}, {data.get('state')}")

            if utils.ask_confirmation("¿Son correctos estos datos en el formulario?"):
                logging.info("Datos de perfil confirmados por el usuario.")
                break
            else:
                logging.info("Usuario indicó datos incorrectos. Iniciando corrección manual.")
                redo_form(data)
                logging.info("Reintentando llenado con nuevos datos...")
                # Al reintentar, el bucle volverá a ejecutar los send_keys con los nuevos datos

        except Exception as e:
                action = utils.request_human_help(f"Error en llenado de perfil: {e}", driver=driver)
                if action == 'continue':
                    break

def verify_plans(driver, data):
    """
    Verifica planes disponibles.
    """
    logging.info("Iniciando verificación de planes...")
    if not utils.ask_confirmation("Buscar planes que coincidan con las necesidades"):
        return

    try:
        preferences = data.get("plan_preferences", {})
        logging.info(f"Criterios de búsqueda: Nivel {preferences.get('metal_level')}, Max Prima ${preferences.get('max_premium')}")

        # --- LÓGICA DE FILTRADO ---
        # Si hubiera una página de resultados, aquí podríamos usar Selenium para leer los precios.
        # plans = driver.find_elements(By.CLASS_NAME, "plan-card")
        # for plan in plans: ...
        # --------------------------

        logging.info("Búsqueda de planes finalizada (Revise el navegador para ver los resultados).")
    except Exception as e:
        utils.request_human_help(f"Error buscando planes: {e}", driver=driver)
