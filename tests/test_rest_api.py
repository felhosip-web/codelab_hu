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
    ok, msg = _set_memory_limit(max_memory_mb)
    if not ok:
        pipe_conn.send(("error", f"MEMORY_CONFIG_FAIL: {msg}"))
        return
    try:
        # Allocate 500 MB array under strict limit
        data = bytearray(500 * 1024 * 1024)
        pipe_conn.send(("ok", len(data)))
    except MemoryError as me:
        pipe_conn.send(("error", f"MEMORY_ENFORCED: MemoryError caught ({me})"))
    except Exception as e:
        pipe_conn.send(("error", f"WORKER_EXCEPTION: {e}"))

def _failing_fault_worker(pipe_conn, plugin_id, params, array, max_memory_mb):
    import sys
    sys.exit(137)  # Simulate crash or SIGKILL exit code

def _result_then_hang_worker(pipe_conn, plugin_id, params, array, max_memory_mb):
    import time
    pipe_conn.send(("ok", "preliminary_payload"))
    while True:
        time.sleep(0.01)

def _set_limit_worker_target(pipe_conn, plugin_id, params, array, max_memory_mb):
    import os
    from core.rest_api import _set_memory_limit, resource
    pid = os.getpid()
    ok, msg = _set_memory_limit(max_memory_mb)
    if ok and resource and hasattr(resource, 'RLIMIT_AS'):
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        pipe_conn.send(("ok", (pid, soft, hard)))
    else:
        pipe_conn.send(("error", msg))

class TestSEC03SandboxIsolation(unittest.TestCase):
    """
    Automated regression tests proving SEC-03 review requirements:
    - Finding 1: Memory-limit soft/hard calculation, OS failures vs invalid config, parent process unaffected.
    - Finding 2: Genuine timeout vs abnormal exit distinction with exit codes.
    - Finding 3: Deterministic worker termination and cleanup verification without orphaned processes.
    """

    def test_memory_limit_unit_and_parent_process_unaffected(self):
        """Verify _set_memory_limit calculations, error reports, and parent process isolation."""
        import sys
        import os
        from core.rest_api import _set_memory_limit, resource

        # 1. Invalid config
        ok, msg = _set_memory_limit(-10)
        self.assertFalse(ok)
        self.assertIn("Invalid memory limit configuration", msg)

        ok, msg = _set_memory_limit("invalid")
        self.assertFalse(ok)
        self.assertIn("Invalid memory limit configuration", msg)

        if sys.platform != "win32" and resource is not None and hasattr(resource, 'RLIMIT_AS'):
            parent_soft_before, parent_hard_before = resource.getrlimit(resource.RLIMIT_AS)

            # Execute in isolated sandbox process to verify limit enforcement in worker
            res, err = _run_in_sandbox_process(
                plugin_id="bubble_sort",
                params=None,
                array=[1],
                max_memory_mb=1024,
                timeout_sec=5,
                target_func=_set_limit_worker_target
            )
            self.assertIsNone(err)
            self.assertIsNotNone(res)
            worker_pid, w_soft, w_hard = res
            self.assertEqual(w_soft, 1024 * 1024 * 1024)

            # Verify parent process limits remain untouched
            parent_soft_after, parent_hard_after = resource.getrlimit(resource.RLIMIT_AS)
            self.assertEqual(parent_soft_before, parent_soft_after)
            self.assertEqual(parent_hard_before, parent_hard_after)

            # Verify worker process is dead
            try:
                os.kill(worker_pid, 0)
                alive = True
            except OSError:
                alive = False
            self.assertFalse(alive, "Worker process PID should be dead after execution")

    def test_worker_infinite_loop_timeout_and_cleanup(self):
        """Infinite loop worker is stopped on timeout, and process is proven no longer alive via PID check."""
        import os
        import time

        captured_pid = []

        t0 = time.time()
        res, err = _run_in_sandbox_process(
            plugin_id="bubble_sort",
            params=None,
            array=[1, 2, 3],
            max_memory_mb=256,
            timeout_sec=1,
            target_func=_infinite_loop_worker,
            pid_callback=lambda p: captured_pid.append(p)
        )
        elapsed = time.time() - t0

        self.assertIsNone(res)
        self.assertIsNotNone(err)
        self.assertIn("timeout", err.lower())
        self.assertGreaterEqual(elapsed, 0.9)

        self.assertEqual(len(captured_pid), 1, "Worker PID should have been captured")
        w_pid = captured_pid[0]
        try:
            os.kill(w_pid, 0)
            alive = True
        except OSError:
            alive = False
        self.assertFalse(alive, f"Timed-out worker process (PID {w_pid}) is still alive after cleanup!")

    def test_repeated_timed_out_executions_no_orphans(self):
        """Repeated timed-out executions leave 0 orphaned processes (verified via PID handles)."""
        import os

        captured_pids = []

        for _ in range(3):
            res, err = _run_in_sandbox_process(
                plugin_id="bubble_sort",
                params=None,
                array=[1],
                max_memory_mb=256,
                timeout_sec=1,
                target_func=_infinite_loop_worker,
                pid_callback=lambda p: captured_pids.append(p)
            )
            self.assertIsNone(res)
            self.assertIsNotNone(err)
            self.assertIn("timeout", err.lower())

        self.assertEqual(len(captured_pids), 3, "All 3 worker PIDs should have been captured")
        for w_pid in captured_pids:
            try:
                os.kill(w_pid, 0)
                alive = True
            except OSError:
                alive = False
            self.assertFalse(alive, f"Repeated timeout test leaked orphan worker process (PID {w_pid})!")

    def test_distinguish_timeout_from_abnormal_exit(self):
        """Finding 2: Process exit before timeout is classified as abnormal exit with exit code, NOT timeout."""
        res, err = _run_in_sandbox_process(
            plugin_id="bubble_sort",
            params=None,
            array=[1],
            max_memory_mb=256,
            timeout_sec=10,
            target_func=_failing_fault_worker
        )

        self.assertIsNone(res)
        self.assertIsNotNone(err)
        self.assertNotIn("timeout", err.lower())
        self.assertIn("exited abnormally with code", err.lower())
        self.assertIn("137", err)

    def test_worker_sends_result_then_hangs_cleaned_up(self):
        """Edge case: worker sends result but remains alive; caller must terminate it and return controlled error."""
        import os

        captured_pid = []
        res, err = _run_in_sandbox_process(
            plugin_id="bubble_sort",
            params=None,
            array=[1],
            max_memory_mb=256,
            timeout_sec=5,
            target_func=_result_then_hang_worker,
            pid_callback=lambda p: captured_pid.append(p)
        )

        self.assertIsNone(res)
        self.assertIsNotNone(err)
        self.assertIn("remained alive after sending result", err)

        self.assertEqual(len(captured_pid), 1, "Worker PID should have been captured")
        w_pid = captured_pid[0]
        try:
            os.kill(w_pid, 0)
            alive = True
        except OSError:
            alive = False
        self.assertFalse(alive, f"Hanging worker process (PID {w_pid}) is still alive after cleanup!")

    def test_worker_memory_limit_exceeded_distinction(self):
        """Finding 3: Proves memory limit was applied and distinguishes OOM/MemoryError from timeout/exceptions."""
        import sys
        from core.rest_api import resource

        if sys.platform == "win32" or resource is None or not hasattr(resource, 'RLIMIT_AS'):
            self.skipTest("RLIMIT_AS memory enforcement is POSIX-only. Windows non-POSIX fallback documented.")

        res, err = _run_in_sandbox_process(
            plugin_id="bubble_sort",
            params=None,
            array=[1],
            max_memory_mb=20,
            timeout_sec=5,
            target_func=_memory_hog_worker
        )

        self.assertIsNone(res)
        self.assertIsNotNone(err)
        # Verify that memory enforcement triggered OOM/MemoryError or abnormal exit, NOT a timeout
        self.assertNotIn("timeout", err.lower())
        self.assertTrue(
            "memory" in err.lower() or "exited abnormally" in err.lower() or "memória" in err.lower()
        )

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
