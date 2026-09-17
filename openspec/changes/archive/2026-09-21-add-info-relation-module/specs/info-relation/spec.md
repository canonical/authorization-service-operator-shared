## ADDED Requirements

### Requirement: Authorization Service Info Relation Provider
`AuthorizationServiceInfoProvider` SHALL handle `relation_joined` on the `authorization-service-info` endpoint, emit `AuthorizationServiceInfoRelationReadyEvent`, manage Juju secrets for database credentials (`db-password`), grant secret access to connected relations, and allow leader units to publish version, OpenFGA model ID, and database connection details to the application databag.

#### Scenario: Leader unit publishes info and database secret
- **WHEN** `publish_info(...)` is called on a leader unit with `db_password`
- **THEN** it SHALL create or update a Juju secret with content `{"db-password": db_password}`, grant access to connected `authorization-service-info` relations, and write `workload_version`, `migration_version`, `openfga_store_id`, `openfga_model_id`, `db_host`, `db_port`, `db_name`, `db_user`, and `db_secret_id` into `relation.data[self.charm.app]`.

#### Scenario: Non-leader unit publish call
- **WHEN** `publish_info(...)` is called on a non-leader unit
- **THEN** it SHALL do nothing and return without writing to relation data.

#### Scenario: Relation joined event
- **WHEN** a remote unit joins the `authorization-service-info` relation
- **THEN** `AuthorizationServiceInfoProvider` SHALL emit `AuthorizationServiceInfoRelationReadyEvent`.

#### Scenario: Relation broken event on provider
- **WHEN** an `authorization-service-info` relation is broken on a leader unit
- **THEN** `AuthorizationServiceInfoProvider` SHALL revoke secret access for the departing relation via `secret.revoke(relation)`, and if no active relations remain on the endpoint, it SHALL call `secret.remove_all_revisions()` to destroy the secret.

### Requirement: Authorization Service Info Relation Requirer
`AuthorizationServiceInfoRequirer` SHALL handle `relation_broken`, emit `AuthorizationServiceInfoBrokenEvent`, retrieve database secrets using `db_secret_id`, and parse `AuthorizationServiceInfo` from the relation application databag.

#### Scenario: Reading valid info from databag
- **WHEN** `get_info()` is called and a valid relation exists with `workload_version`, `migration_version`, and database credentials/secret ID
- **THEN** it SHALL fetch the secret content for `db_secret_id` using `secret.get_content(refresh=True)` and return an `AuthorizationServiceInfo` object with `is_ready`, `is_migration_ready`, and `is_db_ready` evaluating to `True`.

#### Scenario: Reading when no relation exists
- **WHEN** `get_info()` is called and no `authorization-service-info` relation exists
- **THEN** it SHALL return `None`.
