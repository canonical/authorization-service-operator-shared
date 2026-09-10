# Technical Design: Add Authorization Service Info Relation Module

## Overview
This technical design details the implementation of the `authorization_service_operator_shared.info` module for managing the `authorization-service-info` relation across Charmed Authorization Service operators.

## Architectural Design

### 1. Data Schema
`AuthorizationServiceInfo` is a frozen dataclass representing version metadata exchanged over the relation:
- `workload_version`: `str | None` - Version of the application workload running in the container.
- `migration_version`: `str | None` - Version of database schema migrations completed by the Server charm.
- `is_ready`: Property returning `True` if both `workload_version` and `migration_version` are non-empty strings.

### 2. Relation Provider (`AuthorizationServiceInfoProvider`)
- Inherits from `ops.Object`.
- Exposes `self.on.authorization_service_info_relation_ready` (`AuthorizationServiceInfoRelationReadyEvent`).
- Handles `relation_joined` events on `authorization-service-info` and emits `authorization_service_info_relation_ready`.
- `publish_info(workload_version: str, migration_version: str)`: Leader-only method that writes `workload_version` and `migration_version` to `relation.data[self.charm.app]`.

### 3. Relation Requirer (`AuthorizationServiceInfoRequirer`)
- Inherits from `ops.Object`.
- Exposes `self.on.authorization_service_info_broken` (`AuthorizationServiceInfoBrokenEvent`).
- Handles `relation_broken` events on `authorization-service-info` and emits `authorization_service_info_broken`.
- `get_info() -> AuthorizationServiceInfo | None`: Reads the relation app databag and returns an `AuthorizationServiceInfo` instance (or `None` if relation is absent or missing data).

### 4. Sequence & Status Lifecycle
```
+----------------+            +---------------------+            +----------------+
|  Server Charm  |            | authorization-info  |            |  Worker Charm  |
+----------------+            +---------------------+            +----------------+
| Run migration  |                                               |                |
| peer_data set  |                                               |                |
|                | <--- relation_joined -----                    | Join relation  |
| Emit ready evt |                                               |                |
| Publish info   | ---- app_databag write --> [ versions ] ----> | get_info()     |
|                |                                               | Compare ver    |
+----------------+                                               +----------------+
```
If the worker's workload version does not match `info.migration_version`, the worker sets `WaitingStatus("Waiting for database migration to match workload version")`.
