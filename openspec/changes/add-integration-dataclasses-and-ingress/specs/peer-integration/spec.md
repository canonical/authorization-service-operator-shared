## ADDED Requirements

### Requirement: JSON Peer Relation Accessor
The library SHALL provide a `PeerData` class providing typed JSON serialization over app-level peer databags.

#### Scenario: Reading and writing peer databag keys
- **WHEN** a value is set via `peer_data[key] = value` on the leader unit
- **THEN** it SHALL be JSON-encoded in the peer relation app databag and decoded when accessed via `peer_data[key]`
