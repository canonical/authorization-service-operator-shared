## ADDED Requirements

### Requirement: CommandLine Wrapper execution
The library SHALL provide a `CommandLine` class that executes commands against the underlying Go workload binary inside a specified Pebble container.

#### Scenario: Successful version lookup
- **WHEN** the `CommandLine` wrapper's `get_service_version()` method is executed on a connected container
- **THEN** it SHALL return the stripped stdout string representing the workload's version
