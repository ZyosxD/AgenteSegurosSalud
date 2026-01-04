import logging
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
            # Verificar con el usuario
            logging.info("Mostrando datos actuales para confirmación...")
            print(f"Nombre: {data.get('first_name')} {data.get('last_name')}")
            print(f"Dirección: {data.get('address')}")

            if utils.ask_confirmation("¿Son correctos estos datos en el formulario?"):
                logging.info("Datos de perfil confirmados por el usuario.")
                break
            else:
                logging.info("Usuario indicó datos incorrectos. Iniciando corrección manual.")
                redo_form(data)
                logging.info("Reintentando llenado con nuevos datos...")
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
        # ... scraping logic ...
        logging.info("Búsqueda de planes finalizada.")
    except Exception as e:
        utils.request_human_help(f"Error buscando planes: {e}", driver=driver)
