# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Setup mocks for Juju charmlibs before running tests."""

import sys
from types import ModuleType
from unittest.mock import MagicMock


class MockDatabaseRequires:
    """Mock for DatabaseRequires charmlib class."""

    def __init__(self, charm, relation_name="database", database_name="authorization_service", extra_user_roles=""):
        self.charm = charm
        self.relation_name = relation_name
        self.database_name = database_name
        self.relations = [MagicMock(id=0)]
        self._is_ready = True
        self._credentials = {
            "endpoints": "postgres-host:5432",
            "username": "user",
            "password": "password",
            "read-only-endpoints": "",
        }

    def is_resource_created(self) -> bool:
        """Mock is_resource_created status."""
        return self._is_ready

    def fetch_relation_data(self) -> dict:
        """Mock fetch_relation_data."""
        return {0: {"endpoints": "postgres-host:5432", "username": "user", "password": "password"}}


class MockStsInfoRequirer:
    """Mock for StsInfoRequirer charmlib class."""

    def __init__(self, charm, relation_name="sts-info"):
        self.charm = charm
        self.relation_name = relation_name
        self._sts_info = MagicMock()
        self._sts_info.jwks_url = "https://sts.example.com/jwks"
        self._sts_info.http_address = "https://sts.example.com"
        self._sts_info.grpc_address = "sts.example.com:443"
        self._sts_info.tls_enabled = True

    def get_sts_info(self):
        """Mock get_sts_info."""
        return self._sts_info


class MockKafkaRequires:
    """Mock for KafkaRequires charmlib class."""

    def __init__(self, charm, relation_name="kafka", topic="authorization-service"):
        self.charm = charm
        self.relation_name = relation_name
        self.topic = topic
        self._is_ready = True

    def fetch_relation_data(self, relation_ids=None, fields=None, relation_name=None):
        return {1: {"endpoints": "kafka-broker:9092"}}


class MockMetricsEndpointProvider:
    """Mock for MetricsEndpointProvider charmlib class."""

    def __init__(self, charm, relation_name="metrics-endpoint", jobs=None):
        self.charm = charm
        self.relation_name = relation_name
        self.jobs = jobs


class MockGrafanaDashboardProvider:
    """Mock for GrafanaDashboardProvider charmlib class."""

    def __init__(self, charm, relation_name="grafana-dashboard"):
        self.charm = charm
        self.relation_name = relation_name


def _mock_module(name: str, **attrs) -> ModuleType:
    """Recursively register a mock charmlib module in sys.modules."""
    parts = name.split(".")
    for i in range(1, len(parts) + 1):
        mod_name = ".".join(parts[:i])
        if mod_name not in sys.modules:
            sys.modules[mod_name] = ModuleType(mod_name)
    mod = sys.modules[name]
    for key, value in attrs.items():
        setattr(mod, key, value)
    return mod


# Register charmlib mock modules
_mock_module("charms.data_platform_libs.v0.data_interfaces", DatabaseRequires=MockDatabaseRequires, KafkaRequires=MockKafkaRequires)
_mock_module("charms.postgresql_k8s.v0.postgresql", PostgreSQLRequires=MockDatabaseRequires)
_mock_module("charms.secure_token_service.v0.sts_info", StsInfoRequirer=MockStsInfoRequirer)
_mock_module("charms.kafka_k8s.v0.kafka", KafkaRequires=MockKafkaRequires)
_mock_module("charms.prometheus_k8s.v0.prometheus_scrape", MetricsEndpointProvider=MockMetricsEndpointProvider)
_mock_module("charms.grafana_k8s.v0.grafana_dashboard", GrafanaDashboardProvider=MockGrafanaDashboardProvider)
