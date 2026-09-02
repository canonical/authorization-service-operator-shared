# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Coordinates Prometheus metrics scraping, Grafana dashboards, and OpenTelemetry tracing."""

import logging
from dataclasses import dataclass

try:
    from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
except ImportError:

    class GrafanaDashboardProvider:  # type: ignore[no-redef]
        """Fallback provider when charms.grafana_k8s is not available."""

        def __init__(self, *args, **kwargs) -> None:
            pass


try:
    from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
except ImportError:

    class MetricsEndpointProvider:  # type: ignore[no-redef]
        """Fallback provider when charms.prometheus_k8s is not available."""

        def __init__(self, *args, **kwargs) -> None:
            pass


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class TracingConfig:
    """Tracing exporter settings for the workload."""

    otlp_endpoint: str = ""
    service_name: str = "authorization-service"

    @property
    def is_ready(self) -> bool:
        """True when OTLP endpoint is configured."""
        return bool(self.otlp_endpoint)

    def to_env_vars(self) -> dict[str, str | bool]:
        """Convert tracing settings to workload environment variables."""
        if not self.is_ready:
            return {}
        return {
            "TELEMETRY_ENABLED": True,
            "OTEL_EXPORTER_OTLP_ENDPOINT": self.otlp_endpoint,
            "OTEL_SERVICE_NAME": self.service_name,
        }

    @classmethod
    def load(cls, requirer, service_name: str = "authorization-service") -> "TracingConfig":
        """Load tracing settings from the tracing relation requirer helper."""
        if not hasattr(requirer, "is_ready") or not requirer.is_ready():
            return cls(service_name=service_name)

        endpoint = requirer.get_endpoint("otlp_http")
        if not endpoint:
            return cls(service_name=service_name)

        return cls(otlp_endpoint=endpoint, service_name=service_name)


class MetricsRelationHandler:
    """Configures Prometheus metrics scraping endpoint for the service components."""

    def __init__(
        self,
        charm,
        relation_name: str = "metrics-endpoint",
        port: int = 9100,
        path: str = "/metrics",
    ) -> None:
        self.charm = charm
        self.relation_name = relation_name
        self.port = port
        self.path = path
        try:
            self.provider = MetricsEndpointProvider(
                charm,
                relation_name=relation_name,
                jobs=[{"static_configs": [{"targets": [f"*:{port}"]}], "metrics_path": path}],
            )
        except Exception as exc:
            logger.debug("Failed to initialize MetricsEndpointProvider: %s", exc)
            self.provider = None

    def get_env_vars(self) -> dict[str, str]:
        """Returns environment variables to enable metrics exporting in the Go binary."""
        return {
            "METRICS_ENABLED": "true",
            "METRICS_PORT": str(self.port),
            "METRICS_PATH": self.path,
        }


class GrafanaDashboardHandler:
    """Registers pre-configured Grafana JSON dashboards into the COS Stack."""

    def __init__(self, charm, relation_name: str = "grafana-dashboard") -> None:
        self.charm = charm
        self.relation_name = relation_name
        try:
            self.provider = GrafanaDashboardProvider(charm, relation_name=relation_name)
        except Exception as exc:
            logger.debug("Failed to initialize GrafanaDashboardProvider: %s", exc)
            self.provider = None
