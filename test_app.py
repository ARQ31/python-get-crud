import json
import os
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import app


class BackendAPITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        app.DATA_FILE = Path(cls.temp_dir.name) / "messages.json"
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), app.APIHandler)
        cls.port = cls.server.server_port
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.temp_dir.cleanup()

    def setUp(self):
        if app.DATA_FILE.exists():
            app.DATA_FILE.unlink()

    def _request(self, method, path, payload=None):
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = Request(f"{self.base_url}{path}", data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=5) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except HTTPError as err:
            return err.code, json.loads(err.read().decode("utf-8"))

    def test_health_endpoint(self):
        status, body = self._request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body.get("status"), "active")
        self.assertEqual(body.get("service"), "Backend API")

    def test_post_message_valid(self):
        status, body = self._request("POST", "/messages", {"message": "Automated test message"})
        self.assertEqual(status, 201)
        self.assertEqual(body.get("status"), "created")
        self.assertIn("created_at", body.get("message", {}))
        self.assertEqual(body["message"]["message"], "Automated test message")

    def test_post_message_empty_validation(self):
        status, body = self._request("POST", "/messages", {"message": "   "})
        self.assertEqual(status, 400)
        self.assertEqual(body.get("error"), "message must not be empty")

    def test_post_message_too_long_validation(self):
        status, body = self._request("POST", "/messages", {"message": "x" * 501})
        self.assertEqual(status, 400)
        self.assertEqual(body.get("error"), "message must be 500 characters or fewer")


if __name__ == "__main__":
    unittest.main(verbosity=2)

