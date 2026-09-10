## ADDED Requirements

### Requirement: Kafka Broker Configuration Mapping
The library SHALL provide a class `KafkaRelationHandler` that wraps the Juju `kafka` relation interface, parsing bootstrap broker host/port elements and consumer parameters.

#### Scenario: Successful Kafka broker extraction
- **WHEN** the Kafka relation is active and contains bootstrap broker URLs in its Juju databag
- **THEN** the handler's `get_env_vars()` method SHALL return a dictionary with `KAFKA_BROKERS` and `KAFKA_CONSUMER_GROUP` correctly populated
