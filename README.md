# Charmed Authorization Service Operator Shared Library

This repository contains the shared Python library (`authorization-service-operator-shared`) for the Charmed Authorization Service operator family (Server, Listener, and Worker).

It consolidates common concerns including database integration, OpenFGA relation handling, STS configuration, Kafka bindings, Istio Gateway API ingress, peer databag access, observability scraping, Pebble container management, config mappings, and CLI execution wrappers.

## Package Layout

```text
src/authorization_service_operator_shared/
├── __init__.py         # Public interface imports
├── cli.py              # CommandLine wrapper for Pebble exec command runs
├── configs.py          # CharmConfig mapping proxies & logging levels
├── database.py         # DatabaseConfig & DatabaseRelationHandler (postgresql_client)
├── exceptions.py       # Standard operational exception hierarchy
├── info.py             # AuthorizationServiceInfo, AuthorizationServiceInfoProvider, & AuthorizationServiceInfoRequirer (authorization-service-info relation)
├── ingress.py          # IstioIngressIntegration (Istio Gateway API)
├── kafka.py            # KafkaRelationHandler
├── observability.py    # MetricsRelationHandler, GrafanaDashboardHandler, & TracingConfig
├── openfga.py          # OpenFGAConfig, OpenFGAModelData, & OpenFGARelationHandler
├── peer.py             # PeerData accessor for peer relation app databags
├── services.py         # PebbleService & WorkloadService managers
├── sts.py              # StsConfig & STSRelationHandler
├── utils.py            # Utilities (leader_unit, container_connectivity, integration_existence)
└── constants.py        # Reusable application constants
```

## Importing Patterns

To import common handlers, dataclasses, exceptions, or services from this library in your charms:

```python
from authorization_service_operator_shared import (
    AuthorizationServiceInfo,
    AuthorizationServiceInfoProvider,
    AuthorizationServiceInfoRequirer,
    DatabaseConfig,
    DatabaseRelationHandler,
    KafkaRelationHandler,
    OpenFGAConfig,
    OpenFGAModelData,
    OpenFGARelationHandler,
    StsConfig,
    STSRelationHandler,
    IstioIngressIntegration,
    PeerData,
    TracingConfig,
    MetricsRelationHandler,
    GrafanaDashboardHandler,
    CommandLine,
    CharmConfig,
    PebbleService,
    WorkloadService,
    leader_unit,
    container_connectivity,
    integration_existence,
)
```

## Developer Instructions

### Prerequisites
Ensure you have `uv` installed (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`).

### Installation for Local Development
Install the library in editable mode:

```bash
uv pip install -e .
```

### Running Tests
Run unit tests with:

```bash
uv run pytest
```

### Formatting and Linting
To format and lint the codebase, use `ruff`:

```bash
uv run ruff format .
uv run ruff check . --fix
```
