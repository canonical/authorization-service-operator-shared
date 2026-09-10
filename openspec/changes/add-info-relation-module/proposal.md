# Change Proposal: Add Authorization Service Info Relation Module

## Executive Summary
This proposal adds the `authorization_service_operator_shared.info` module providing `AuthorizationServiceInfo`, `AuthorizationServiceInfoProvider`, and `AuthorizationServiceInfoRequirer` to `authorization-service-operator-shared`. This module allows Charmed Authorization Service operator family members (Server, Worker, Listener) to share workload versions and database schema migration completion status over the `authorization-service-info` Juju relation without needing legacy charmcraft libraries.

## Motivation
Charmcraft libraries deprecation and blocked registration for new packages require distributing relation helpers directly within shared packages. The Server charm is solely responsible for executing database schema migrations and needs a standardized mechanism to communicate its `workload_version` and database `migration_version` (`self.peer_data[MIGRATION_COMPLETED]`) to dependent Worker and Listener charms. Requirer charms inspect these versions to ensure their local workload version matches the server's database migration version before serving traffic.

## Proposed Changes
1. **Module `authorization_service_operator_shared.info`**:
   - `AuthorizationServiceInfo`: Dataclass container for `workload_version` and `migration_version` with `is_ready` property.
   - `AuthorizationServiceInfoProvider`: Juju provider wrapper emitting `AuthorizationServiceInfoRelationReadyEvent` when a relation joins and providing `publish_info(workload_version, migration_version)` to write versions into the application databag when leader.
   - `AuthorizationServiceInfoRequirer`: Juju requirer wrapper emitting `AuthorizationServiceInfoBrokenEvent` and providing `get_info()` to read and parse version information from the application relation databag.
2. **Public Interface Exports**: Export `AuthorizationServiceInfo`, `AuthorizationServiceInfoProvider`, and `AuthorizationServiceInfoRequirer` in `authorization_service_operator_shared.__init__.py`.
3. **Unit Tests**: Implement complete unit tests in `tests/unit/test_info.py`.

## Non-Goals
- Executing database schema migrations inside requirer charms (migrations remain exclusive to the Server charm).
