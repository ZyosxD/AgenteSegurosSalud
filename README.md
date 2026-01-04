# 🏥 Bot de Automatización para CuidadoDeSalud.gov

¡Bienvenido! Este repositorio contiene un bot en Python diseñado para automatizar interacciones con el sitio web [CuidadoDeSalud.gov](https://www.cuidadodesalud.gov/). 🤖

El bot está diseñado para ayudar a:
1.  **Crear cuentas nuevas** (Registro).
2.  **Iniciar sesión** con verificación de dos pasos (2FA).
3.  **Llenar perfiles** automáticamente.
4.  **Verificar planes de salud** disponibles.

Todo basado en datos predefinidos para ahorrar tiempo y asegurar precisión. ✨

---

## 🚀 Características Nuevas

*   **🆕 Creación de Cuenta Automática**: Usa datos de `data/newuser.txt` para registrar nuevos usuarios.
*   **🔐 Soporte para 2FA**: Permite ingresar códigos de verificación (SMS/Email) manualmente desde la terminal para continuar el flujo automatizado.
*   **🔀 Menú Interactivo**: Elige fácilmente entre "Iniciar Sesión" o "Crear Cuenta" al inicio.

---

## 🛠️ Instalación y Configuración

Sigue estos pasos para poner en marcha tu bot.

### 1. Requisitos Previos

Asegúrate de tener instalado **Python 3.x**. También necesitarás el navegador **Google Chrome**.

### 2. Clonar el Repositorio

Descarga este código a tu máquina local.

```bash
git clone <URL_DEL_REPO>
cd <NOMBRE_DEL_DIRECTORIO>
```

### 3. Instalar Dependencias 📦

Instala las librerías necesarias de Python ejecutando:

```bash
pip install selenium webdriver-manager
```

### 4. Preparar tus Datos 📝

El bot usa dos archivos de datos en la carpeta `data/`.

#### A. Datos de Registro (`data/newuser.txt`)
Para crear una cuenta nueva. Copia este JSON y edítalo:

```json
{
    "first_name": "Juan",
    "last_name": "Perez",
    "email": "juan.perez@example.com",
    "password": "PasswordSeguro123!",
    "security_questions": [
        {
            "question": "Pregunta 1",
            "answer": "Respuesta 1"
        },
        {
            "question": "Pregunta 2",
            "answer": "Respuesta 2"
        },
        {
            "question": "Pregunta 3",
            "answer": "Respuesta 3"
        }
    ]
}
```

#### B. Datos de Perfil (`data/namefull.txt`)
Para llenar el perfil y buscar planes.

```json
{
    "username": "tu_usuario",
    "password": "tu_contraseña",
    "first_name": "Juan",
    "last_name": "Perez",
    "dob": "01/01/1980",
    "address": "123 Calle Principal",
    "city": "Miami",
    "state": "FL",
    "zip_code": "33101",
    "income": "30000",
    "plan_preferences": {
        "max_premium": 100,
        "metal_level": "Silver"
    }
}
```

> **⚠️ Nota de Seguridad:** Nunca compartas estos archivos, ya que contienen información personal sensible.

#### C. Base de Datos de Usuarios (`data/user_database.json`)
Este archivo se genera automáticamente.
*   **Propósito**: Almacenar un registro de todos los usuarios que han creado una cuenta exitosamente con el bot.
*   **Contenido**: Incluye nombre, correo, contraseña, preguntas de seguridad y fecha de registro.
*   **Uso**: Sirve como respaldo para recuperar datos de acceso si se olvidan.

---

## 🛑 Sistema de Registro y Recuperación de Errores

Este bot incluye un **LOG magistral** que registra cada paso de la actividad en el archivo `bot_activity.log` y en la consola. Esto permite una transparencia total sobre lo que el bot está haciendo.

### ¿Qué hacer si ocurre un error?

Si el bot encuentra un problema que no puede resolver automáticamente (por ejemplo, un elemento de la página cambió o falló la conexión), entrará en modo de **Solicitud de Ayuda Humana**:

1.  **Alerta**: Verás un mensaje de error claro en la pantalla y en el log.
2.  **Acción Manual**: El bot pausará su ejecución. Deberás ir a la ventana del navegador y corregir el problema manualmente (ej. cerrar un popup, rellenar un campo difícil, refrescar la página).
3.  **Opciones de Recuperación**:
    *   Escribe `r` y presiona Enter para **Reintentar** el paso que falló.
    *   Escribe `c` y presiona Enter para **Continuar** e ignorar el error (útil si ya lo corregiste manualmente y el bot solo necesita seguir adelante).
    *   Escribe `exit` para cerrar el bot.

Esto asegura que ningún error pase desapercibido y que siempre tengas el control para desatascar al bot.

---

## ▶️ Cómo Usar el Bot

1.  Ejecuta el bot:
    ```bash
    python bot.py
    ```

2.  **Selecciona una opción** del menú:
    ```
    === Bot de Automatización CuidadoDeSalud.gov ===
    1. Iniciar Sesión (Login)
    2. Crear Nueva Cuenta
    Seleccione una opción (1 o 2):
    ```

3.  **Sigue las instrucciones**:
    *   Confirma las acciones con `s` (sí).
    *   **Ingreso de Códigos (OTP)**: Cuando el bot llegue a la pantalla de verificación (ya sea al crear cuenta o al hacer login), te pedirá en la terminal que ingreses el código que te llegó al correo o celular. Escríbelo y presiona Enter para que el bot continúe.

4.  **Modo de Corrección**: Si ves datos incorrectos en el llenado de formularios, el bot te permitirá corregirlos antes de continuar.

---

## 📁 Estructura del Proyecto

```
.
├── bot.py              # 🐍 Código principal actualizado
├── data/
│   ├── namefull.txt    # 📄 Datos de perfil y planes
│   └── newuser.txt     # 🆕 Datos para creación de cuenta
└── README.md           # 📖 Instrucciones actualizadas
```

---

## ⚠️ Aviso Legal

Este bot es una herramienta educativa. El uso de bots en sitios gubernamentales debe cumplir con sus términos de servicio. Úsalo bajo tu propia responsabilidad.
