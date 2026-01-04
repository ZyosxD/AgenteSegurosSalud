# 🏥 Bot de Automatización para CuidadoDeSalud.gov

¡Bienvenido! Este repositorio contiene un bot en Python diseñado para automatizar interacciones con el sitio web [CuidadoDeSalud.gov](https://www.cuidadodesalud.gov/). 🤖

El bot está diseñado para ayudar a completar perfiles, mantener sesiones activas y verificar planes de salud, todo basado en datos predefinidos, ahorrando tiempo y asegurando precisión. ✨

---

## 🚀 Características

*   **📄 Carga de Datos Automática**: Lee información personal desde un archivo local (`data/namefull.txt`).
*   **🔐 Inicio de Sesión Simulado**: Estructura lista para automatizar el login.
*   **📝 Llenado de Formularios**: Completa campos de perfil automáticamente.
*   **✅ Verificación Interactiva**: Pregunta al usuario antes de cada paso importante.
*   **🔄 Corrección de Errores**: Permite reingresar datos manualmente si algo no se ve bien.
*   **🔍 Verificación de Planes**: Busca planes basados en tus preferencias.

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

El bot necesita tus datos para funcionar.

1.  Crea una carpeta llamada `data` en la raíz del proyecto (si no existe).
2.  Dentro, crea un archivo llamado `namefull.txt` (o asegúrate de que exista).
3.  El formato debe ser **JSON**. Puedes copiar y pegar este ejemplo y modificarlo con tus datos reales:

**Archivo: `data/namefull.txt`**

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

> **⚠️ Nota de Seguridad:** Nunca compartas tu archivo `namefull.txt` con nadie, ya que contiene información personal sensible. Asegúrate de añadir `data/` a tu `.gitignore` si subes este código a un repositorio público.

---

## ▶️ Cómo Usar el Bot

Una vez configurado todo, ¡es hora de correr el bot!

1.  Abre tu terminal.
2.  Ejecuta el siguiente comando:

```bash
python bot.py
```

3.  **Sigue las instrucciones en pantalla**. El bot te preguntará antes de realizar acciones clave:

    *   `¿Desea proceder con: 'Iniciar sesión...'? (s/n)`
    *   Si respondes `s` (sí), el bot continuará.
    *   Si respondes `n` (no), se cancelará esa acción.

4.  **Modo de Corrección**: Si el bot llena un formulario incorrectamente, te permitirá corregir los valores escribiendo los nuevos en la terminal.

---

## 📁 Estructura del Proyecto

```
.
├── bot.py              # 🐍 El código principal del bot
├── data/
│   └── namefull.txt    # 📄 Tus datos personales (¡Mantenlo seguro!)
└── README.md           # 📖 Estas instrucciones
```

---

## ⚠️ Aviso Legal

Este bot es una herramienta educativa y de automatización. El uso de bots en sitios gubernamentales puede estar sujeto a términos y condiciones específicos. Úsalo bajo tu propia responsabilidad y asegúrate de cumplir con las normativas de [CuidadoDeSalud.gov](https://www.cuidadodesalud.gov/).

---

¡Esperamos que esta herramienta te sea de gran utilidad! 🙌 Si tienes dudas o mejoras, ¡no dudes en contribuir!
