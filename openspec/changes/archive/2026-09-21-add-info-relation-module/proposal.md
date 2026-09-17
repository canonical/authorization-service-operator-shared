# Change Proposal: Add Authorization Service Info Relation Module

## Executive Summary
This proposal adds the `authorization_service_operator_shared.info` module providing `AuthorizationServiceInfo`, `AuthorizationServiceInfoProvider`, and `AuthorizationServiceInfoRequirer` to `authorization-service-operator-shared`. This module allows Charmed Authorization Service operator family members (Server, Worker, Listener) to share workload versions, database schema migration completion status, OpenFGA model ID, and database connection credentials/secrets over the `authorization-service-info` Juju relation without needing legacy charmcraft libraries or requiring worker/listener charms to integrate directly with PostgreSQL.

## Motivation
Charmcraft libraries deprecation and blocked registration for new packages require distributing relation helpers directly within shared packages. In alignment with Authentik-style operator architecture, the Server charm is solely responsible for executing database schema migrations and managing the direct PostgreSQL relation. The Server charm shares its `workload_version`, database `migration_version`, OpenFGA store/model IDs, and database connection credentials (`db_host`, `db_port`, `db_name`, `db_user`, `db_secret_id`) with dependent Worker and Listener charms via `authorization-service-info` and Juju secrets (`db-password`). Requirer charms inspect these credentials to connect to PostgreSQL without requiring separate direct Juju database relations.

## Proposed Changes
1. **Module `authorization_service_operator_shared.info`**:
   - `AuthorizationServiceInfo`: Dataclass container for `workload_version`, `migration_version`, `openfga_store_id`, `openfga_model_id`, `db_host`, `db_port`, `db_name`, `db_user`, `db_secret_id`, and `db_password` (retrieved from secret) with `is_ready`, `is_migration_ready`, and `is_db_ready` properties.
   - `AuthorizationServiceInfoProvider`: Juju provider wrapper emitting `AuthorizationServiceInfoRelationReadyEvent` when a relation joins and providing `publish_info(...)` to create/update Juju secrets (`db-password`), grant relation access, and write versions and connection details into the application databag when leader. Handles `relation_broken` to revoke secret grants for departing relations and execute `secret.remove_all_revisions()` when no active relations remain.
   - `AuthorizationServiceInfoRequirer`: Juju requirer wrapper emitting `AuthorizationServiceInfoBrokenEvent` and providing `get_info()` to read databag details and retrieve database secrets using `secret.get_content(refresh=True)`.
2. **Module `authorization_service_operator_shared.database`**:
   - `DatabaseConfig.from_info(info)`: Factory method creating `DatabaseConfig` directly from `AuthorizationServiceInfo`.
3. **Public Interface Exports**: Export `AuthorizationServiceInfo`, `AuthorizationServiceInfoProvider`, and `AuthorizationServiceInfoRequirer` in `authorization_service_operator_shared.__init__.py`.
4. **Unit Tests**: Implement complete unit tests in `tests/unit/test_info.py` covering model readiness, leader/non-leader provider publishing, secret revocation/cleanup on relation broken, and requirer parsing.

## Non-Goals
- Executing database schema migrations inside requirer charms (migrations remain exclusive to the Server charm).
