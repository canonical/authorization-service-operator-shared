## ADDED Requirements

### Requirement: OpenTelemetry Tracing Configuration Object
The library SHALL provide a `TracingConfig` frozen dataclass holding `otlp_endpoint` and `service_name`.

#### Scenario: Tracing environment variable conversion
- **WHEN** `TracingConfig` contains a non-empty `otlp_endpoint`
- **THEN** `to_env_vars()` SHALL return a dictionary containing `TELEMETRY_ENABLED: True`, `OTEL_EXPORTER_OTLP_ENDPOINT`, and `OTEL_SERVICE_NAME`
