## ADDED Requirements

### Requirement: Custom Exceptions Hierarchy
The library SHALL provide a base exception class `AuthorizationServiceCharmError` and sub-exceptions representing config, databag, and workload issues.

#### Scenario: Custom exception raising
- **WHEN** an operational command fails or configuration parameters are invalid
- **THEN** the charm SHALL raise a custom subclass of `AuthorizationServiceCharmError` with clear error details
