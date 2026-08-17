"""Stub de `machine` para ejecutar la lógica del firmware en una PC.

Reemplaza la clase Pin de MicroPython con una versión que solo guarda su
valor en memoria, permitiendo probar outlets.py sin hardware.
"""


class Pin:
    OUT = "OUT"
    IN = "IN"

    def __init__(self, gpio, mode=None):
        self.gpio = gpio
        self.mode = mode
        self._value = 0

    def value(self, val=None):
        if val is None:
            return self._value
        self._value = int(val)
        return None

    def on(self):
        self._value = 1

    def off(self):
        self._value = 0
