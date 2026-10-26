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

if __name__ == "__main__":
    unittest.main()
