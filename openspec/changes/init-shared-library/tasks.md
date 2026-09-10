## 1. Workspace & Packaging Setup

- [x] 1.1 Create a PEP 621-compliant `pyproject.toml` file declaring project metadata, `setuptools` build-backend, and base dependencies (`ops>=2.0.0`).
- [x] 1.2 Establish package directory structure under `src/authorization_service_operator_shared/` with `__init__.py`.
- [x] 1.3 Create a project README.md documenting package layout, importing patterns, and developer instructions.

## 2. Implement Common Core Framework Modules

- [x] 2.1 Implement `constants.py` containing reusable application ports, binary names, container paths, and service configurations.
- [x] 2.2 Implement `exceptions.py` establishing the custom `AuthorizationServiceCharmError` base exception and sub-exceptions (ConfigError, IntegrationDataError, WorkloadError, CreateFgaModelError).
- [x] 2.3 Implement `configs.py` containing `CharmConfig` to cleanly extract logging levels, developer modes, and HTTP/HTTPS/NO proxy variables into environment mappings.
- [x] 2.4 Implement `cli.py` containing `CommandLine` to wrap `/usr/bin/app` commands (version lookup, database migrations, and OpenFGA model creation) via Pebble exec.
- [x] 2.5 Implement `services.py` containing `PebbleService` and `WorkloadService` to safely orchestrate Pebble container layer additions, replan services, track readiness checks, and publish workload versions.
- [x] 2.6 Implement `utils.py` containing decorator helpers like `@leader_unit` and workload connectivity validation functions.

## 3. Implement Relation Integration Handlers

- [x] 3.1 Implement `database.py` containing `DatabaseRelationHandler` using PostgreSQLRequires to translate credentials into Go binary environment mappings.
- [x] 3.2 Implement `openfga.py` containing `OpenFGARelationHandler` to extract OpenFGA store IDs, authentication tokens, and server addresses.
- [x] 3.3 Implement `sts.py` containing `STSRelationHandler` to map Secure Token Service endpoints and credentials.
- [x] 3.4 Implement `kafka.py` containing `KafkaRelationHandler` to decode Kafka broker configurations.
- [x] 3.5 Implement `observability.py` containing `MetricsRelationHandler` and `GrafanaDashboardHandler` to configure Prometheus scrapes and Grafana dashboard files.

## 4. Testing & Verification

- [x] 4.1 Configure a local `pytest` testing harness.
- [x] 4.2 Write unit tests verifying that core modules (CLI command execution, configuration mapping, exceptions raising, and service layers) operate correctly with mock containers.
- [x] 4.3 Write unit tests verifying that all five integration relation handlers parse databag variables correctly.
- [x] 4.4 Run `ruff` code format and lint checks to ensure high quality and standard compliance.
