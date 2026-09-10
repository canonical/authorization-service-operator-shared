## ADDED Requirements

### Requirement: Charm Configuration Conversion
The library SHALL provide a `CharmConfig` class parsing `ops.ConfigData` parameters into standardized environment mappings for Go workload container consumption.

#### Scenario: Successful configuration formatting
- **WHEN** the `CharmConfig` is instantiated with configurations containing proxies and log settings, and `to_env_vars()` is called
- **THEN** it SHALL return a dictionary containing keys like `LOG_LEVEL` and proxy environment variables mapped correctly as strings
