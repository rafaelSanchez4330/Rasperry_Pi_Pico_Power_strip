"""Configura sys.path para que los tests importen el firmware en una PC.

Añade el stub de `machine` y la carpeta `firmware/` al path de importación.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)

for path in (os.path.join(_HERE, "stubs"), os.path.join(_ROOT, "firmware")):
    if path not in sys.path:
        sys.path.insert(0, path)
