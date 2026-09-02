## ADDED Requirements

### Requirement: Database Connection Configuration Object
The library SHALL provide a `DatabaseConfig` frozen dataclass containing `host`, `port`, `dbname`, `username`, and `password`.

#### Scenario: DSN string rendering
- **WHEN** all connection parameters (`host`, `port`, `dbname`, `username`, `password`) are non-empty
- **THEN** the `dsn` property SHALL return a PostgreSQL connection string formatted as `postgres://<username>:<password>@<host>:<port>/<dbname>`

#### Scenario: Environment variables rendering
- **WHEN** `to_env_vars()` is called on a populated `DatabaseConfig`
- **THEN** it SHALL return a dictionary containing `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`
