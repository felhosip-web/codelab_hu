# -*- coding: utf-8 -*-
import unittest
import json
import urllib.request
import urllib.error
import time
from pathlib import Path

from core.plugin_system import PluginLoader
from core.engine import Engine
from core.rest_api import SecureRESTAPIServer, RESTConfig

class TestRESTAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plugin_loader = PluginLoader()
        cls.plugin_loader.load_all()
        cls.engine = Engine()

    def setUp(self):
        # Temp save paths for test
        self.server = SecureRESTAPIServer(
            config_path="saves/test_rest_config.json",
            keys_path="saves/test_api_keys.json",
            plugin_loader=self.plugin_loader,
            engine=self.engine
        )
        self.server.config.enabled = True
        self.server.config.host = "127.0.0.1"
        self.server.config.port = 8888
        self.server.config.require_api_key = True
        self.server.config.enable_read_endpoints = True
        self.server.config.enable_execute_endpoints = True

        # Create test keys
        self.read_key = self.server.create_key("read_key", permissions=["read"])
        self.exec_key = self.server.create_key("exec_key", permissions=["read", "execute"])

        self.server.start()
        time.sleep(0.1)  # wait for server thread to bind

    def tearDown(self):
        self.server.stop()
        for p in [Path("saves/test_rest_config.json"), Path("saves/test_api_keys.json")]:
            if p.exists():
                p.unlink()

    def _make_request(self, path, method="GET", body=None, headers=None):
        url = f"http://127.0.0.1:8888{path}"
        req_headers = headers or {}
        data = json.dumps(body).encode("utf-8") if body is not None else None

        if body is not None and "Content-Type" not in req_headers:
            req_headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                res_body = resp.read().decode("utf-8")
                return resp.status, json.loads(res_body)
        except urllib.error.HTTPError as e:
            res_body = e.read().decode("utf-8")
            try:
                parsed = json.loads(res_body)
            except Exception:
                parsed = res_body
            return e.code, parsed

    def test_get_plugins_unauthorized(self):
        status, res = self._make_request("/api/v2/plugins")
        self.assertEqual(status, 403)
        self.assertIn("error", res)

    def test_get_plugins_success(self):
        headers = {"X-API-Key": self.read_key}
        status, res = self._make_request("/api/v2/plugins", headers=headers)
        self.assertEqual(status, 200)
        self.assertIn("plugins", res)
        self.assertIn("count", res)
        self.assertGreater(res["count"], 0)

        first_plugin = res["plugins"][0]
        for key in ["id", "name", "version", "type", "time_complexity", "space_complexity", "description"]:
            self.assertIn(key, first_plugin)

    def test_run_plugin_no_execute_permission(self):
        headers = {"X-API-Key": self.read_key}
        body = {"plugin_id": "bubble_sort", "array": [3, 1, 2]}
        status, res = self._make_request("/api/v2/run", method="POST", body=body, headers=headers)
        self.assertEqual(status, 403)

    def test_run_plugin_not_found(self):
        headers = {"X-API-Key": self.exec_key}
        body = {"plugin_id": "non_existent_plugin_xyz"}
        status, res = self._make_request("/api/v2/run", method="POST", body=body, headers=headers)
        self.assertEqual(status, 404)

    def test_run_plugin_success(self):
        headers = {"X-API-Key": self.exec_key}
        body = {"plugin_id": "bubble_sort", "array": [5, 2, 8, 1]}
        status, res = self._make_request("/api/v2/run", method="POST", body=body, headers=headers)
        self.assertEqual(status, 200)
        self.assertEqual(res["plugin_id"], "bubble_sort")
        self.assertEqual(res["array"], [5, 2, 8, 1])
        self.assertIn("steps", res)
        self.assertGreater(len(res["steps"]), 0)
        self.assertLessEqual(len(res["steps"]), 200)

if __name__ == "__main__":
    unittest.main()
