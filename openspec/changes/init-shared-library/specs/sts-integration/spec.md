## ADDED Requirements

### Requirement: Secure Token Service Configuration
The library SHALL provide a class `STSRelationHandler` that wraps the Juju `sts` relation interface, parsing the databag content to return standard environment variables required to authenticate with the Secure Token Service.

#### Scenario: Ready STS relation parsing
- **WHEN** the STS relation is ready and has valid endpoints and credential keys in its Juju databag
- **THEN** the handler's `get_env_vars()` method SHALL return a dictionary with `STS_ENDPOINT_URI`, `STS_CLIENT_ID`, and `STS_CLIENT_SECRET` correctly populated
