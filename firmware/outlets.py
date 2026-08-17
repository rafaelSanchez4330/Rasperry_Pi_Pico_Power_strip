"""Capa de hardware: control de los relés del multicontacto.

Toda la interacción con GPIO se centraliza aquí. El resto de la aplicación
(servidor, API) trabaja con estas clases y nunca toca los pines directamente.
"""

from machine import Pin

import config


class Outlet:
    """Representa un contacto individual controlado por un relé."""

    def __init__(self, outlet_id, name, gpio, active_low=True, default_on=False):
        self.id = outlet_id
        self.name = name
        self.gpio = gpio
        self.active_low = active_low
        self._pin = Pin(gpio, Pin.OUT)
        self._on = False
        # Aplicamos el estado inicial deseado sobre el hardware.
        if default_on:
            self.turn_on()
        else:
            self.turn_off()

    def _write(self):
        """Escribe el estado lógico actual en el pin, respetando active-low."""
        if self.active_low:
            self._pin.value(0 if self._on else 1)
        else:
            self._pin.value(1 if self._on else 0)

    def turn_on(self):
        self._on = True
        self._write()
        return self._on

    def turn_off(self):
        self._on = False
        self._write()
        return self._on

    def toggle(self):
        return self.turn_off() if self._on else self.turn_on()

    def is_on(self):
        return self._on

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "gpio": self.gpio,
            "state": "on" if self._on else "off",
        }


class OutletManager:
    """Colección de contactos con operaciones individuales y globales."""

    def __init__(self, outlets):
        # Diccionario id -> Outlet para acceso directo por ID.
        self._outlets = {}
        for outlet in outlets:
            self._outlets[outlet.id] = outlet

    @classmethod
    def from_config(cls):
        """Construye el gestor a partir de los valores de config.py."""
        outlets = []
        for index in range(config.OUTLET_COUNT):
            outlet_id = index + 1
            gpio = config.OUTLET_PINS[index]
            try:
                name = config.OUTLET_NAMES[index]
            except IndexError:
                name = "Contacto {}".format(outlet_id)
            outlets.append(
                Outlet(
                    outlet_id=outlet_id,
                    name=name,
                    gpio=gpio,
                    active_low=config.RELAY_ACTIVE_LOW,
                    default_on=config.OUTLET_DEFAULT_ON,
                )
            )
        return cls(outlets)

    def get(self, outlet_id):
        """Devuelve el contacto por ID o None si no existe."""
        return self._outlets.get(outlet_id)

    def all(self):
        """Lista de contactos ordenada por ID."""
        return [self._outlets[key] for key in sorted(self._outlets.keys())]

    def all_on(self):
        for outlet in self._outlets.values():
            outlet.turn_on()

    def all_off(self):
        for outlet in self._outlets.values():
            outlet.turn_off()

    def to_dict(self):
        return {"outlets": [outlet.to_dict() for outlet in self.all()]}
