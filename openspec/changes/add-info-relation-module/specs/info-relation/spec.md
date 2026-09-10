## ADDED Requirements

### Requirement: Authorization Service Info Relation Provider
`AuthorizationServiceInfoProvider` SHALL handle `relation_joined` on the `authorization-service-info` endpoint, emit `AuthorizationServiceInfoRelationReadyEvent`, and allow leader units to publish `workload_version` and `migration_version` to the application databag.

#### Scenario: Leader unit publishes versions
- **WHEN** `publish_info(workload_version, migration_version)` is called on a leader unit
- **THEN** it SHALL write `workload_version` and `migration_version` into `relation.data[self.charm.app]`.

#### Scenario: Non-leader unit publish call
- **WHEN** `publish_info(...)` is called on a non-leader unit
- **THEN** it SHALL do nothing and return without writing to relation data.

#### Scenario: Relation joined event
- **WHEN** a remote unit joins the `authorization-service-info` relation
- **THEN** `AuthorizationServiceInfoProvider` SHALL emit `AuthorizationServiceInfoRelationReadyEvent`.

### Requirement: Authorization Service Info Relation Requirer
`AuthorizationServiceInfoRequirer` SHALL handle `relation_broken`, emit `AuthorizationServiceInfoBrokenEvent`, and parse `AuthorizationServiceInfo` from the relation application databag.

#### Scenario: Reading valid info from databag
- **WHEN** `get_info()` is called and a valid relation exists with `workload_version` and `migration_version`
- **THEN** it SHALL return an `AuthorizationServiceInfo` object with `is_ready` evaluating to `True`.

#### Scenario: Reading when no relation exists
- **WHEN** `get_info()` is called and no `authorization-service-info` relation exists
- **THEN** it SHALL return `None`.
