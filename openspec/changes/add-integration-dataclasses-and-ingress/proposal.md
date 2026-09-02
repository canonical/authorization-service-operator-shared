# Change Proposal: Add Integration Config Dataclasses, Istio Ingress, and Peer Data

## Executive Summary
This proposal adds strongly-typed integration config dataclasses (`DatabaseConfig`, `OpenFGAConfig`, `OpenFGAModelData`, `StsConfig`, `TracingConfig`), `IstioIngressIntegration`, and `PeerData` to `authorization-service-operator-shared`. Moving these wrappers into the shared library enables all authorization service charms (Server, Proxy, Sidecar) to share connection models, DSN generation, OTLP tracing setup, Istio Gateway API route submission, and peer databag handling without code duplication.

## Motivation
Previously, `DatabaseConfig`, `OpenFGAIntegrationData`, `StsConfig`, `TracingConfig`, `IstioIngressIntegration`, and `PeerData` were implemented locally in each operator's `src/integrations.py`. As the authorization service operator family expands, these data objects and integration helpers are identical across operators. Moving them to `authorization-service-operator-shared` establishes a unified interface for workload environment variable rendering, migration CLI invocation (DSN string formatting), and external HTTP/gRPC route submission via Istio Gateway API.

## Proposed Changes
1. **`authorization_service_operator_shared.database`**: Add `DatabaseConfig` dataclass with `is_ready`, `dsn`, `to_env_vars()`, and `load(requirer)` classmethod. Expose `.config` and `.dsn` properties on `DatabaseRelationHandler`.
2. **`authorization_service_operator_shared.openfga`**: Add `OpenFGAConfig` and `OpenFGAModelData` dataclasses with `api_scheme`, `api_host`, `to_env_vars()`, and `load(source)` classmethods.
3. **`authorization_service_operator_shared.sts`**: Add `StsConfig` dataclass with `is_ready`, `to_env_vars()`, and `load(requirer)` classmethod. Expose `.config` property on `STSRelationHandler`.
4. **`authorization_service_operator_shared.observability`**: Add `TracingConfig` dataclass with `to_env_vars()` and `load(requirer)` classmethod.
5. **`authorization_service_operator_shared.ingress`**: Create new module providing `IstioIngressIntegration` to manage Istio Ingress Gateway API route configurations via `charmlibs.interfaces.istio_ingress_route`.
6. **`authorization_service_operator_shared.peer`**: Create new module providing `PeerData` for JSON-encoded peer relation app-databag access.

## Non-Goals
- Modifying underlying Juju relation interfaces or external charm libraries (`charms.data_platform_libs`, `charms.openfga_k8s`, etc.).
- Adding non-standard environment variable keys beyond those required by the authorization service workload suite.
