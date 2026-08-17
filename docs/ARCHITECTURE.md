# Arquitectura

El firmware está dividido en módulos con una única responsabilidad cada uno,
de modo que la lógica de red, la de hardware y la del servidor estén
desacopladas.

## Flujo de arranque

```
Pico enciende
     |
boot.py (mínimo, gc.collect)
     |
main.py
     |-- carga config.py
     |-- WiFiManager.connect()   (wifi.py)
     |-- OutletManager.from_config()  (outlets.py)
     |-- HTTPServer.serve_forever()   (server.py)
```

## Módulos

- **config.py** — Valores no sensibles: pines GPIO, número de contactos,
  nombres por defecto, puerto HTTP, timeouts y lógica de relé (active-low).
- **secrets.py** — Solo credenciales Wi-Fi. Ignorado por git.
- **wifi.py** — `WiFiManager`: activa la interfaz, conecta con timeout,
  expone IP y estado de conexión. Lanza `WiFiError` si falla.
- **outlets.py** — Capa de hardware. `Outlet` encapsula un relé
  (`turn_on/turn_off/toggle/is_on`) respetando active-low. `OutletManager`
  agrupa los contactos y ofrece operaciones globales y serialización a dict.
- **server.py** — `Request` parsea la solicitud HTTP (método, ruta, query,
  headers, body). `HTTPServer` crea el socket, enruta `/api/*` a la API REST
  y sirve los archivos estáticos de `web/`. Respuestas en bytes, headers con
  `\r\n` y códigos 200/400/404/405/500.

## Capa web

`web/app.js` consulta la API con `fetch()` y refresca el estado cada pocos
segundos. No usa frameworks; solo DOM y `fetch`.

## Pruebas

`tests/` incluye un stub de `machine.Pin` (`tests/stubs/machine.py`) para
ejecutar la lógica de `outlets.py` y el parser de `server.py` en una PC sin
depender del hardware ni de MicroPython.
