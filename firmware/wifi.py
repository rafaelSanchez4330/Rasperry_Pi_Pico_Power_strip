"""Administración de la conexión Wi-Fi, desacoplada de la lógica principal."""

import time

import network

import config


class WiFiError(Exception):
    """Error al establecer la conexión Wi-Fi."""


class WiFiManager:
    def __init__(self, ssid, password, timeout=None, retry_delay=None):
        self.ssid = ssid
        self.password = password
        self.timeout = timeout if timeout is not None else config.WIFI_TIMEOUT
        self.retry_delay = (
            retry_delay if retry_delay is not None else config.WIFI_RETRY_DELAY
        )
        self._station = network.WLAN(network.STA_IF)

    def connect(self):
        """Activa la interfaz e intenta conectarse dentro del timeout.

        Devuelve la IP asignada o lanza WiFiError si falla.
        """
        self._station.active(True)

        if not self._station.isconnected():
            self._station.connect(self.ssid, self.password)

        waited = 0
        while waited < self.timeout:
            if self._station.isconnected():
                return self.ip()
            time.sleep(self.retry_delay)
            waited += self.retry_delay

        if self._station.isconnected():
            return self.ip()

        raise WiFiError(
            "No se pudo conectar a '{}' en {}s".format(self.ssid, self.timeout)
        )

    def is_connected(self):
        return self._station.isconnected()

    def ip(self):
        """Dirección IP asignada, o None si no hay conexión."""
        if not self._station.isconnected():
            return None
        return self._station.ifconfig()[0]

    def disconnect(self):
        try:
            self._station.disconnect()
        except Exception:
            pass
