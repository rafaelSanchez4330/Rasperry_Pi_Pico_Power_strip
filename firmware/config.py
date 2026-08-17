# Configuración no sensible del proyecto.
# Las credenciales Wi-Fi NO van aquí, sino en secrets.py (ignorado por git).

# Número de contactos (relés) del multicontacto.
OUTLET_COUNT = 6

# Pines GPIO conectados a la entrada de cada módulo de relé.
# El orden corresponde al ID del contacto (índice + 1).
OUTLET_PINS = [2, 3, 4, 5, 6, 7]

# Nombres por defecto de cada contacto (usados si no hay override).
OUTLET_NAMES = [
    "Contacto 1",
    "Contacto 2",
    "Contacto 3",
    "Contacto 4",
    "Contacto 5",
    "Contacto 6",
]

# Muchos módulos de relé son activos en bajo: el pin en LOW enciende el relé.
# Si tu módulo es activo en alto, cambia esto a False.
RELAY_ACTIVE_LOW = True

# Estado en el que quedan los contactos al arrancar (False = apagados).
OUTLET_DEFAULT_ON = False

# Puerto del servidor HTTP.
HTTP_PORT = 80

# Segundos máximos de espera para conectar al Wi-Fi.
WIFI_TIMEOUT = 15

# Segundos entre reintentos de comprobación de conexión Wi-Fi.
WIFI_RETRY_DELAY = 1

# Nombre del proyecto mostrado en el dashboard.
PROJECT_NAME = "Smart Power Strip"

# Carpeta (en el filesystem del Pico) donde viven los archivos web estáticos.
WEB_ROOT = "web"
