# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests for authorization_service_operator_shared.info module."""

from unittest.mock import MagicMock

from ops.charm import CharmBase

from authorization_service_operator_shared.info import (
    AuthorizationServiceInfo,
    AuthorizationServiceInfoProvider,
    AuthorizationServiceInfoRequirer,
)


def _make_mock_charm() -> MagicMock:
    """Create a mock charm with ops Object attributes configured."""
    charm = MagicMock(spec=CharmBase)
    charm.framework = MagicMock()
    charm.handle = MagicMock()
    charm.on = MagicMock()
    return charm


def test_info_model_is_ready() -> None:
    """Test AuthorizationServiceInfo model readiness."""
    info = AuthorizationServiceInfo(
        workload_version="1.0.0",
        migration_version="1.0.0",
        openfga_store_id="store123",
        openfga_model_id="model123",
    )
    assert info.is_migration_ready is True
    assert info.is_openfga_ready is True
    assert info.is_ready is True

    migration_only = AuthorizationServiceInfo(workload_version="1.0.0", migration_version="1.0.0")
    assert migration_only.is_migration_ready is True
    assert migration_only.is_openfga_ready is False
    assert migration_only.is_ready is False


def test_provider_publish_info_non_leader() -> None:
    """Test provider does not publish info on non-leader units."""
    charm = _make_mock_charm()
    charm.unit.is_leader.return_value = False

    provider = AuthorizationServiceInfoProvider(charm, relation_name="authorization-service-info")
    provider.publish_info(
        workload_version="1.0.0",
        migration_version="1.0.0",
        openfga_store_id="store123",
        openfga_model_id="model123",
    )

    charm.model.relations.get.assert_not_called()


def test_provider_publish_info_leader() -> None:
    """Test provider publishes workload, migration versions, store ID, and model ID when leader."""
    charm = _make_mock_charm()
    charm.unit.is_leader.return_value = True
    charm.app = "authz-app"

    relation = MagicMock()
    databag = {}
    relation.data = {charm.app: databag}
    charm.model.relations.get.return_value = [relation]

    provider = AuthorizationServiceInfoProvider(charm, relation_name="authorization-service-info")
    provider.publish_info(
        workload_version="1.2.3",
        migration_version="1.2.3",
        openfga_store_id="store456",
        openfga_model_id="model789",
    )

    assert databag.get("workload_version") == "1.2.3"
    assert databag.get("migration_version") == "1.2.3"
    assert databag.get("openfga_store_id") == "store456"
    assert databag.get("openfga_model_id") == "model789"


def test_requirer_get_info_none_when_no_relation() -> None:
    """Test requirer returns None when relation is missing."""
    charm = _make_mock_charm()
    charm.model.relations.get.return_value = []

    requirer = AuthorizationServiceInfoRequirer(charm, relation_name="authorization-service-info")
    assert requirer.get_info() is None


def test_requirer_get_info_valid_data() -> None:
    """Test requirer parses valid databag content."""
    charm = _make_mock_charm()
    app = MagicMock()
    relation = MagicMock()
    relation.app = app
    relation.data = {
        app: {
            "workload_version": "2.0.0",
            "migration_version": "2.0.0",
            "openfga_store_id": "store1",
            "openfga_model_id": "model1",
        }
    }
    charm.model.relations.get.return_value = [relation]

    requirer = AuthorizationServiceInfoRequirer(charm, relation_name="authorization-service-info")
    info = requirer.get_info()

    assert info is not None
    assert info.workload_version == "2.0.0"
    assert info.migration_version == "2.0.0"
    assert info.openfga_store_id == "store1"
    assert info.openfga_model_id == "model1"
    assert info.is_ready is True
