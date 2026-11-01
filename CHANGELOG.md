# Changelog

All notable changes to CodeLab HU are documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

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
