## ADDED Requirements

### Requirement: Service Management Layers
The library SHALL provide `PebbleService` and `WorkloadService` classes to manage service layer definitions, reload checks, status queries, and version strings.

#### Scenario: Pebble layer planning
- **WHEN** environment inputs change and a service layer plan is triggered
- **THEN** the handler SHALL update the Pebble layer definitions and run `container.replan()` to apply variables seamlessly
