import socket

# --- Eliminamos toda la lógica de los LEDs y RGB ---

# Función web_page() simplificada
def web_page():
    html = """
            <html>
            <head>
                <title>Test Page</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
                <h1>Hola, esto es una prueba</h1>
            </body>
            </html>
           """
    return html

# --- Configuración del socket (Esto es lo que fallará) ---
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

print("Servidor escuchando en el puerto 80...")

while True:
    try:
        conn, addr = s.accept()
        print('Conexión recibida de %s' % str(addr))
        request = conn.recv(1024)
        
        # --- Eliminamos toda la lógica de los botones ---
        
        # Servimos la página simplificada
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
        
    except Exception as e:
        print(e)
        # conn.close() # Opcional: cerrar conexión si falla
