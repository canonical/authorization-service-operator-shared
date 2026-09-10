## Context

The Charmed Authorization Service operator family (Server, Worker, and Listener) must be able to communicate with common external services (PostgreSQL, OpenFGA, secure token service, and Kafka) and export standard telemetry endpoints to Juju's Observability Stack (COS LMA). In addition to relations mapping, they share baseline operator concerns such as CLI wrap interactions (running migrations, migrations status checks, writing OpenFGA models), parsed configurations (log level, HTTP/HTTPS proxies), custom exceptions, Pebble planning layers orchestration, and connection wrappers. Rather than duplicating these components inside each individual operator charm, we consolidate them inside a shared, reusable Python package `authorization-service-operator-shared` to maintain strict behavioral parity.

## Goals / Non-Goals

**Goals:**
- **Standardized Multi-File Packaging**: Establish a modern, clean, PEP 621-compliant project layout supporting structured submodules (`database`, `openfga`, `sts`, `kafka`, `observability`, `cli`, `configs`, `exceptions`, `services`, `utils`) rather than a restricted single-file charm library.
- **Charmcraft UV Compatibility**: Provide standard package configurations in `pyproject.toml` so that consumer charms can declare the shared library directly in their dependencies under modern Charmcraft compile-time `uv` layers.
- **Expose Reusable Relation Wrappers and Services**: Provide robust connection handlers and Pebble orchestration managers that return simple, consistent parameters and handle planning loops uniformly.

**Non-Goals:**
- **Charmed Operator Implementation**: This repository does not implement Juju Charmed Operator classes themselves. It only hosts the common libraries that the charms import.
- **Production PyPI Release Automation**: Setting up final CD deployment pipelines to public/private indices is out of scope for this initial bootstrap step. We will utilize UV's Git-source mechanism (`[tool.uv.sources]`) to link charms to the library during the development/prototyping phase.

## Package Structure

The shared library contains both Juju relation mapping wrappers and foundational operator components:

```text
authorization-service-operator-shared/
├── pyproject.toml              # Build & dependency configurations (PEP 621 metadata)
├── README.md                   # Shared developer documentation
├── LICENSE                     # License file
├── tests/                      # Automated unit/integration tests
│   ├── unit/
│   └── integration/
└── src/
    └── authorization_service_operator_shared/
        ├── __init__.py         # Exposes public interface classes
        ├── database.py         # DatabaseRelationHandler (wraps postgresql_client)
        ├── openfga.py          # OpenFGARelationHandler (wraps openfga relation)
        ├── sts.py              # STSRelationHandler (wraps STS relation)
        ├── kafka.py            # KafkaRelationHandler (wraps kafka relation)
        ├── observability.py    # MetricsRelationHandler (scrape endpoint) & GrafanaDashboardHandler
        ├── cli.py              # CommandLine wrapper for the binary via Pebble exec
        ├── configs.py          # Shared CharmConfig helper parsing proxies, log levels
        ├── exceptions.py       # Custom exception hierarchy
        ├── services.py         # Shared PebbleService and WorkloadService managers
        ├── utils.py            # Shared wrapper decorators (such as @leader_unit)
        └── constants.py        # Shared constant definitions (e.g. app commands, filenames)
```

## Decisions

### Decision 1: Standard Python Package vs. Legacy Charmhub Library
- **Choice**: Standard Python package published/accessed via Git/PyPI.
- **Rationale**: Standard Juju charm libraries (`charmcraft publish-lib`) are restricted to a single `.py` file containing all code. To avoid a monolithic, hard-to-maintain single file, a standard Python package structure allows split files for clean segregation. Under the modern Charmcraft `uv` build backend, standard package importing works out-of-the-box.
- **Alternatives Considered**: Creating multiple single-file libraries on Charmhub. This was rejected due to heavy maintenance overhead and poor module structure.

### Decision 2: Build Backend Selection
- **Choice**: Use `setuptools` with PEP 621 metadata.
- **Rationale**: Highly compatible, extremely robust, and easily integrated with all standard linting/formatting toolchains.
- **Alternatives Considered**: `hatchling` or `flit`. While modern and efficient, `setuptools` remains the canonical choice in standard Canonical environments and has the widest compiler compatibility.

### Decision 3: Consumer Dependency Linking in Dev
- **Choice**: Link via Git in the consumer charms' `pyproject.toml` using `[tool.uv.sources]`.
- **Rationale**: Allows rapid development and instant validation of shared library modifications without requiring version bumps, releases, or local wheel building on the developer's host.

### Decision 4: Charmlibs Resolution Strategy
- **Choice**: Option A — Consuming charms fetch required charmlibs locally via `charmcraft fetch-lib`.
- **Rationale**: Keeps the shared library lightweight, avoids packaging brittle or specific Juju relation libraries inside our shared python module, and guarantees that each individual operator charm maintains local ownership over its required charmlib versions. At runtime on Juju, the host runner puts the charm's local `lib/` directory on `sys.path`, resolving the shared library's `from charms.xxx` imports perfectly and seamlessly.
- **Alternatives Considered**: Option B — Packing charmlibs transitively or declaring them as PyPI dependencies in the shared library's configuration. This was rejected because many Juju relation libraries are not published on PyPI or are pinned to highly specific charm revisions that are safer managed locally by the operator itself.

## Risks / Trade-offs

- **[Risk] Upstream Relation Interface Drift** → **[Mitigation]**: Incorporate the standard `pytest-interface-tester` package inside unit/integration testing suites to guarantee that our relational parsing code complies exactly with the canonical schemas specified in `charm-relation-interfaces`.
- **[Risk] Library Coupling causing deployment delays** → **[Mitigation]**: Keep the classes strictly separated by concern (database, openfga, etc.) and restrict shared wrappers to minimal databag extraction, avoiding business logic.
