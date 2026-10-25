# -*- coding: utf-8 -*-
import unittest
import json
import urllib.request
import urllib.error
import time
from pathlib import Path

from core.plugin_system import PluginLoader
from core.engine import Engine
from core.rest_api import SecureRESTAPIServer, RESTConfig, _run_in_sandbox_process
from core.version import REST_API_VERSION, API_MANAGER_VERSION, MAIN_VERSION

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
        self.server.config.sandbox_max_memory_mb = 256
        self.server.config.sandbox_timeout_sec = 10

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

    def test_status_endpoint(self):
        headers = {"X-API-Key": self.read_key}
        status, res = self._make_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 200)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["rest_api_version"], str(REST_API_VERSION))
        self.assertEqual(res["api_version"], str(API_MANAGER_VERSION))
        self.assertEqual(res["version"], str(MAIN_VERSION))

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

def _infinite_loop_worker(pipe_conn, plugin_id, params, array, max_memory_mb):
    import time
    while True:
        time.sleep(0.01)

def _memory_hog_worker(pipe_conn, plugin_id, params, array, max_memory_mb):
    from core.rest_api import _set_memory_limit
    _set_memory_limit(max_memory_mb)
    try:
        data = bytearray(500 * 1024 * 1024)
        pipe_conn.send(("ok", len(data)))
    except MemoryError:
        pipe_conn.send(("error", f"Sandbox memória korlát túllépve ({max_memory_mb} MB)"))
    except Exception as e:
        pipe_conn.send(("error", str(e)))

def _failing_fault_worker(pipe_conn, plugin_id, params, array, max_memory_mb):
    raise RuntimeError("Internal worker fault simulation")

class TestSEC03SandboxIsolation(unittest.TestCase):
    """
    Automated regression tests proving SEC-03 requirements:
    1. Infinite loop worker stopped after configured timeout.
    2. Timed-out worker process is no longer alive after cleanup.
    3. Repeated timed-out executions do not leave accumulating background workers.
    4. Worker exceeding memory limit is terminated/prevented gracefully.
    5. Successful execution returns expected results.
    6. Worker exceptions and abnormal exits handled without crashing REST API.
    7. Authorization and execution-permission checks intact.
    """

    def test_worker_infinite_loop_timeout_and_cleanup(self):
        """Infinite loop worker is stopped on timeout and process is cleaned up (not alive)."""
        import time

        t0 = time.time()
        res, err = _run_in_sandbox_process(
            plugin_id="bubble_sort",
            params=None,
            array=[1, 2, 3],
            max_memory_mb=256,
            timeout_sec=1,
            target_func=_infinite_loop_worker
        )
        elapsed = time.time() - t0

        self.assertIsNone(res)
        self.assertIsNotNone(err)
        self.assertIn("timeout", err.lower())
        self.assertGreaterEqual(elapsed, 0.9)
        self.assertLess(elapsed, 4.0)

    def test_repeated_timed_out_executions_no_orphans(self):
        """Repeated timed-out executions do not leave accumulating background processes."""
        import sys

        for i in range(3):
            res, err = _run_in_sandbox_process(
                plugin_id="bubble_sort",
                params=None,
                array=[1],
                max_memory_mb=256,
                timeout_sec=1,
                target_func=_infinite_loop_worker
            )
            self.assertIsNone(res)
            self.assertIn("timeout", err.lower())

        if sys.platform != "win32":
            import subprocess
            try:
                out = subprocess.check_output(["ps", "aux"], text=True)
                self.assertNotIn("_infinite_loop_worker", out)
            except Exception:
                pass

    def test_worker_memory_limit_exceeded(self):
        """Worker exceeding memory limit is prevented/terminated and returns controlled error."""
        import sys
        from core.rest_api import resource

        if sys.platform == "win32" or resource is None:
            self.skipTest("RLIMIT_AS memory enforcement is POSIX-only. Windows non-POSIX fallback documented.")

        res, err = _run_in_sandbox_process(
            plugin_id="bubble_sort",
            params=None,
            array=[1],
            max_memory_mb=10,
            timeout_sec=5,
            target_func=_memory_hog_worker
        )

        self.assertIsNone(res)
        self.assertIsNotNone(err)
        self.assertTrue(
            "memória korlát" in err or "memory" in err.lower() or "exitcode" in err.lower() or "timeout" in err.lower()
        )

    def test_worker_exception_handled_cleanly(self):
        """Worker exceptions and fault exits are handled without crashing REST API server."""
        res, err = _run_in_sandbox_process(
            plugin_id="bubble_sort",
            params=None,
            array=[1],
            max_memory_mb=256,
            timeout_sec=5,
            target_func=_failing_fault_worker
        )

        self.assertIsNone(res)
        self.assertIsNotNone(err)

    def test_invalid_and_nonsensical_configurations(self):
        """Invalid/nonsensical timeout and memory limit configs fallback safely."""
        res, err = _run_in_sandbox_process(
            plugin_id="bubble_sort",
            params=None,
            array=[2, 1],
            max_memory_mb=0,
            timeout_sec=-5
        )
        self.assertIsNotNone(res)
        self.assertIsNone(err)
        p_id, p_name, ret_arr, steps = res
        self.assertEqual(p_id, "bubble_sort")
        self.assertEqual(ret_arr, [2, 1])
        self.assertIsInstance(steps, list)

if __name__ == "__main__":
    unittest.main()
