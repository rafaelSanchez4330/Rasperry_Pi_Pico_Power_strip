"""Punto de entrada de la aplicación.

Orquesta el arranque:
    config -> Wi-Fi -> contactos -> servidor HTTP
"""

import gc

from machine import Pin

import config
from outlets import OutletManager
from server import HTTPServer
from wifi import WiFiManager, WiFiError

try:
    import secrets
except ImportError:
    secrets = None


def _connect_wifi():
    if secrets is None:
        print("No se encontró secrets.py. Copia secrets.example.py a secrets.py.")
        return None
    wifi = WiFiManager(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    try:
        ip = wifi.connect()
        print("Wi-Fi conectado. IP:", ip)
        return wifi
    except WiFiError as exc:
        print("Fallo de Wi-Fi:", exc)
        return None


def main():
    led = Pin("LED", Pin.OUT)
    led.off()

    outlets = OutletManager.from_config()
    print("Contactos inicializados:", config.OUTLET_COUNT)

    wifi = _connect_wifi()
    if wifi is not None and wifi.is_connected():
        led.on()

    def status_provider():
        connected = wifi is not None and wifi.is_connected()
        return {
            "online": connected,
            "ip": wifi.ip() if connected else None,
        }

    gc.collect()

    server = HTTPServer(outlets, status_provider=status_provider)
    server.start()
    server.serve_forever()


if __name__ == "__main__":
    main()
