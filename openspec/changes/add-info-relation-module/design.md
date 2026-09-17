# Technical Design: Add Authorization Service Info Relation Module

## Overview
This technical design details the implementation of the `authorization_service_operator_shared.info` module for managing the `authorization-service-info` relation across Charmed Authorization Service operators.

## Architectural Design

### 1. Data Schema
`AuthorizationServiceInfo` is a dataclass representing version metadata and database credentials exchanged over the relation:
- `workload_version`: `str | None` - Version of the application workload running in the container.
- `migration_version`: `str | None` - Version of database schema migrations completed by the Server charm.
- `openfga_store_id`: `str | None` - OpenFGA store ID created by the Server charm.
- `openfga_model_id`: `str | None` - OpenFGA model ID created by the Server charm.
- `db_host`: `str | None` - PostgreSQL database host.
- `db_port`: `str | None` - PostgreSQL database port.
- `db_name`: `str | None` - PostgreSQL database name.
- `db_user`: `str | None` - PostgreSQL database username.
- `db_secret_id`: `str | None` - Juju secret ID containing `db-password`.
- `db_password`: `str | None` - Database password retrieved from Juju secret.
- `is_ready`: Property returning `True` if `workload_version` and `migration_version` are non-empty.
- `is_db_ready`: Property returning `True` if `db_host`, `db_port`, `db_name`, `db_user`, and `db_password` are non-empty strings.

### 2. Relation Provider (`AuthorizationServiceInfoProvider`)
- Inherits from `ops.Object`.
- Exposes `self.on.authorization_service_info_relation_ready` (`AuthorizationServiceInfoReadyEvent`).
- Handles `relation_joined` events on `authorization-service-info` and emits `authorization_service_info_relation_ready`.
- `publish_info(...)`: Leader-only method that writes `workload_version`, `migration_version`, `openfga_store_id`, `openfga_model_id`, `db_host`, `db_port`, `db_name`, `db_user`, and `db_secret_id` to `relation.data[self.charm.app]`. Automatically creates/updates Juju secret containing `{"db-password": db_password}` and grants access to connected relations.

### 3. Relation Requirer (`AuthorizationServiceInfoRequirer`)
- Inherits from `ops.Object`.
- Exposes `self.on.authorization_service_info_broken` (`AuthorizationServiceInfoBrokenEvent`).
- Handles `relation_broken` events on `authorization-service-info` and emits `authorization_service_info_broken`.
- `get_info() -> AuthorizationServiceInfo | None`: Reads relation app databag, fetches secret content via `db_secret_id`, and returns an `AuthorizationServiceInfo` instance (or `None` if relation is absent or missing data).

### 4. Sequence & Status Lifecycle
```
+----------------+            +---------------------+            +----------------+
|  Server Charm  |            | authorization-info  |            |  Worker Charm  |
+----------------+            +---------------------+            +----------------+
| Run migration  |                                               |                |
| Add DB secret  |                                               |                |
|                | <--- relation_joined -----                    | Join relation  |
| Grant DB secret|                                               |                |
| Publish info   | ---- app_databag write --> [ credentials ] -> | get_info()     |
|                |                                               | Read secret    |
|                |                                               | Config DB      |
+----------------+                                               +----------------+
```
If the worker's workload version does not match `info.migration_version`, the worker sets `WaitingStatus("Waiting for the server to run migration")`.
