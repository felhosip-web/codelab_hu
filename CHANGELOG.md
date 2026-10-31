# Changelog

All notable changes to CodeLab HU are documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

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
