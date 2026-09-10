## ADDED Requirements

### Requirement: Leader Unit Decorator
The library SHALL provide a `@leader_unit` decorator ensuring that certain event handlers only execute on Juju's active leader unit.

#### Scenario: Running decorated handler on non-leader
- **WHEN** a decorated method is called on a unit where `unit.is_leader()` is false
- **THEN** the handler SHALL return immediately with `None` without executing the inner logic

### Requirement: Container Connectivity Check
The library SHALL provide a `container_connectivity(charm, container_name)` function checking if a workload container is reachable via Pebble.

#### Scenario: Checking container reachability
- **WHEN** `container_connectivity(charm, "container")` is called
- **THEN** it SHALL return the result of `container.can_connect()`

### Requirement: Integration Existence Factory
The library SHALL provide an `integration_existence(relation_name)` factory function returning a callable that checks if a relation exists on the charm model.

#### Scenario: Checking relation existence
- **WHEN** the returned condition function is called with a charm instance
- **THEN** it SHALL return `True` if `charm.model.relations.get(relation_name)` is present and non-empty
