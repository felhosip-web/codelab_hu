# Changelog

All notable changes to CodeLab HU are documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

## [3.8.4] - 2026-11-03

### Core Maintenance & Plugin Reload Isolation (Bizt-PR#4 — Core Maintenance & Plugin Reload Isolation)
- **Exclude "workspace_config.json" from StateManager Discovery (P4-01)**:
  - Added `workspace_config.json` to `EXCLUDE_FILES` set in `StateManager.list_saves()` in `core/engine.py`.
  - Prevents user-specific workspace configuration files from entering state file discovery, session loading, or state management workflows while preserving normal workspace configuration loading and saving.
  - Updated documentation in `core/README.md` and added regression tests in `tests/test_engine.py`.
- **Truly Targeted PluginLoader.reload(target) (P4-02)**:
  - Refactored `PluginLoader` in `core/plugin_system.py` to share folder loading logic across `load_all()` and `reload(target)` via `_load_plugin_folder()`.
  - Tracked folder associations in `plugin_folders` to reliably map plugin IDs and features to their defining module directories.
  - `reload()` without target retains full reload of all plugins.
  - `reload(target)` reloads only the plugin, plugin category/feature, or folder targeted, without re-importing or disturbing unrelated plugins.
  - Preserves unrelated plugin instances (`is`) and internal state across targeted reloads.
  - Only evicts targeted plugin modules from `sys.modules`, ensuring unrelated module files are not re-executed.
  - Handles missing targets and target loading errors deterministically without corrupting the existing registry or impacting unrelated plugins.
  - Added comprehensive regression tests in `tests/test_plugin_loader.py`.
- **Version Updates**:
  - Bumped `MAIN_VERSION` to `3.8.4`. (Kept `REST_API_VERSION` at `1.0.2` as the REST API HTTP contract itself remains unchanged).

## [3.8.3] - 2026-11-02

### GUI & Usability Security Improvements (Bizt-PR#3 — GUI & Usability Security Improvements)
- **Expose and Validate "allowed_ips" in REST API GUI (P3-01)**:
  - Added dedicated multiline configuration field (`allowed_ips_edit`) in `ui/rest_api_dialog.py` for configuring `allowed_ips`.
  - Added `validate_allowed_ips` validation in `core/rest_api.py` and enforce it in `RESTConfig.__post_init__` as well as the GUI save workflow.
  - Supports IPv4 addresses, IPv6 addresses, and CIDR network ranges.
  - Rejects malformed addresses and CIDR subnets with actionable GUI warning dialog without corrupting configuration or writing invalid settings to disk.
  - Correctly preserves existing configuration when unrelated settings are edited.
- **Clarify API Key Hash vs Token Wording (P3-02)**:
  - Updated API key management UI labels, tooltips, list entries, and messages in `ui/rest_api_dialog.py` to make an explicit distinction between secret API tokens and stored SHA-256 hashes.
  - Formatted API key entries in the GUI list to explicitly identify stored values as SHA-256 hashes (`HASH: ... (SHA-256 lenyomat)`).
  - Renamed copy button and action to explicitly copy the SHA-256 hash digest, and added explicit warnings in confirmation dialogs clarifying that the copied hash cannot be used for authentication.
  - Emphasized one-time secret token display upon key creation, informing users that unhashed tokens cannot be retrieved again from the system.
- **Version Updates**:
  - Bumped `MAIN_VERSION` to `3.8.3`. (Kept `REST_API_VERSION` at `1.0.2` as the REST API HTTP contract itself remains unchanged).

## [3.8.2] - 2026-11-01

### Reliability & Server Lifecycle (Bizt-PR#2 — REST API Reliability & Lifecycle)
- **RateLimiter Memory Cleanup & Synchronization (P2-02)**:
  - Added thread synchronization (`threading.Lock`) to `RateLimiter` in `core/rest_api.py` for safe concurrent request processing across server threads.
  - Implemented automatic identifier pruning: client identifiers whose sliding-window request timestamps have expired are removed from memory, avoiding unbounded memory growth.
  - Added an injectable clock (`time_func`) for deterministic testing without fragile sleeps or race conditions.
  - Maintained exact sliding-window allow/deny semantics at configured rate limits.
- **REST Server Lifecycle & GUI Shutdown (P2-03)**:
  - Updated `MainWindow.closeEvent()` in `ui/main_window.py` to ensure clean shutdown of the embedded REST server upon closing the main window without blocking or aborting application shutdown.
  - Updated `SecureRESTAPIServer.stop()` to be thread-safe, idempotent, and bounded with thread join timeouts, preventing deadlocks when invoked from the serving thread and reliably releasing sockets and terminating daemon threads.
- **Strict Content-Length Validation (P2-04)**:
  - Added strict validation for incoming HTTP `Content-Length` headers in `SecureRESTHandler.do_POST`.
  - Rejects duplicate, ambiguous, non-numeric, negative, or empty `Content-Length` headers with HTTP 400 Bad Request, preventing unhandled exceptions and server instability.
  - Retained HTTP 413 payload size enforcement for oversized requests.
- **Version Updates**:
  - Bumped `MAIN_VERSION` to `3.8.2` and `REST_API_VERSION` to `1.0.2`.

## [3.8.1] - 2026-10-31

### Security & Hardening (Bizt-PR#1 — REST API Key & IP Security Hardening)
- **CIDR-aware IPv4 and IPv6 Access Restrictions (SEC-P1-02)**:
  - Implemented `is_ip_in_network_list()` and `parse_ip_or_network()` in `core/rest_api.py` supporting IPv4/IPv6 addresses, CIDR subnet masks (`strict=False`), and unmapping of IPv4-mapped IPv6 addresses (`::ffff:192.0.2.1` -> `192.0.2.1`).
  - Applied CIDR matching and canonical IP address normalization consistently across `RESTConfig.allowed_ips` and `APIKey.ip_whitelist`.
  - Normalized direct TCP socket peer address in `resolve_client_ip()` to ensure consistent evaluation.
- **API Key IP Whitelist Persistence & Enforcement (SEC-P1-01)**:
  - Fixed `POST /api/v2/keys` to extract, validate, and persist `ip_whitelist` in the generated `APIKey` record.
  - Ensured API keys configured with IP whitelists reject unauthorized client IPs with HTTP 403.
  - Preserved backward compatibility for keys with empty whitelists (no key-level restriction).
- **Strict API Key Request Validation (SEC-P2-01)**:
  - Enforced validation on `name` (string, non-blank, max 100 characters).
  - Enforced validation on `permissions` (must be a list of strings strictly within `{"read", "write", "execute", "admin"}`).
  - Enforced validation on `rate_limit` (integer strictly within 1–10000; explicitly rejects booleans, floats, numeric strings, and out-of-range values).
  - Ensured invalid input returns HTTP 400 Bad Request without persisting partial or corrupted keys.
- **Tests & Coverage**:
  - Added comprehensive security unit and integration tests covering CIDR matching, IPv4-mapped IPv6 addresses, API key whitelist persistence, and request validation error cases in `tests/test_rest_api.py`.
- **Version Updates**:
  - Bumped `MAIN_VERSION` to `3.8.1` and `REST_API_VERSION` to `1.0.1`.
