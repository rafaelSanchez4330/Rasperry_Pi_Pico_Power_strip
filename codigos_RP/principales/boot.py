import utime
from machine import Pin
import network
import gc

led = Pin('LED', Pin.OUT)
led.on()
utime.sleep(1)
# Define cuántos segundos esperar
max_wait = 10 

ssid = 'RedPrueba'
password = '12345678'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

print("Conectando a WiFi...")
while max_wait > 0:
    if station.isconnected():
        break # ¡Éxito! Salir del bucle
        
    max_wait -= 1
    print('.')
    utime.sleep(1) # Esperar 1 segundo

# Comprobar si salimos por éxito o por timeout
if station.isconnected():
    print('\n¡Conexión exitosa!')
    print(station.ifconfig())
    led = Pin('LED', Pin.OUT)
    led.on()
else:
    print('\nFallo al conectar.')

gc.collect()



