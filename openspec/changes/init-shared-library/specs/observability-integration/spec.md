## ADDED Requirements

### Requirement: Prometheus Scraping Setup
The library SHALL provide a class `MetricsRelationHandler` that wraps the Juju `prometheus_scrape` interface and registers the charm's workload metrics endpoint.

#### Scenario: Metrics endpoint environment generation
- **WHEN** the Prometheus scraper is initialized on a charm with a target scrape port and metrics path
- **THEN** the handler's `get_env_vars()` method SHALL return a dictionary with `METRICS_ENABLED`, `METRICS_PORT`, and `METRICS_PATH` populated appropriately

### Requirement: Grafana Dashboard Setup
The library SHALL provide a class `GrafanaDashboardHandler` that wraps the Juju `grafana_dashboard` interface to automatically register packaged dashboard specifications with the COS Grafana deployment.

#### Scenario: Grafana dashboard provider initialization
- **WHEN** the Grafana handler is instantiated on a charm instance
- **THEN** it SHALL register a `GrafanaDashboardProvider` instance binding the charm's default local `/src/grafana_dashboards` specifications to the specified relation name
