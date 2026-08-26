## ADDED Requirements

### Requirement: Database Relation Parsing
The library SHALL provide a class `DatabaseRelationHandler` that wraps the Juju PostgreSQL relation (`postgresql_client` interface) and dynamically extracts the credentials to expose them as a dictionary of environment variables.

#### Scenario: Successful credentials parsing
- **WHEN** the PostgreSQL relation is ready and contains valid host and credential keys in its Juju databag
- **THEN** the handler's `get_env_vars()` method SHALL return a dictionary with `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and `POSTGRES_SSL_MODE` populated with the corresponding values from Juju's databag
