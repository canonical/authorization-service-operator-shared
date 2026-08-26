# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests for the five relation integration handlers."""

from unittest.mock import MagicMock

from authorization_service_operator_shared.database import DatabaseRelationHandler
from authorization_service_operator_shared.kafka import KafkaRelationHandler
from authorization_service_operator_shared.observability import (
    GrafanaDashboardHandler,
    MetricsRelationHandler,
)
from authorization_service_operator_shared.openfga import OpenFGARelationHandler
from authorization_service_operator_shared.sts import STSRelationHandler


def _make_mock_charm(relation_name=None, app_data=None, has_units=True):
    charm = MagicMock()
    if relation_name:
        relation = MagicMock()
        relation.units = [MagicMock()] if has_units else []
        relation.app = MagicMock()

        # Databag mapping
        relation.data = {relation.app: app_data or {}}
        charm.model.get_relation.return_value = relation
    else:
        charm.model.get_relation.return_value = None
    return charm


# ── DatabaseRelationHandler Tests ─────────────────────────────────────────────


def test_database_relation_handler_is_ready_true():
    charm = _make_mock_charm("database")
    handler = DatabaseRelationHandler(charm)
    assert handler.is_ready() is True


def test_database_relation_handler_is_ready_false_when_no_relation():
    charm = _make_mock_charm()
    handler = DatabaseRelationHandler(charm)
    assert handler.is_ready() is False


def test_database_relation_handler_is_ready_false_when_no_units():
    charm = _make_mock_charm("database", has_units=False)
    handler = DatabaseRelationHandler(charm)
    assert handler.is_ready() is False


def test_database_relation_handler_get_env_vars():
    charm = _make_mock_charm("database")
    handler = DatabaseRelationHandler(charm, database_name="test_db")
    env = handler.get_env_vars()
    assert env["POSTGRES_HOST"] == "postgres-host"
    assert env["POSTGRES_PORT"] == "5432"
    assert env["POSTGRES_USER"] == "user"
    assert env["POSTGRES_PASSWORD"] == "password"
    assert env["POSTGRES_DB"] == "test_db"


# ── OpenFGARelationHandler Tests ──────────────────────────────────────────────


def test_openfga_relation_handler_is_ready_true():
    mock_requirer = MagicMock()
    mock_requirer.get_store_info.return_value = MagicMock(
        http_api_url="127.0.0.1:8080", store_id="store-1", token="tok", authorization_model_id=""
    )
    handler = OpenFGARelationHandler(mock_requirer)
    assert handler.is_ready() is True


def test_openfga_relation_handler_is_ready_false_missing_keys():
    mock_requirer = MagicMock()
    mock_requirer.get_store_info.return_value = None
    handler = OpenFGARelationHandler(mock_requirer)
    assert handler.is_ready() is False


def test_openfga_relation_handler_get_env_vars():
    mock_requirer = MagicMock()
    mock_requirer.get_store_info.return_value = MagicMock(
        http_api_url="127.0.0.1:8080",
        store_id="store-1",
        token="tok",
        authorization_model_id="model-1",
    )
    handler = OpenFGARelationHandler(mock_requirer)
    env = handler.get_env_vars()
    assert env["OPENFGA_ADDRESS"] == "127.0.0.1:8080"
    assert env["OPENFGA_STORE_ID"] == "store-1"
    assert env["OPENFGA_API_KEY"] == "tok"
    assert env["OPENFGA_AUTHORIZATION_MODEL_ID"] == "model-1"


# ── STSRelationHandler Tests ──────────────────────────────────────────────────


def test_sts_relation_handler_is_ready_true():
    charm = _make_mock_charm("sts-info")
    handler = STSRelationHandler(charm)
    assert handler.is_ready() is True


def test_sts_relation_handler_is_ready_false_when_no_relation():
    charm = _make_mock_charm()
    handler = STSRelationHandler(charm)
    assert handler.is_ready() is False


def test_sts_relation_handler_get_env_vars():
    charm = _make_mock_charm("sts-info")
    handler = STSRelationHandler(charm)
    env = handler.get_env_vars()
    assert env["STS_ADDRESS"] == "sts.example.com:443"
    assert env["STS_USE_TLS"] == "true"
    assert env["STS_JWKS_URI"] == "https://sts.example.com/jwks"
    assert env["EXTAUTHZ_JWK_SET_URL"] == "https://sts.example.com/jwks"


# ── KafkaRelationHandler Tests ────────────────────────────────────────────────


def test_kafka_relation_handler_is_ready_true():
    charm = _make_mock_charm("kafka")
    handler = KafkaRelationHandler(charm)
    assert handler.is_ready() is True


def test_kafka_relation_handler_is_ready_false_when_no_relation():
    charm = _make_mock_charm()
    handler = KafkaRelationHandler(charm)
    assert handler.is_ready() is False


def test_kafka_relation_handler_get_env_vars():
    charm = _make_mock_charm("kafka")
    handler = KafkaRelationHandler(charm, consumer_group="test-group")
    env = handler.get_env_vars()
    assert env["KAFKA_BROKERS"] == "kafka-broker:9092"
    assert env["KAFKA_CONSUMER_GROUP"] == "test-group"


# ── Observability Relation Handlers Tests ─────────────────────────────────────


def test_metrics_relation_handler_get_env_vars():
    charm = MagicMock()
    handler = MetricsRelationHandler(charm, port=9200, path="/my-metrics")
    env = handler.get_env_vars()
    assert env["METRICS_ENABLED"] == "true"
    assert env["METRICS_PORT"] == "9200"
    assert env["METRICS_PATH"] == "/my-metrics"


def test_grafana_dashboard_handler_init():
    charm = MagicMock()
    handler = GrafanaDashboardHandler(charm, relation_name="my-dashboard")
    assert handler.relation_name == "my-dashboard"
