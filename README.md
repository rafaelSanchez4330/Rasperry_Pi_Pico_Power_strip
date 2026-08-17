# Raspberry Pi Pico W — Smart Power Strip

Multicontacto inteligente basado en **Raspberry Pi Pico W** y **MicroPython**.
Permite encender y apagar de forma remota e independiente cada uno de los
contactos eléctricos mediante una interfaz web accesible desde la red local.

El controlador (tu navegador) y el dispositivo controlado (el Pico W) deben
estar conectados a la misma red Wi-Fi.

## Características

- Control independiente de **6 contactos** vía relés.
- Conexión Wi-Fi a la red local doméstica.
- **API REST** para consultar y controlar los contactos.
- **Dashboard web** (HTML/CSS/JS, sin frameworks) servido desde el propio Pico.
- Configuración separada del código y credenciales fuera del repositorio.
- Pruebas de la lógica ejecutables en una PC (sin hardware).

## Arquitectura

```
Frontend (web/)
     |
   HTTP
     |
  REST API  ---------> server.py
     |
Outlet Manager ------> outlets.py
     |
   GPIO
     |
  Relés
```

## Estructura del proyecto

```
firmware/
├── boot.py       # arranque mínimo del Pico
├── main.py       # orquesta: config -> wifi -> outlets -> server
├── config.py     # configuración no sensible (pines, nº contactos, puerto...)
├── wifi.py       # conexión Wi-Fi, timeout, IP, estado
├── outlets.py    # clase Outlet + OutletManager (capa de hardware)
└── server.py     # servidor HTTP + router de la API REST + estáticos

web/
├── index.html
├── style.css
└── app.js        # consume la API con fetch()

tests/            # pruebas de lógica pura (stub de machine.Pin)
docs/             # documentación técnica
secrets.example.py
```

## Configuración

1. Copia `secrets.example.py` como `secrets.py` y coloca tus credenciales:

   ```python
   WIFI_SSID = "MiRed"
   WIFI_PASSWORD = "MiPassword"
   ```

   `secrets.py` está en `.gitignore` y **no** se sube al repositorio.

2. Ajusta `firmware/config.py` según tu hardware:
   - `OUTLET_PINS`: pines GPIO conectados a cada relé.
   - `RELAY_ACTIVE_LOW`: `True` si tu módulo enciende con LOW (lo más común).
   - `OUTLET_NAMES`, `HTTP_PORT`, `WIFI_TIMEOUT`, etc.

## Instalación en el Pico W

Copia al sistema de archivos del Pico:

- El contenido de `firmware/` en la raíz (`boot.py`, `main.py`, `config.py`,
  `wifi.py`, `outlets.py`, `server.py`) y tu `secrets.py`.
- La carpeta `web/` en la raíz (el servidor la sirve desde `WEB_ROOT`).

Puedes usar [Thonny](https://thonny.org/) o `mpremote`. Al reiniciar, el Pico
se conecta al Wi-Fi, muestra su IP por consola y levanta el servidor. Abre
`http://<IP-del-Pico>/` en un navegador de la misma red.

## API REST

| Método | Ruta                          | Descripción                     |
|--------|-------------------------------|---------------------------------|
| GET    | `/api/status`                 | Estado de red (online, IP)      |
| GET    | `/api/outlets`                | Lista de todos los contactos    |
| GET    | `/api/outlets/<id>`           | Un contacto por ID              |
| POST   | `/api/outlets/<id>/on`        | Encender un contacto            |
| POST   | `/api/outlets/<id>/off`       | Apagar un contacto              |
| POST   | `/api/outlets/<id>/toggle`    | Alternar un contacto            |
| POST   | `/api/outlets/all/on`         | Encender todos                  |
| POST   | `/api/outlets/all/off`        | Apagar todos                    |

Ejemplo de respuesta de un contacto:

```json
{ "id": 1, "name": "Monitor", "gpio": 2, "state": "on" }
```

Lista de contactos:

```json
{
  "outlets": [
    { "id": 1, "name": "Contacto 1", "gpio": 2, "state": "on" },
    { "id": 2, "name": "Contacto 2", "gpio": 3, "state": "off" }
  ]
}
```

## Pruebas

Las pruebas de lógica corren en una PC usando un stub de `machine.Pin`:

```bash
python -m unittest discover -s tests -v
```

## Licencia

[MIT](LICENSE).
