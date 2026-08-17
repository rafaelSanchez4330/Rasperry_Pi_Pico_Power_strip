import unittest

import _bootstrap  # noqa: F401  (configura sys.path)

from server import Request


def build_request(method, target, headers=None, body=""):
    lines = ["{} {} HTTP/1.1".format(method, target)]
    headers = headers or {}
    for key, value in headers.items():
        lines.append("{}: {}".format(key, value))
    raw = "\r\n".join(lines) + "\r\n\r\n" + body
    return raw.encode("utf-8")


class RequestParseTests(unittest.TestCase):
    def test_basic_get(self):
        req = Request.parse(build_request("GET", "/api/outlets"))
        self.assertEqual(req.method, "GET")
        self.assertEqual(req.path, "/api/outlets")
        self.assertEqual(req.query, {})

    def test_query_string(self):
        req = Request.parse(build_request("GET", "/api/outlets?debug=1&x=2"))
        self.assertEqual(req.path, "/api/outlets")
        self.assertEqual(req.query, {"debug": "1", "x": "2"})

    def test_headers_lowercased(self):
        req = Request.parse(
            build_request("GET", "/", headers={"Content-Type": "application/json"})
        )
        self.assertEqual(req.headers.get("content-type"), "application/json")

    def test_json_body(self):
        req = Request.parse(
            build_request("POST", "/api/x", body='{"name": "Lamp"}')
        )
        self.assertEqual(req.json(), {"name": "Lamp"})

    def test_invalid_json_returns_none(self):
        req = Request.parse(build_request("POST", "/api/x", body="not-json"))
        self.assertIsNone(req.json())

    def test_empty_request_raises(self):
        with self.assertRaises(ValueError):
            Request.parse(b"")

    def test_malformed_request_line_raises(self):
        with self.assertRaises(ValueError):
            Request.parse(b"GARBAGE\r\n\r\n")


if __name__ == "__main__":
    unittest.main()
