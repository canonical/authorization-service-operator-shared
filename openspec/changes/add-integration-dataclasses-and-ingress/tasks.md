## 1. Database Configuration Dataclass

- [x] 1.1 Implement `DatabaseConfig` frozen dataclass in `authorization_service_operator_shared/database.py` with `host`, `port`, `dbname`, `username`, `password`, `is_ready`, `dsn`, `to_env_vars()`, and `load(requirer)` classmethod.
- [x] 1.2 Expose `.config` and `.dsn` properties on `DatabaseRelationHandler`.

## 2. OpenFGA Configuration Dataclasses

- [x] 2.1 Implement `OpenFGAConfig` frozen dataclass in `authorization_service_operator_shared/openfga.py` with URL parsing (`api_scheme`, `api_host`) and environment variable conversion.
- [x] 2.2 Implement `OpenFGAModelData` frozen dataclass in `authorization_service_operator_shared/openfga.py` with `load(source)` classmethod supporting dict and string inputs.
- [x] 2.3 Expose `.config` property on `OpenFGARelationHandler`.

## 3. STS & Observability Configuration Dataclasses

- [x] 3.1 Implement `StsConfig` frozen dataclass in `authorization_service_operator_shared/sts.py` with `load(requirer)` and `to_env_vars()`.
- [x] 3.2 Implement `TracingConfig` frozen dataclass in `authorization_service_operator_shared/observability.py` with `load(requirer)` and OpenTelemetry environment variable conversion.

## 4. Istio Ingress & Peer Data

- [x] 4.1 Implement `IstioIngressIntegration` in `authorization_service_operator_shared/ingress.py` encapsulating `IstioIngressRouteRequirer`.
- [x] 4.2 Implement `PeerData` in `authorization_service_operator_shared/peer.py` with JSON serialization for app-level peer databags.
- [x] 4.3 Export all new dataclasses and handlers in `authorization_service_operator_shared/__init__.py`.

## 5. Testing & Verification

- [x] 5.1 Verify that `authorization-service-operator` builds cleanly against `authorization-service-operator-shared`.
- [x] 5.2 Execute static code quality check `uv run ruff check .` across shared library.
- [x] 5.3 Run operator unit tests `uv run pytest tests/unit` ensuring 100% pass rate.
