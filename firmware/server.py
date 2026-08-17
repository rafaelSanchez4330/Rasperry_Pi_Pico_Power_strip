"""Servidor HTTP mínimo y router de la API REST.

Separado de la lógica de negocio: recibe el OutletManager y una función que
reporta el estado de red. Sirve la API bajo /api/ y los archivos estáticos de
la carpeta web/ para el resto de rutas.
"""

import socket

try:
    import ujson as json
except ImportError:
    import json

import config


# Códigos de estado HTTP usados por el servidor.
STATUS_TEXT = {
    200: "OK",
    400: "Bad Request",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
}

# Tipos MIME por extensión para servir archivos estáticos.
CONTENT_TYPES = {
    "html": "text/html; charset=utf-8",
    "css": "text/css; charset=utf-8",
    "js": "application/javascript; charset=utf-8",
    "json": "application/json",
    "png": "image/png",
    "ico": "image/x-icon",
}


class Request:
    """Representa una solicitud HTTP parseada."""

    def __init__(self, method, path, query, headers, body):
        self.method = method
        self.path = path
        self.query = query
        self.headers = headers
        self.body = body

    @classmethod
    def parse(cls, raw):
        """Parsea los bytes crudos de una solicitud HTTP.

        Lanza ValueError si la solicitud está malformada.
        """
        text = raw.decode("utf-8")
        head, _, body = text.partition("\r\n\r\n")
        lines = head.split("\r\n")
        if not lines or not lines[0]:
            raise ValueError("Solicitud vacía")

        parts = lines[0].split(" ")
        if len(parts) < 2:
            raise ValueError("Línea de solicitud inválida")
        method, target = parts[0], parts[1]

        path, _, query_string = target.partition("?")
        query = cls._parse_query(query_string)

        headers = {}
        for line in lines[1:]:
            if ":" in line:
                key, _, value = line.partition(":")
                headers[key.strip().lower()] = value.strip()

        return cls(method, path, query, headers, body)

    @staticmethod
    def _parse_query(query_string):
        params = {}
        if not query_string:
            return params
        for pair in query_string.split("&"):
            key, _, value = pair.partition("=")
            if key:
                params[key] = value
        return params

    def json(self):
        """Cuerpo parseado como JSON, o None si está vacío/ inválido."""
        if not self.body:
            return None
        try:
            return json.loads(self.body)
        except Exception:
            return None


class HTTPServer:
    def __init__(self, outlet_manager, status_provider=None, port=None):
        self.outlets = outlet_manager
        # Función opcional que devuelve un dict con estado de red (ip, online).
        self.status_provider = status_provider
        self.port = port if port is not None else config.HTTP_PORT
        self._sock = None

    # --- Ciclo de vida del socket ------------------------------------------
    def start(self):
        addr = socket.getaddrinfo("0.0.0.0", self.port)[0][-1]
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(addr)
        self._sock.listen(5)
        print("Servidor HTTP escuchando en el puerto {}".format(self.port))

    def serve_forever(self):
        if self._sock is None:
            self.start()
        while True:
            try:
                conn, addr = self._sock.accept()
                self._handle_connection(conn)
            except Exception as exc:  # noqa: BLE001 - el servidor no debe morir
                print("Error en el bucle del servidor:", exc)

    def stop(self):
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    # --- Manejo de una conexión --------------------------------------------
    def _handle_connection(self, conn):
        try:
            raw = conn.recv(2048)
            if not raw:
                return
            try:
                request = Request.parse(raw)
            except ValueError:
                self._send(conn, 400, "text/plain", "Bad Request")
                return
            self._route(conn, request)
        except Exception as exc:  # noqa: BLE001
            print("Error al manejar la conexión:", exc)
            try:
                self._send_json(conn, 500, {"error": "internal_error"})
            except Exception:
                pass
        finally:
            try:
                conn.close()
            except Exception:
                pass

    # --- Enrutamiento -------------------------------------------------------
    def _route(self, conn, request):
        if request.path.startswith("/api/"):
            self._route_api(conn, request)
        else:
            self._serve_static(conn, request)

    def _route_api(self, conn, request):
        segments = [s for s in request.path.split("/") if s]
        # segments[0] == "api"
        rest = segments[1:]

        if rest == ["status"] and request.method == "GET":
            status = self._status_provider_dict()
            status["project"] = config.PROJECT_NAME
            self._send_json(conn, 200, status)
            return

        if rest == ["outlets"] and request.method == "GET":
            self._send_json(conn, 200, self.outlets.to_dict())
            return

        if len(rest) == 2 and rest[0] == "outlets" and request.method == "GET":
            outlet = self._lookup(rest[1])
            if outlet is None:
                self._send_json(conn, 404, {"error": "outlet_not_found"})
            else:
                self._send_json(conn, 200, outlet.to_dict())
            return

        # Acciones: POST /api/outlets/<id|all>/<on|off|toggle>
        if len(rest) == 3 and rest[0] == "outlets" and request.method == "POST":
            target, action = rest[1], rest[2]
            self._handle_action(conn, target, action)
            return

        if request.method not in ("GET", "POST"):
            self._send_json(conn, 405, {"error": "method_not_allowed"})
            return

        self._send_json(conn, 404, {"error": "not_found"})

    def _handle_action(self, conn, target, action):
        if action not in ("on", "off", "toggle"):
            self._send_json(conn, 400, {"error": "invalid_action"})
            return

        if target == "all":
            if action == "on":
                self.outlets.all_on()
            elif action == "off":
                self.outlets.all_off()
            else:
                self._send_json(conn, 400, {"error": "toggle_all_not_supported"})
                return
            self._send_json(conn, 200, self.outlets.to_dict())
            return

        outlet = self._lookup(target)
        if outlet is None:
            self._send_json(conn, 404, {"error": "outlet_not_found"})
            return

        if action == "on":
            outlet.turn_on()
        elif action == "off":
            outlet.turn_off()
        else:
            outlet.toggle()
        self._send_json(conn, 200, outlet.to_dict())

    def _lookup(self, raw_id):
        try:
            outlet_id = int(raw_id)
        except (ValueError, TypeError):
            return None
        return self.outlets.get(outlet_id)

    # --- Estáticos ----------------------------------------------------------
    def _serve_static(self, conn, request):
        path = request.path
        if path == "/" or path == "":
            path = "/index.html"
        # Evita traversal fuera de la carpeta web.
        if ".." in path:
            self._send(conn, 400, "text/plain", "Bad Request")
            return

        filename = config.WEB_ROOT + path
        ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
        content_type = CONTENT_TYPES.get(ext, "application/octet-stream")

        try:
            with open(filename, "rb") as fh:
                body = fh.read()
        except OSError:
            self._send(conn, 404, "text/plain", "Not Found")
            return

        self._send_bytes(conn, 200, content_type, body)

    # --- Helpers de respuesta ----------------------------------------------
    def _status_provider_dict(self):
        if self.status_provider is None:
            return {}
        try:
            return self.status_provider() or {}
        except Exception:
            return {}

    def _send_json(self, conn, status, payload):
        body = json.dumps(payload)
        self._send(conn, status, "application/json", body)

    def _send(self, conn, status, content_type, body):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self._send_bytes(conn, status, content_type, body)

    def _send_bytes(self, conn, status, content_type, body):
        reason = STATUS_TEXT.get(status, "OK")
        headers = (
            "HTTP/1.1 {} {}\r\n"
            "Content-Type: {}\r\n"
            "Content-Length: {}\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).format(status, reason, content_type, len(body))
        conn.sendall(headers.encode("utf-8"))
        conn.sendall(body)
