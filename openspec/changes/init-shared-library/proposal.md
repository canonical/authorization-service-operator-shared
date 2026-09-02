## Why

The Charmed Authorization Service operator family (Server, Listener, and Worker) share several core operational requirements and Juju relation patterns (e.g., PostgreSQL credentials parsing, OpenFGA bindings, STS parameters mapping, and Prometheus metrics scraping). To eliminate code duplication, maintain consistent operational behaviors across all three operators, and simplify upgrading standard charms library interfaces, we need a cohesive, shared Python library package (`authorization-service-operator-shared`). 

In addition to relation handlers, the sister operators share identical foundational concerns: executing commands against the underlying Go binary via Pebble exec (migrations, versions, model writes), mapping proxy/log configurations, raising standard exceptions, managing Pebble planning loops, and validating container connectivity. Consolidating these modules into the shared library guarantees operational consistency.

## What Changes

- **Create Shared Library Package**: Establish a reusable Python library structure compliant with PEP 621 under the name `authorization-service-operator-shared` (namespace: `authorization_service_operator_shared`).
- **Standardized UV Packaging**: Configure the package using modern `pyproject.toml` settings, making it directly consumable by charms using Charmcraft's `uv` build backend plugin.
- **Implement Shared Connection Wrappers**:
  - `DatabaseRelationHandler`: Unified Postgres integration logic.
  - `OpenFGARelationHandler`: Unified OpenFGA connection details parser.
  - `STSRelationHandler`: Secure Token Service integration mapper.
  - `KafkaRelationHandler`: Kafka broker details mapper.
  - `MetricsRelationHandler` and `GrafanaDashboardHandler`: Centralized Prometheus scrapers and automated dashboard packaging.
- **Extract Reusable Operational Modules**:
  - `cli`: Reusable command runner utilizing Pebble exec for running migrations, checking migration statuses, fetching versions, and creating OpenFGA models.
  - `configs`: Unified charm configuration helpers to parse developer modes, proxy settings, and logging levels.
  - `exceptions`: Unified custom Juju operator exceptions hierarchy.
  - `services`: Reusable `PebbleService` and `WorkloadService` managers for declarative service layer planning, port binding, and ready-check status validation.
  - `utils`: Shared Juju-decorator utilities (such as `@leader_unit` and container connectivity guards).

## Capabilities

### New Capabilities
- `database-integration`: Standardized PostgreSQL requires handler extracting host, port, user, password, database, and SSL mode variables into environment dictionaries for Pebble container consumption.
- `openfga-integration`: OpenFGA address, store, API key, and schema mapping parser for relationship evaluation.
- `sts-integration`: Secure Token Service endpoint addresses and TLS secret mapping parser for security credentials verification.
- `kafka-integration`: Kafka topic subscription broker mappings for durable queue ingestion.
- `observability-integration`: Centralized Prometheus scraping registration and Grafana JSON dashboard loading into Juju's COS LMA stack.
- `cli-framework`: Modular CLI wrapper executing commands (`version`, `migrate`, `write-model`) via standard Pebble container exec hooks.
- `config-framework`: Reusable schema conversion methods translating standard operator configs (developer logs, proxies) into environment dictionaries.
- `exception-framework`: Standard exception hierarchies mapping operational failures across relation databags, Pebble commands, and workload configurations.
- `service-framework`: Shared service orchestrators planning Pebble layers, tracking readiness checks, and opening standard Juju ports.
- `utility-framework`: Reusable wrapper decorators ensuring leadership executions and container ready validations.

### Modified Capabilities
*(None - this is a new library)*

## Impact

- **Charms Maintenance**: Significantly reduces code duplication across the three operator charms.
- **Consistency**: Guarantees identical database parsing, security token mapping, and telemetry behaviors.
- **Packaging**: Eliminates requirement-file pollution by utilizing native Charmcraft `uv` package integration.
