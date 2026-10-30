# -*- coding: utf-8 -*-
import unittest
import json
import urllib.request
import urllib.error
import time
from pathlib import Path

from core.plugin_system import PluginLoader
from core.engine import Engine
from core.rest_api import SecureRESTAPIServer, RESTConfig, _run_in_sandbox_process, hash_api_key
from core.version import REST_API_VERSION, API_MANAGER_VERSION, MAIN_VERSION
from datetime import datetime, timedelta

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

def _unsupported_platform_worker(pipe_conn, plugin_id, params, array, max_memory_mb):
    import sys
    import core.rest_api
    import core.plugin_system

    class GuardedPluginLoader:
        def __init__(self, *args, **kwargs):
            raise AssertionError("FAIL-CLOSED VIOLATION: PluginLoader was instantiated after memory limit setup failed!")

    # Patch resource = None and monkeypatch PluginLoader to fail if instantiated
    old_resource = core.rest_api.resource
    old_loader = core.plugin_system.PluginLoader
    try:
        core.rest_api.resource = None
        core.plugin_system.PluginLoader = GuardedPluginLoader
        # Directly invoke production _sandbox_worker_target
        core.rest_api._sandbox_worker_target(pipe_conn, plugin_id, params, array, max_memory_mb)
    finally:
        core.rest_api.resource = old_resource
        core.plugin_system.PluginLoader = old_loader

def _os_setrlimit_failure_worker(pipe_conn, plugin_id, params, array, max_memory_mb):
    import sys
    import core.rest_api
    import core.plugin_system
    from unittest.mock import patch

    class GuardedPluginLoader:
        def __init__(self, *args, **kwargs):
            raise AssertionError("FAIL-CLOSED VIOLATION: PluginLoader was instantiated after setrlimit failed!")

    def mock_setrlimit(*args, **kwargs):
        raise OSError("Simulated OS setrlimit permission error")

    old_loader = core.plugin_system.PluginLoader
    try:
        core.plugin_system.PluginLoader = GuardedPluginLoader
        if core.rest_api.resource is not None:
            with patch.object(core.rest_api.resource, "setrlimit", side_effect=mock_setrlimit):
                core.rest_api._sandbox_worker_target(pipe_conn, plugin_id, params, array, max_memory_mb)
        else:
            core.rest_api._sandbox_worker_target(pipe_conn, plugin_id, params, array, max_memory_mb)
    finally:
        core.plugin_system.PluginLoader = old_loader

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

    def test_unsupported_platform_fails_closed(self):
        """Verify fail-closed requirement: if OS memory limit is unavailable, production worker target rejects execution before PluginLoader runs."""
        res, err = _run_in_sandbox_process(
            plugin_id="bubble_sort",
            params=None,
            array=[1],
            max_memory_mb=256,
            timeout_sec=5,
            target_func=_unsupported_platform_worker
        )
        self.assertIsNone(res)
        self.assertIsNotNone(err)
        self.assertIn("Sandbox memory configuration failure", err)
        self.assertIn("unavailable on this platform", err)
        self.assertNotIn("FAIL-CLOSED VIOLATION", err, "PluginLoader must NOT be instantiated when memory limit is unsupported!")

    def test_os_setrlimit_failure_fails_closed(self):
        """Verify OS-level setrlimit failure fails closed and prevents production worker target from instantiating PluginLoader."""
        res, err = _run_in_sandbox_process(
            plugin_id="bubble_sort",
            params=None,
            array=[1],
            max_memory_mb=256,
            timeout_sec=5,
            target_func=_os_setrlimit_failure_worker
        )
        self.assertIsNone(res)
        self.assertIsNotNone(err)
        self.assertIn("Sandbox memory configuration failure", err)
        self.assertIn("OS error enforcing memory limit", err)
        self.assertNotIn("FAIL-CLOSED VIOLATION", err, "PluginLoader must NOT be instantiated when setrlimit fails!")

    def test_invalid_and_nonsensical_configurations(self):
        """Invalid/nonsensical timeout and memory limit configs are rejected safely by failing closed."""
        res, err = _run_in_sandbox_process(
            plugin_id="bubble_sort",
            params=None,
            array=[2, 1],
            max_memory_mb=0,
            timeout_sec=-5
        )
        self.assertIsNone(res)
        self.assertIsNotNone(err)
        self.assertIn("Sandbox memory configuration failure", err)

class TestSEC01APIKeyStorage(unittest.TestCase):
    """
    Deterministic regression tests covering SEC-01 requirements for API Key Hashing & Storage:
    - Generated token authenticates successfully; incorrect token or hash-as-token is rejected.
    - Saved JSON contains neither raw token nor raw-token field.
    - Newly created token returned once in key-creation response, not duplicated in key_info.
    - Existing plaintext records migrate successfully and original tokens remain usable.
    - Migration re-runs are safe and idempotent.
    - Malformed/mixed records handled without silent data loss or plaintext persistence.
    - Revocation works after migration.
    - Permission, expiry, IP whitelist, rate-limit behavior intact.
    - No sensitive token appears in captured log/error output.
    """

    def setUp(self):
        self.config_path = Path("saves/test_sec01_config.json")
        self.keys_path = Path("saves/test_sec01_keys.json")
        self.log_path = Path("saves/test_sec01_access.log")

        from core.rest_api import RateLimiter, SecureRESTHandler
        SecureRESTHandler.rate_limiter = RateLimiter()

        self.server = SecureRESTAPIServer(
            config_path=str(self.config_path),
            keys_path=str(self.keys_path)
        )
        self.server.config.enabled = True
        self.server.config.host = "127.0.0.1"
        self.server.config.port = 8889
        self.server.config.require_api_key = True
        self.server.config.log_file = str(self.log_path)
        self.server.config.log_all_requests = True

    def tearDown(self):
        if self.server.is_running():
            self.server.stop()
        for p in [self.config_path, self.keys_path, self.log_path]:
            if p.exists():
                p.unlink()

    def _make_request(self, path, method="GET", body=None, headers=None):
        url = f"http://127.0.0.1:8889{path}"
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

    def test_token_authentication_and_hash_bearer_rejection(self):
        """Generated token authenticates successfully, incorrect token and raw hash token are rejected."""
        raw_token = self.server.create_key("test_key", permissions=["read"])
        token_hash = hash_api_key(raw_token)
        self.server.start()
        time.sleep(0.05)

        # 1. Correct token authenticates
        status, res = self._make_request("/api/v2/status", headers={"X-API-Key": raw_token})
        self.assertEqual(status, 200)
        self.assertEqual(res["status"], "ok")

        # 2. Incorrect token rejected
        status, res = self._make_request("/api/v2/status", headers={"X-API-Key": "invalid_secret_token_12345"})
        self.assertEqual(status, 403)
        self.assertEqual(res["error"], "Érvénytelen API kulcs")

        # 3. Presenting the SHA-256 hash itself as bearer token is REJECTED
        status, res = self._make_request("/api/v2/status", headers={"X-API-Key": token_hash})
        self.assertEqual(status, 403)
        self.assertEqual(res["error"], "Érvénytelen API kulcs")

    def test_persisted_json_storage_contains_no_raw_token(self):
        """The saved JSON file contains only cryptographic digests and no raw token strings or raw key fields."""
        raw_token = self.server.create_key("secret_user_key", permissions=["read", "execute"])

        # Read the persisted api_keys.json file
        with open(self.keys_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
            data = json.loads(raw_content)

        # Check raw token is nowhere in the file text
        self.assertNotIn(raw_token, raw_content)

        # Check dictionary keys are hashes (length 64 hex strings)
        expected_hash = hash_api_key(raw_token)
        self.assertIn(expected_hash, data)
        record = data[expected_hash]
        self.assertEqual(record["key"], expected_hash)
        self.assertTrue(record["hashed"])

    def test_key_creation_response_contract_no_duplicate_token(self):
        """Key creation returns raw token in "api_key", and "key_info" key field contains digest, not raw token."""
        admin_token = self.server.create_key("admin_key", permissions=["admin"])
        self.server.start()
        time.sleep(0.05)

        body = {"name": "new_service_key", "permissions": ["read"], "rate_limit": 100}
        status, res = self._make_request("/api/v2/keys", method="POST", body=body, headers={"X-API-Key": admin_token})
        self.assertEqual(status, 201)
        self.assertIn("api_key", res)
        self.assertIn("key_info", res)

        returned_raw_token = res["api_key"]
        key_info = res["key_info"]

        # Ensure key_info["key"] is the SHA-256 digest, NOT the raw token
        self.assertNotEqual(key_info["key"], returned_raw_token)
        self.assertEqual(key_info["key"], hash_api_key(returned_raw_token))
        self.assertTrue(key_info["hashed"])

        # Authenticate with the returned raw token
        status, _ = self._make_request("/api/v2/status", headers={"X-API-Key": returned_raw_token})
        self.assertEqual(status, 200)

    def test_legacy_plaintext_migration_and_idempotency(self):
        """Legacy plaintext records migrate seamlessly; original tokens work after migration, and re-runs are idempotent."""
        legacy_raw_key = "legacy_secret_token_abc123"
        legacy_data = {
            legacy_raw_key: {
                "key": legacy_raw_key,
                "name": "legacy_app",
                "permissions": ["read"],
                "created_at": datetime.now().isoformat(),
                "expires_at": None,
                "last_used": None,
                "usage_count": 5,
                "ip_whitelist": [],
                "rate_limit_per_min": 60
            }
        }
        with open(self.keys_path, "w", encoding="utf-8") as f:
            json.dump(legacy_data, f, indent=2)

        # 1. Initialize server to trigger migration
        migrated_server = SecureRESTAPIServer(
            config_path=str(self.config_path),
            keys_path=str(self.keys_path)
        )
        migrated_server.config.enabled = True
        migrated_server.config.port = 8889

        # Verify raw key removed from disk file
        with open(self.keys_path, "r", encoding="utf-8") as f:
            disk_content = f.read()
            disk_json = json.loads(disk_content)

        self.assertNotIn(legacy_raw_key, disk_content)
        expected_hash = hash_api_key(legacy_raw_key)
        self.assertIn(expected_hash, disk_json)
        self.assertTrue(disk_json[expected_hash]["hashed"])

        # Verify original token authenticates
        migrated_server.start()
        time.sleep(0.05)
        status, res = self._make_request("/api/v2/status", headers={"X-API-Key": legacy_raw_key})
        migrated_server.stop()
        self.assertEqual(status, 200)

        # 2. Test Migration Idempotency by re-loading
        reloaded_server = SecureRESTAPIServer(
            config_path=str(self.config_path),
            keys_path=str(self.keys_path)
        )
        self.assertEqual(len(reloaded_server.api_keys), 1)
        self.assertIn(expected_hash, reloaded_server.api_keys)

    def test_malformed_records_fail_closed_without_data_loss(self):
        """Malformed or corrupt legacy JSON records raise an exception on load and preserve the file on disk."""
        corrupt_content = '{"valid_key": "not_a_dict_record"}'
        with open(self.keys_path, "w", encoding="utf-8") as f:
            f.write(corrupt_content)

        with self.assertRaises(ValueError):
            SecureRESTAPIServer(
                config_path=str(self.config_path),
                keys_path=str(self.keys_path)
            )

        # File on disk must remain unchanged (recoverable)
        with open(self.keys_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), corrupt_content)

    def test_migration_error_does_not_leak_secret_token_in_logs_or_exceptions(self):
        """Synthetic secret token used as dictionary key in corrupt legacy file is NEVER printed or leaked in exceptions/logs/stdout/stderr."""
        import io
        import sys

        synthetic_secret = "DISTINCTIVE_SYNTHETIC_SECRET_TOKEN_99999"
        corrupt_legacy_data = {
            synthetic_secret: "invalid_non_dict_record_content"
        }

        with open(self.keys_path, "w", encoding="utf-8") as f:
            json.dump(corrupt_legacy_data, f)

        captured_stdout = io.StringIO()
        captured_stderr = io.StringIO()

        old_stdout, old_stderr = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = captured_stdout, captured_stderr
            with self.assertRaises(ValueError) as cm:
                SecureRESTAPIServer(
                    config_path=str(self.config_path),
                    keys_path=str(self.keys_path)
                )
            exception_msg = str(cm.exception)
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

        stdout_val = captured_stdout.getvalue()
        stderr_val = captured_stderr.getvalue()

        # Synthetic secret token MUST NOT appear in exception message, stdout, or stderr
        self.assertNotIn(synthetic_secret, exception_msg)
        self.assertNotIn(synthetic_secret, stdout_val)
        self.assertNotIn(synthetic_secret, stderr_val)

        # Original corrupt file remains intact on disk
        with open(self.keys_path, "r", encoding="utf-8") as f:
            self.assertIn(synthetic_secret, f.read())

    def test_atomic_save_keys_resilience_to_write_failures(self):
        """save_keys() atomic write failure does not destroy existing valid key file, and temp files are cleaned up."""
        from unittest.mock import patch

        initial_key = self.server.create_key("initial_key", permissions=["read"])
        with open(self.keys_path, "r", encoding="utf-8") as f:
            initial_content = f.read()

        # Simulate failure during os.replace
        with patch("os.replace", side_effect=OSError("Simulated disk replace error")):
            with self.assertRaises(OSError):
                self.server.create_key("failing_key", permissions=["read"])

        # Original valid file on disk MUST remain untouched
        with open(self.keys_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), initial_content)

        # Ensure no leftover temporary files in keys_path directory
        temp_files = list(self.keys_path.parent.glob(f".{self.keys_path.name}.tmp_*"))
        self.assertEqual(len(temp_files), 0, f"Leftover temporary files found: {temp_files}")

    def test_malformed_sha256_digest_rejection_and_file_preservation(self):
        """Dedicated test: records marked hashed=True with malformed SHA-256 digests fail load_keys(), leaving file byte-for-byte unchanged and zero secret leakage."""
        import io
        import sys

        synthetic_secret = "MALFORMED_DIGEST_SECRET_98765"

        malformed_cases = [
            # Case A: 63 hex chars (too short)
            {"key_str": "a" * 63, "rec_key": "a" * 63},
            # Case B: 65 hex chars (too long)
            {"key_str": "b" * 65, "rec_key": "b" * 65},
            # Case C: 64 chars with non-hex character 'Z'
            {"key_str": "c" * 63 + "Z", "rec_key": "c" * 63 + "Z"},
            # Case D: raw string token as key
            {"key_str": synthetic_secret, "rec_key": synthetic_secret}
        ]

        for idx, m_case in enumerate(malformed_cases):
            raw_key_str = m_case["key_str"]
            rec_key_val = m_case["rec_key"]

            data = {
                raw_key_str: {
                    "key": rec_key_val,
                    "name": f"malformed_rec_{idx}",
                    "permissions": ["read"],
                    "created_at": datetime.now().isoformat(),
                    "hashed": True
                }
            }

            expected_bytes = json.dumps(data, indent=2).encode("utf-8")
            with open(self.keys_path, "wb") as f:
                f.write(expected_bytes)

            cap_out, cap_err = io.StringIO(), io.StringIO()
            old_out, old_err = sys.stdout, sys.stderr
            try:
                sys.stdout, sys.stderr = cap_out, cap_err
                with self.assertRaises(ValueError) as cm:
                    SecureRESTAPIServer(config_path=str(self.config_path), keys_path=str(self.keys_path))
                err_msg = str(cm.exception)
            finally:
                sys.stdout, sys.stderr = old_out, old_err

            # 1. Zero secret leak
            self.assertNotIn(synthetic_secret, err_msg)
            self.assertNotIn(synthetic_secret, cap_out.getvalue())
            self.assertNotIn(synthetic_secret, cap_err.getvalue())

            # 2. File byte-for-byte unchanged on disk
            with open(self.keys_path, "rb") as f:
                self.assertEqual(f.read(), expected_bytes)

    def test_strict_digest_validation_and_tampered_records(self):
        """Strictly validates SHA-256 digests in load_keys(); rejects raw tokens, mismatched keys, and corrupt digests without overwriting disk file."""
        import io
        import sys

        synthetic_secret = "SECRET_LEAK_TEST_TOKEN_12345"
        valid_raw = "valid_raw_token_xyz"
        valid_hash = hash_api_key(valid_raw)

        # 1. Record marked hashed=True but with raw token as dict key
        bad_hash_key_data = {
            synthetic_secret: {
                "key": synthetic_secret,
                "name": "fake_hashed",
                "permissions": ["read"],
                "created_at": datetime.now().isoformat(),
                "hashed": True
            }
        }

        # Write bad file
        with open(self.keys_path, "w", encoding="utf-8") as f:
            json.dump(bad_hash_key_data, f)

        cap_out, cap_err = io.StringIO(), io.StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = cap_out, cap_err
            with self.assertRaises(ValueError) as cm:
                SecureRESTAPIServer(config_path=str(self.config_path), keys_path=str(self.keys_path))
            err_msg = str(cm.exception)
        finally:
            sys.stdout, sys.stderr = old_out, old_err

        # Assert zero secret leak
        self.assertNotIn(synthetic_secret, err_msg)
        self.assertNotIn(synthetic_secret, cap_out.getvalue())
        self.assertNotIn(synthetic_secret, cap_err.getvalue())

        # Assert file byte-for-byte unchanged
        with open(self.keys_path, "r", encoding="utf-8") as f:
            self.assertIn(synthetic_secret, f.read())

        # 2. Record dict key and "key" field mismatch
        mismatched_data = {
            valid_hash: {
                "key": "0000000000000000000000000000000000000000000000000000000000000000",
                "name": "mismatch",
                "permissions": ["read"],
                "created_at": datetime.now().isoformat(),
                "hashed": True
            }
        }
        with open(self.keys_path, "w", encoding="utf-8") as f:
            json.dump(mismatched_data, f)

        with self.assertRaises(ValueError):
            SecureRESTAPIServer(config_path=str(self.config_path), keys_path=str(self.keys_path))

    def test_mixed_legacy_and_valid_hashed_records_migration(self):
        """Mixed file with valid legacy plaintext and valid hashed records loads, migrates legacy, and preserves all keys."""
        legacy_raw = "legacy_token_mix_111"
        legacy_hash = hash_api_key(legacy_raw)

        hashed_raw = "already_hashed_token_222"
        hashed_digest = hash_api_key(hashed_raw)

        mixed_data = {
            legacy_raw: {
                "key": legacy_raw,
                "name": "legacy_part",
                "permissions": ["read"],
                "created_at": datetime.now().isoformat(),
                "hashed": False
            },
            hashed_digest: {
                "key": hashed_digest,
                "name": "hashed_part",
                "permissions": ["read", "execute"],
                "created_at": datetime.now().isoformat(),
                "hashed": True
            }
        }

        with open(self.keys_path, "w", encoding="utf-8") as f:
            json.dump(mixed_data, f, indent=2)

        srv = SecureRESTAPIServer(config_path=str(self.config_path), keys_path=str(self.keys_path))
        srv.config.enabled = True
        srv.config.port = 8889
        self.assertEqual(len(srv.api_keys), 2)
        self.assertIn(legacy_hash, srv.api_keys)
        self.assertIn(hashed_digest, srv.api_keys)

        # Confirm migration persisted
        with open(self.keys_path, "r", encoding="utf-8") as f:
            saved = json.load(f)
        self.assertNotIn(legacy_raw, saved)
        self.assertIn(legacy_hash, saved)
        self.assertIn(hashed_digest, saved)

        # Both tokens work
        srv.start()
        time.sleep(0.05)
        s1, _ = self._make_request("/api/v2/status", headers={"X-API-Key": legacy_raw})
        s2, _ = self._make_request("/api/v2/status", headers={"X-API-Key": hashed_raw})
        srv.stop()
        self.assertEqual(s1, 200)
        self.assertEqual(s2, 200)

    def test_create_key_endpoint_expire_days_validation(self):
        """Strengthened: Every invalid expire_days input returns HTTP 400, leaves in-memory key count unchanged, and leaves disk key file byte-for-byte identical."""
        admin_token = self.server.create_key("admin_user", permissions=["admin"])
        self.server.start()
        time.sleep(0.05)

        initial_count = len(self.server.api_keys)
        with open(self.keys_path, "rb") as f:
            initial_file_bytes = f.read()

        invalid_payloads = [
            {"name": "k1", "expire_days": "not_a_number"},
            {"name": "k2", "expire_days": -5},
            {"name": "k3", "expire_days": 0},
            {"name": "k4", "expire_days": True},
            {"name": "k5", "expire_days": [30]},
            {"name": "k6", "expire_days": float("nan")},
            {"name": "k7", "expire_days": float("inf")},
            {"name": "k8", "expire_days": float("-inf")}
        ]

        for payload in invalid_payloads:
            status, res = self._make_request("/api/v2/keys", method="POST", body=payload, headers={"X-API-Key": admin_token})
            self.assertEqual(status, 400, f"Payload {payload} should have returned 400")
            self.assertIn("error", res)
            self.assertIn("expire_days", res["error"])

            # Assert in-memory key count remains unchanged
            self.assertEqual(len(self.server.api_keys), initial_count, f"Key count changed for payload {payload}")

            # Assert persisted key file on disk remains byte-for-byte identical
            with open(self.keys_path, "rb") as f:
                self.assertEqual(f.read(), initial_file_bytes, f"Key file altered on disk for payload {payload}")

    def test_create_key_persistence_failure_rollback(self):
        """If save_keys() fails during create_key(), in-memory key state is rolled back and error is returned."""
        from unittest.mock import patch

        admin_token = self.server.create_key("admin_user", permissions=["admin"])
        self.server.start()
        time.sleep(0.05)

        initial_count = len(self.server.api_keys)

        with patch.object(self.server, "save_keys", side_effect=OSError("Simulated save error")):
            # 1. Direct call
            with self.assertRaises(OSError):
                self.server.create_key("fail_key", permissions=["read"])
            self.assertEqual(len(self.server.api_keys), initial_count)

            # 2. HTTP endpoint call
            status, res = self._make_request("/api/v2/keys", method="POST", body={"name": "fail_http"}, headers={"X-API-Key": admin_token})
            self.assertEqual(status, 500)
            self.assertEqual(len(self.server.api_keys), initial_count)

    def test_revocation_by_raw_token_or_digest(self):
        """revocation works using either raw token or key digest after storage is hashed."""
        key1 = self.server.create_key("key1", permissions=["read"])
        key2 = self.server.create_key("key2", permissions=["read"])

        hash1 = hash_api_key(key1)
        hash2 = hash_api_key(key2)

        self.assertIn(hash1, self.server.api_keys)
        self.assertIn(hash2, self.server.api_keys)

        # Revoke key1 by raw token
        self.server.revoke_key(key1)
        self.assertNotIn(hash1, self.server.api_keys)

        # Revoke key2 by hash digest
        self.server.revoke_key(hash2)
        self.assertNotIn(hash2, self.server.api_keys)

    def test_permission_expiry_ip_whitelist_and_rate_limiting(self):
        """All metadata controls (permissions, expiry, IP whitelist, rate limits) work correctly with hashed keys."""
        # Expiry test
        exp_key = self.server.create_key("exp_key", permissions=["read"])
        exp_hash = hash_api_key(exp_key)
        self.server.api_keys[exp_hash].expires_at = (datetime.now() - timedelta(days=1)).isoformat()

        # IP whitelist test
        ip_key = self.server.create_key("ip_key", permissions=["read"], ip_whitelist=["10.0.0.1"])

        # Rate limit test
        rate_key = self.server.create_key("rate_key", permissions=["read"], rate_limit=2)

        self.server.start()
        time.sleep(0.05)

        # Expired key fails
        status, res = self._make_request("/api/v2/status", headers={"X-API-Key": exp_key})
        self.assertEqual(status, 403)
        self.assertIn("lejárt", res["error"].lower())

        # IP whitelist mismatch fails
        status, res = self._make_request("/api/v2/status", headers={"X-API-Key": ip_key})
        self.assertEqual(status, 403)
        self.assertIn("whitelist", res["error"].lower())

        # Rate limit per key triggers after limit exceeded
        status1, _ = self._make_request("/api/v2/status", headers={"X-API-Key": rate_key})
        status2, _ = self._make_request("/api/v2/status", headers={"X-API-Key": rate_key})
        status3, res3 = self._make_request("/api/v2/status", headers={"X-API-Key": rate_key})

        self.assertEqual(status1, 200)
        self.assertEqual(status2, 200)
        self.assertEqual(status3, 403)
        self.assertIn("rate limit", res3["error"].lower())

    def test_logs_and_error_messages_contain_no_raw_tokens(self):
        """Zero sensitive raw tokens appear in captured request logs or error response messages."""
        raw_token = self.server.create_key("log_test_key", permissions=["read"])
        self.server.start()
        time.sleep(0.05)

        # Make valid and invalid requests
        self._make_request("/api/v2/status", headers={"X-API-Key": raw_token})
        self._make_request("/api/v2/status", headers={"X-API-Key": "invalid_token_xyz"})

        self.server.stop()

        if self.log_path.exists():
            with open(self.log_path, "r", encoding="utf-8") as f:
                log_contents = f.read()
            self.assertNotIn(raw_token, log_contents)
            self.assertNotIn("invalid_token_xyz", log_contents)

class TestSEC02CORSValidation(unittest.TestCase):
    """
    Automated regression tests covering SEC-02 requirements for CORS Origin Validation and Response Headers:
    1. Allowed Origin receives exactly its matching Access-Control-Allow-Origin value.
    2. Multiple configured allowed origins result in only the requesting Origin being returned.
    3. Disallowed Origin is not reflected or granted access.
    4. Missing Origin does not cause a permissive fallback.
    5. OPTIONS preflight from allowed Origin receives valid CORS headers, methods, and request headers without requiring API key.
    6. Disallowed or missing Origin preflight receives no permissive CORS headers.
    7. CORS-disabled mode does not emit CORS permission headers.
    8. Actual protected requests enforce API key and permission checks (CORS cannot bypass auth).
    9. Vary: Origin header included on CORS-enabled responses.
    """

    def setUp(self):
        self.config_path = Path("saves/test_sec02_config.json")
        self.keys_path = Path("saves/test_sec02_keys.json")

        self.server = SecureRESTAPIServer(
            config_path=str(self.config_path),
            keys_path=str(self.keys_path)
        )
        self.server.config.enabled = True
        self.server.config.host = "127.0.0.1"
        self.server.config.port = 8890
        self.server.config.require_api_key = True
        self.server.config.enable_cors = True
        self.server.config.cors_origins = ["http://localhost:3000", "https://app.example.com"]

        self.read_key = self.server.create_key("read_key", permissions=["read"])
        self.exec_key = self.server.create_key("exec_key", permissions=["read", "execute"])

        self.server.start()
        time.sleep(0.05)

    def tearDown(self):
        if self.server.is_running():
            self.server.stop()
        for p in [self.config_path, self.keys_path]:
            if p.exists():
                p.unlink()

    def _make_raw_request(self, path, method="GET", body=None, headers=None):
        url = f"http://127.0.0.1:8890{path}"
        req_headers = headers or {}
        data = json.dumps(body).encode("utf-8") if body is not None else None

        if body is not None and "Content-Type" not in req_headers:
            req_headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                res_body = resp.read().decode("utf-8")
                resp_headers = {k.lower(): v for k, v in resp.headers.items()}
                try:
                    parsed = json.loads(res_body)
                except Exception:
                    parsed = res_body
                return resp.status, resp_headers, parsed
        except urllib.error.HTTPError as e:
            res_body = e.read().decode("utf-8")
            resp_headers = {k.lower(): v for k, v in e.headers.items()}
            try:
                parsed = json.loads(res_body)
            except Exception:
                parsed = res_body
            return e.code, resp_headers, parsed

    def test_allowed_origin_returns_exact_match_and_vary_header(self):
        """1 & 9. An allowed Origin receives exactly its matching Access-Control-Allow-Origin value and Vary: Origin."""
        headers = {"X-API-Key": self.read_key, "Origin": "http://localhost:3000"}
        status, resp_headers, res = self._make_raw_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 200)
        self.assertEqual(resp_headers.get("access-control-allow-origin"), "http://localhost:3000")
        self.assertEqual(resp_headers.get("vary"), "Origin")

    def test_multiple_origins_returns_only_matching_origin(self):
        """2. Multiple configured allowed origins result in only the request's matching Origin being returned."""
        headers = {"X-API-Key": self.read_key, "Origin": "https://app.example.com"}
        status, resp_headers, res = self._make_raw_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 200)
        self.assertEqual(resp_headers.get("access-control-allow-origin"), "https://app.example.com")
        self.assertNotIn(",", resp_headers.get("access-control-allow-origin", ""))

    def test_disallowed_origin_not_reflected_or_granted_access(self):
        """3. A disallowed Origin is not reflected or granted access."""
        headers = {"X-API-Key": self.read_key, "Origin": "https://malicious.attacker.com"}
        status, resp_headers, res = self._make_raw_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 200)
        self.assertNotIn("access-control-allow-origin", resp_headers)
        self.assertEqual(resp_headers.get("vary"), "Origin")

    def test_missing_origin_does_not_cause_permissive_fallback(self):
        """4. A missing Origin does not cause a permissive fallback."""
        headers = {"X-API-Key": self.read_key}
        status, resp_headers, res = self._make_raw_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 200)
        self.assertNotIn("access-control-allow-origin", resp_headers)

    def test_options_preflight_allowed_origin_no_api_key_required(self):
        """5. OPTIONS preflight from allowed Origin receives valid CORS headers, methods, and headers without API key."""
        headers = {"Origin": "http://localhost:3000"}
        status, resp_headers, res = self._make_raw_request("/api/v2/run", method="OPTIONS", headers=headers)
        self.assertEqual(status, 200)
        self.assertEqual(resp_headers.get("access-control-allow-origin"), "http://localhost:3000")
        self.assertEqual(resp_headers.get("access-control-allow-methods"), "GET, POST, OPTIONS")
        self.assertEqual(resp_headers.get("access-control-allow-headers"), "Content-Type, X-API-Key")
        self.assertEqual(resp_headers.get("vary"), "Origin")

    def test_options_preflight_disallowed_or_missing_origin(self):
        """6. A disallowed or missing Origin preflight receives no permissive CORS headers."""
        headers = {"Origin": "https://disallowed.org"}
        status, resp_headers, res = self._make_raw_request("/api/v2/run", method="OPTIONS", headers=headers)
        self.assertEqual(status, 200)
        self.assertNotIn("access-control-allow-origin", resp_headers)
        self.assertNotIn("access-control-allow-methods", resp_headers)
        self.assertNotIn("access-control-allow-headers", resp_headers)

        # Missing origin
        status_no_orig, resp_headers_no_orig, _ = self._make_raw_request("/api/v2/run", method="OPTIONS")
        self.assertEqual(status_no_orig, 200)
        self.assertNotIn("access-control-allow-origin", resp_headers_no_orig)
        self.assertNotIn("access-control-allow-methods", resp_headers_no_orig)
        self.assertNotIn("access-control-allow-headers", resp_headers_no_orig)

    def test_cors_disabled_mode_emits_no_cors_headers(self):
        """7. CORS-disabled mode does not emit CORS permission headers."""
        self.server.config.enable_cors = False

        # Preflight returns 403 when CORS disabled
        headers = {"Origin": "http://localhost:3000"}
        status, resp_headers, _ = self._make_raw_request("/api/v2/run", method="OPTIONS", headers=headers)
        self.assertEqual(status, 403)
        self.assertNotIn("access-control-allow-origin", resp_headers)

        # Regular response emits no CORS headers
        req_headers = {"X-API-Key": self.read_key, "Origin": "http://localhost:3000"}
        status, resp_headers, _ = self._make_raw_request("/api/v2/status", headers=req_headers)
        self.assertEqual(status, 200)
        self.assertNotIn("access-control-allow-origin", resp_headers)
        self.assertNotIn("vary", resp_headers)

    def test_protected_requests_enforce_api_key_and_permissions(self):
        """8. Actual protected requests still enforce API key and permission checks; CORS does not bypass server-side authorization."""
        headers = {"Origin": "http://localhost:3000"}  # Allowed origin, but NO API key

        # GET status without API key -> 403
        status, resp_headers, res = self._make_raw_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 403)
        self.assertIn("error", res)
        self.assertEqual(resp_headers.get("access-control-allow-origin"), "http://localhost:3000")

        # POST run with read-only key (lacks execute permission) -> 403
        exec_headers = {"X-API-Key": self.read_key, "Origin": "http://localhost:3000"}
        status, resp_headers, res = self._make_raw_request("/api/v2/run", method="POST", body={"plugin_id": "bubble_sort"}, headers=exec_headers)
        self.assertEqual(status, 403)
        self.assertIn("error", res)
        self.assertEqual(resp_headers.get("access-control-allow-origin"), "http://localhost:3000")

    def test_no_credentials_header_emitted(self):
        """Access-Control-Allow-Credentials header is never emitted."""
        headers = {"X-API-Key": self.read_key, "Origin": "http://localhost:3000"}
        status, resp_headers, res = self._make_raw_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 200)
        self.assertNotIn("access-control-allow-credentials", resp_headers)

class TestSEC05TrustedProxySupport(unittest.TestCase):
    """
    Automated tests for SEC-05 Trusted Proxy Support:
    1. Existing direct-client behavior when trusted-proxy support is disabled.
    2. Forwarded headers supplied by an untrusted peer are ignored.
    3. A trusted immediate peer with a valid single-hop forwarding chain resolves the correct client.
    4. A valid multi-hop chain resolves the first untrusted client address from the right.
    5. A trusted proxy address is not mistaken for the client when the chain identifies an untrusted client.
    6. IPv4, IPv6, and CIDR matching.
    7. Invalid configured proxy entries.
    8. Missing or malformed forwarding headers from a trusted peer fail closed.
    9. Spoofed leftmost "X-Forwarded-For" entries cannot override the actual chain resolution.
    10. IP restrictions and API-key IP whitelists use the same resolved client identity.
    11. Rate limiting uses the intended resolved identity and cannot be trivially bypassed by changing forwarded headers.
    """

    def setUp(self):
        self.config_path = Path("saves/test_sec05_config.json")
        self.keys_path = Path("saves/test_sec05_keys.json")
        self.log_path = Path("saves/test_sec05_access.log")

        self.server = SecureRESTAPIServer(
            config_path=str(self.config_path),
            keys_path=str(self.keys_path)
        )
        self.server.config.enabled = True
        self.server.config.host = "127.0.0.1"
        self.server.config.port = 8891
        self.server.config.require_api_key = True
        self.server.config.log_file = str(self.log_path)
        self.server.config.log_all_requests = True

        self.read_key = self.server.create_key("read_key", permissions=["read"])

    def tearDown(self):
        if self.server.is_running():
            self.server.stop()
        for p in [self.config_path, self.keys_path, self.log_path]:
            if p.exists():
                p.unlink()

    def _make_request(self, path, method="GET", body=None, headers=None):
        url = f"http://127.0.0.1:8891{path}"
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

    def test_disabled_by_default_and_direct_client_behavior(self):
        """Requirement 1: Trusted proxy disabled by default; peer IP used and X-Forwarded-For ignored."""
        self.assertFalse(self.server.config.enable_trusted_proxy)
        self.assertEqual(self.server.config.trusted_proxies, [])

        self.server.start()
        time.sleep(0.05)

        # X-Forwarded-For supplied by untrusted peer when feature is disabled -> IGNORED
        headers = {"X-API-Key": self.read_key, "X-Forwarded-For": "203.0.113.195"}
        status, res = self._make_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 200)
        self.assertEqual(res["status"], "ok")

    def test_untrusted_peer_forwarded_headers_ignored(self):
        """Requirement 2: When feature enabled but immediate TCP peer is not in trusted_proxies, forwarded headers are ignored."""
        self.server.config.enable_trusted_proxy = True
        self.server.config.trusted_proxies = ["10.0.0.1"]  # 127.0.0.1 is NOT trusted
        self.server.start()
        time.sleep(0.05)

        headers = {"X-API-Key": self.read_key, "X-Forwarded-For": "203.0.113.195"}
        status, res = self._make_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 200)

    def test_trusted_peer_single_hop_chain(self):
        """Requirement 3: Trusted immediate peer with valid single-hop X-Forwarded-For resolves correct client."""
        self.server.config.enable_trusted_proxy = True
        self.server.config.trusted_proxies = ["127.0.0.1"]
        self.server.config.block_unknown_ips = True
        self.server.config.allowed_ips = ["203.0.113.195"]  # Only client allowed

        self.server.start()
        time.sleep(0.05)

        # 1. Allowed client IP forwarded -> 200 OK
        headers = {"X-API-Key": self.read_key, "X-Forwarded-For": "203.0.113.195"}
        status, res = self._make_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 200)

        # 2. Blocked client IP forwarded -> 403 Forbidden
        headers = {"X-API-Key": self.read_key, "X-Forwarded-For": "198.51.100.1"}
        status, res = self._make_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 403)
        self.assertIn("blokkolva", res["error"])

    def test_multi_hop_chain_right_to_left_resolution_and_spoof_resistance(self):
        """Requirements 4, 5, 9: Traverses right to left, skips trusted proxies, selects first untrusted client, ignores spoofed leftmost entries."""
        self.server.config.enable_trusted_proxy = True
        # 127.0.0.1, 10.0.0.0/8, and 172.16.0.0/12 are trusted proxies
        self.server.config.trusted_proxies = ["127.0.0.1", "10.0.0.0/8", "172.16.0.0/12"]
        self.server.config.block_unknown_ips = True
        self.server.config.allowed_ips = ["203.0.113.50"]

        self.server.start()
        time.sleep(0.05)

        # Chain: "1.1.1.1, 203.0.113.50, 10.0.0.1"
        # Rightmost is 10.0.0.1 (trusted -> skip), next right is 203.0.113.50 (untrusted -> target client!)
        # Leftmost 1.1.1.1 is ignored!
        headers = {
            "X-API-Key": self.read_key,
            "X-Forwarded-For": "1.1.1.1, 203.0.113.50, 10.0.0.1"
        }
        status, res = self._make_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 200)

        # Verify that if 203.0.113.50 is not allowed, it gets blocked despite 1.1.1.1 or 10.0.0.1
        self.server.config.allowed_ips = ["1.1.1.1"]  # Spoofed IP allowed, but real resolved client is 203.0.113.50
        status, res = self._make_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 403)  # Blocked! Spoof failed!

    def test_ipv4_ipv6_and_cidr_matching(self):
        """Requirement 6: IPv4, IPv6, and CIDR network parsing and matching."""
        from core.rest_api import is_ip_in_trusted_proxies, validate_trusted_proxies

        proxies = ["127.0.0.1", "10.0.0.0/8", "2001:db8::/32", "192.168.1.100"]
        self.assertEqual(validate_trusted_proxies(proxies), proxies)

        # IPv4 exact
        self.assertTrue(is_ip_in_trusted_proxies("127.0.0.1", proxies))
        self.assertFalse(is_ip_in_trusted_proxies("127.0.0.2", proxies))

        # IPv4 CIDR
        self.assertTrue(is_ip_in_trusted_proxies("10.254.1.2", proxies))
        self.assertFalse(is_ip_in_trusted_proxies("11.0.0.1", proxies))

        # IPv6 CIDR
        self.assertTrue(is_ip_in_trusted_proxies("2001:db8:ffff::1", proxies))
        self.assertFalse(is_ip_in_trusted_proxies("2001:db9::1", proxies))

    def test_invalid_configured_proxy_entries_rejected(self):
        """Requirement 7: Invalid configured proxy entries raise ValueError and are clearly rejected."""
        from core.rest_api import validate_trusted_proxies, RESTConfig

        invalid_entries = [
            ["300.300.300.300"],
            ["10.0.0.0/99"],
            ["invalid_hostname"],
            ["2001:xyz::1"],
        ]
        for inv in invalid_entries:
            with self.assertRaises(ValueError):
                validate_trusted_proxies(inv)

            with self.assertRaises(ValueError):
                RESTConfig(enable_trusted_proxy=True, trusted_proxies=inv)

    def test_unconditional_trusted_proxies_type_validation(self):
        """PR #17 Final Hardening 2: RESTConfig.__post_init__() unconditionally validates trusted_proxies types."""
        from core.rest_api import RESTConfig

        invalid_types = [None, "127.0.0.1", 123, {"ip": "127.0.0.1"}]
        for inv in invalid_types:
            with self.assertRaises(ValueError):
                RESTConfig(trusted_proxies=inv)

        # Valid default empty list and valid IP/CIDR tuples/lists initialize successfully
        cfg_empty = RESTConfig(trusted_proxies=[])
        self.assertEqual(cfg_empty.trusted_proxies, [])

        cfg_valid = RESTConfig(trusted_proxies=["127.0.0.1", "10.0.0.0/8", "2001:db8::/32"])
        self.assertEqual(cfg_valid.trusted_proxies, ["127.0.0.1", "10.0.0.0/8", "2001:db8::/32"])

    def test_missing_or_malformed_forwarded_headers_fail_closed(self):
        """Requirement 8: Missing or malformed forwarding headers from trusted peer fail closed with 403."""
        self.server.config.enable_trusted_proxy = True
        self.server.config.trusted_proxies = ["127.0.0.1"]
        self.server.start()
        time.sleep(0.05)

        # 1. Missing header
        headers_no_ff = {"X-API-Key": self.read_key}
        status, res = self._make_request("/api/v2/status", headers=headers_no_ff)
        self.assertEqual(status, 403)
        self.assertIn("resolution failure", res["error"].lower())

        # 2. Empty header
        headers_empty = {"X-API-Key": self.read_key, "X-Forwarded-For": "   "}
        status, res = self._make_request("/api/v2/status", headers=headers_empty)
        self.assertEqual(status, 403)

        # 3. Malformed IP
        headers_malformed = {"X-API-Key": self.read_key, "X-Forwarded-For": "203.0.113.1, invalid_ip"}
        status, res = self._make_request("/api/v2/status", headers=headers_malformed)
        self.assertEqual(status, 403)

        # 4. Trailing comma or empty element
        headers_comma = {"X-API-Key": self.read_key, "X-Forwarded-For": "203.0.113.1, "}
        status, res = self._make_request("/api/v2/status", headers=headers_comma)
        self.assertEqual(status, 403)

    def test_all_trusted_proxy_chain_fails_closed(self):
        """Security Fix 1: When all hops in X-Forwarded-For chain are trusted proxies, resolution fails closed (403)."""
        self.server.config.enable_trusted_proxy = True
        self.server.config.trusted_proxies = ["127.0.0.1", "10.0.0.0/8"]
        self.server.start()
        time.sleep(0.05)

        # Chain containing ONLY trusted proxies (no untrusted client IP identified)
        headers = {"X-API-Key": self.read_key, "X-Forwarded-For": "10.0.0.1, 10.0.0.2"}
        status, res = self._make_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 403)
        self.assertIn("resolution failure", res["error"].lower())
        self.assertIn("trusted proxies", res["error"].lower())

    def test_missing_or_invalid_peer_address_fails_closed(self):
        """Security Fix 2: Missing or invalid direct peer socket address fails closed without inventing 127.0.0.1."""
        from unittest.mock import MagicMock
        from core.rest_api import SecureRESTHandler, RESTConfig

        handler = SecureRESTHandler.__new__(SecureRESTHandler)
        handler.rest_config = RESTConfig(enable_trusted_proxy=True, trusted_proxies=["127.0.0.1"])

        # 1. Missing client_address
        handler.client_address = None
        resolved_ip, err = handler.resolve_client_ip()
        self.assertIsNone(resolved_ip)
        self.assertIn("peer address unavailable", err.lower())

        # 2. Invalid peer IP string
        handler.client_address = ("not_an_ip_addr", 12345)
        resolved_ip, err = handler.resolve_client_ip()
        self.assertIsNone(resolved_ip)
        self.assertIn("invalid direct socket peer ip address", err.lower())

    def test_duplicate_forwarded_headers_rejected(self):
        """Security Fix 3: Ambiguous duplicate X-Forwarded-For header fields fail closed with resolution error (403)."""
        from unittest.mock import MagicMock
        from core.rest_api import SecureRESTHandler, RESTConfig

        handler = SecureRESTHandler.__new__(SecureRESTHandler)
        handler.rest_config = RESTConfig(enable_trusted_proxy=True, trusted_proxies=["127.0.0.1"])
        handler.client_address = ("127.0.0.1", 54321)

        mock_headers = MagicMock()
        mock_headers.get_all.return_value = ["203.0.113.1", "203.0.113.2"]
        mock_headers.get.return_value = "203.0.113.1"
        handler.headers = mock_headers

        resolved_ip, err = handler.resolve_client_ip()
        self.assertIsNone(resolved_ip)
        self.assertIn("ambiguous duplicate x-forwarded-for headers", err.lower())

    def test_ip_restrictions_and_api_key_whitelist_same_identity(self):
        """Requirement 10: Allowed IP checks and API-key IP whitelists both use the same resolved client identity."""
        whitelisted_key = self.server.create_key("wl_key", permissions=["read"], ip_whitelist=["203.0.113.99"])

        self.server.config.enable_trusted_proxy = True
        self.server.config.trusted_proxies = ["127.0.0.1"]
        self.server.config.block_unknown_ips = True
        self.server.config.allowed_ips = ["203.0.113.99", "203.0.113.100"]

        self.server.start()
        time.sleep(0.05)

        # Resolved IP 203.0.113.99 matches both allowed_ips AND key whitelist -> 200 OK
        headers = {"X-API-Key": whitelisted_key, "X-Forwarded-For": "203.0.113.99"}
        status, res = self._make_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 200)

        # Resolved IP 203.0.113.100 passes allowed_ips but fails key whitelist -> 403
        headers = {"X-API-Key": whitelisted_key, "X-Forwarded-For": "203.0.113.100"}
        status, res = self._make_request("/api/v2/status", headers=headers)
        self.assertEqual(status, 403)
        self.assertIn("whitelist", res["error"].lower())

    def test_rate_limiting_uses_resolved_identity(self):
        """Requirement 11: Rate limiting uses intended resolved identity and cannot be bypassed by changing headers when untrusted or spoofing."""
        from core.rest_api import RateLimiter, SecureRESTHandler
        SecureRESTHandler.rate_limiter = RateLimiter()

        limited_key = self.server.create_key("l_key", permissions=["read"], rate_limit=2)

        self.server.config.enable_trusted_proxy = True
        self.server.config.trusted_proxies = ["127.0.0.1"]
        self.server.config.block_unknown_ips = True
        self.server.config.allowed_ips = ["203.0.113.77"]

        self.server.start()
        time.sleep(0.05)

        headers = {"X-API-Key": limited_key, "X-Forwarded-For": "203.0.113.77"}
        s1, _ = self._make_request("/api/v2/status", headers=headers)
        s2, _ = self._make_request("/api/v2/status", headers=headers)
        s3, res3 = self._make_request("/api/v2/status", headers=headers)

        self.assertEqual(s1, 200)
        self.assertEqual(s2, 200)
        self.assertEqual(s3, 403)
        self.assertIn("rate limit", res3["error"].lower())

    def test_global_ip_rate_limit_uses_resolved_client_ip(self):
        """PR #17 Final Hardening 1: Genuine global IP rate-limit test. Requests from same resolved client IP share global bucket even across different API keys."""
        from core.rest_api import RateLimiter, SecureRESTHandler
        SecureRESTHandler.rate_limiter = RateLimiter()

        # Create two separate API keys with high per-key limits (100/min each)
        key1 = self.server.create_key("k1", permissions=["read"], rate_limit=100)
        key2 = self.server.create_key("k2", permissions=["read"], rate_limit=100)

        self.server.config.enable_trusted_proxy = True
        self.server.config.trusted_proxies = ["127.0.0.1"]
        self.server.config.block_unknown_ips = False
        # Set GLOBAL rate limit to 2 requests/min
        self.server.config.rate_limit_global_per_min = 2

        self.server.start()
        time.sleep(0.05)

        client_a = "203.0.113.88"
        client_b = "203.0.113.89"

        # 1. Request 1 from Client A using Key 1 -> 200 OK (Global bucket global:203.0.113.88 count=1)
        s1, _ = self._make_request("/api/v2/status", headers={"X-API-Key": key1, "X-Forwarded-For": client_a})
        self.assertEqual(s1, 200)

        # 2. Request 2 from Client A using DIFFERENT Key 2 -> 200 OK (Global bucket global:203.0.113.88 count=2)
        s2, _ = self._make_request("/api/v2/status", headers={"X-API-Key": key2, "X-Forwarded-For": client_a})
        self.assertEqual(s2, 200)

        # 3. Request 3 from Client A using Key 1 -> 403 Forbidden (Global rate limit exceeded for Client A)
        s3, res3 = self._make_request("/api/v2/status", headers={"X-API-Key": key1, "X-Forwarded-For": client_a})
        self.assertEqual(s3, 403)
        self.assertIn("global rate limit", res3["error"].lower())

        # 4. Request 1 from DIFFERENT Client B using Key 1 -> 200 OK (Client B uses separate bucket global:203.0.113.89)
        s_b, _ = self._make_request("/api/v2/status", headers={"X-API-Key": key1, "X-Forwarded-For": client_b})
        self.assertEqual(s_b, 200)

if __name__ == "__main__":
    unittest.main()
