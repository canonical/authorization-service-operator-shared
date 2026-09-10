## ADDED Requirements

### Requirement: OpenFGA Client & Model Configuration Objects
The library SHALL provide an `OpenFGAConfig` frozen dataclass for client settings and an `OpenFGAModelData` frozen dataclass for authorization model settings.

#### Scenario: OpenFGA address URL parsing
- **WHEN** `OpenFGAConfig` is initialized with an HTTP/HTTPS address
- **THEN** `api_scheme` SHALL return the scheme (e.g., `http` or `https`) and `api_host` SHALL return the host and port portion

#### Scenario: OpenFGA model loading from peer databag
- **WHEN** `OpenFGAModelData.load(source)` is invoked with a dict or string
- **THEN** it SHALL return an `OpenFGAModelData` instance with `model_id` populated
