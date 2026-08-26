## ADDED Requirements

### Requirement: OpenFGA Connection Configuration
The library SHALL provide a class `OpenFGARelationHandler` that wraps the Juju `openfga` relation and parses its databag contents to generate standard environment variables required by the Go binaries.

#### Scenario: Ready relation parsing
- **WHEN** the OpenFGA relation is ready and contains `address`, `store_id`, and `token` keys in the relation databag
- **THEN** the handler's `get_env_vars()` method SHALL return a dictionary with `OPENFGA_ADDRESS`, `OPENFGA_STORE_ID`, `OPENFGA_API_KEY`, and `OPENFGA_AUTHZ_MODEL_ID` populated with the corresponding values from the relation databag
