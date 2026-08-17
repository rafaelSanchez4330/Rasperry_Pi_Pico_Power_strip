# boot.py se ejecuta automáticamente al encender el Pico, antes de main.py.
# Lo mantenemos mínimo: todo el arranque de la aplicación vive en main.py.

import gc

gc.collect()
