# Technical Design: Add Integration Config Dataclasses, Istio Ingress, and Peer Data

## Overview
This design outlines the architecture for integrating typed connection dataclasses and route management into `authorization-service-operator-shared`.

## Architectural Design

### 1. Data Object + Relation Handler Dual Pattern
To combine type safety with Juju event handling, integration modules implement two complementary concepts:

```
+------------------------------------+       +------------------------------------+
|       Relation Handler             | ----> |         Config Dataclass           |
| (e.g., DatabaseRelationHandler)    |       |       (e.g., DatabaseConfig)       |
+------------------------------------+       +------------------------------------+
| - wraps Juju requirer library      |       | - immutable connection parameters  |
| - manages relation lifecycle       |       | - dsn property calculation         |
| - exposes .config / .dsn           |       | - to_env_vars() mapping            |
+------------------------------------+       +------------------------------------+
```

### 2. Detailed Module Specs

#### `authorization_service_operator_shared.database`
- `DatabaseConfig`: `@dataclass(frozen=True, slots=True)` with fields `host`, `port`, `dbname`, `username`, `password`.
- Properties:
  - `is_ready`: `bool(host and port and dbname and username and password)`
  - `dsn`: `"postgres://<user>:<pass>@<host>:<port>/<db>"`
- Methods:
  - `to_env_vars()`: Returns `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`.
  - `load(requirer)`: Reads `DatabaseRequires` relations and extracts endpoint parameters.

#### `authorization_service_operator_shared.openfga`
- `OpenFGAConfig`: Connection parameters (`address`, `token`, `store_id`, `authorization_model_id`). Parses `api_scheme` and `api_host` via `urlparse`.
- `OpenFGAModelData`: Model ID container with `load(source)` supporting both string and dictionary databag sources.

#### `authorization_service_operator_shared.sts`
- `StsConfig`: JWKS URL, gRPC address, HTTP endpoint address, and TLS flag. Exports `STS_ADDRESS`, `STS_USE_TLS`, `STS_JWKS_URI`, and `EXTAUTHZ_JWK_SET_URL`.
- `STSRelationHandler`: Exposes `.config` property, `.get_env_vars()`, and `.to_env_vars()` method alias to satisfy `EnvVarConvertible`.

#### `authorization_service_operator_shared.observability`
- `TracingConfig`: OTLP endpoint and configurable `service_name` settings exporting `TELEMETRY_ENABLED`, `OTEL_EXPORTER_OTLP_ENDPOINT`, and `OTEL_SERVICE_NAME`.
- `MetricsRelationHandler` & `GrafanaDashboardHandler`: Centralized Prometheus scrapers and automated dashboard integration. Uses top-level `try/except ImportError` fallback classes for decoupling.

#### `authorization_service_operator_shared.ingress`
- `IstioIngressIntegration`: Wraps `IstioIngressRouteRequirer` from `charmlibs.interfaces.istio_ingress_route` to calculate public URLs and submit HTTP/gRPC ingress routes. Uses top-level `try/except ImportError` fallback class for decoupling.

#### `authorization_service_operator_shared.peer`
- `PeerData`: JSON-encoded read/write accessor for app-level peer databags (`self.model.get_relation(PEER_INTEGRATION_NAME)`).

### 3. Decoupled Module Import Strategy
All integration modules (`database.py`, `sts.py`, `kafka.py`, `observability.py`, `ingress.py`) define top-level `try/except ImportError` fallback classes for optional Charmhub (`lib/charms/...`) and PyPI libraries. This ensures that consumer charms can import `authorization_service_operator_shared` without raising `ModuleNotFoundError`, even if they do not vendor specific optional relation libraries.
