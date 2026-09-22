# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests for authorization_service_operator_shared.info module."""

from unittest.mock import MagicMock

from ops import ModelError, SecretNotFoundError
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
    charm.app.name = "authz-app"
    return charm


def test_info_model_is_ready() -> None:
    """Test AuthorizationServiceInfo model readiness."""
    info = AuthorizationServiceInfo(
        workload_version="1.0.0",
        migration_version="1.0.0",
        openfga_store_id="store123",
        openfga_model_id="model123",
        db_host="postgres-host",
        db_port="5432",
        db_name="authorization_service",
        db_user="authz_user",
        db_password="authz_password",
    )
    assert info.is_migration_ready is True
    assert info.is_openfga_ready is True
    assert info.is_db_ready is True
    assert info.is_ready is True

    migration_only = AuthorizationServiceInfo(workload_version="1.0.0", migration_version="1.0.0")
    assert migration_only.is_migration_ready is True
    assert migration_only.is_openfga_ready is False
    assert migration_only.is_db_ready is False
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
    """Test provider publishes workload, migration versions, store ID, model ID, and DB info when leader."""
    charm = _make_mock_charm()
    charm.unit.is_leader.return_value = True

    relation = MagicMock()
    databag = {}
    relation.data = {charm.app: databag}
    charm.model.relations.get.return_value = [relation]

    mock_secret = MagicMock()
    mock_secret.id = "secret:123"
    charm.model.get_secret.side_effect = SecretNotFoundError("Not found")
    charm.app.add_secret.return_value = mock_secret

    provider = AuthorizationServiceInfoProvider(charm, relation_name="authorization-service-info")
    provider.publish_info(
        workload_version="1.2.3",
        migration_version="1.2.3",
        openfga_store_id="store456",
        openfga_model_id="model789",
        db_host="postgres-host",
        db_port="5432",
        db_name="authorization_service",
        db_user="authz_user",
        db_password="secret_password",
    )

    assert databag.get("workload_version") == "1.2.3"
    assert databag.get("migration_version") == "1.2.3"
    assert databag.get("openfga_store_id") == "store456"
    assert databag.get("openfga_model_id") == "model789"
    assert databag.get("db_host") == "postgres-host"
    assert databag.get("db_port") == "5432"
    assert databag.get("db_name") == "authorization_service"
    assert databag.get("db_user") == "authz_user"
    assert databag.get("db_secret_id") == "secret:123"


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
            "db_host": "postgres-host",
            "db_port": "5432",
            "db_name": "authorization_service",
            "db_user": "authz_user",
            "db_secret_id": "secret:123",
        }
    }
    charm.model.relations.get.return_value = [relation]

    mock_secret = MagicMock()
    mock_secret.get_content.return_value = {"db-password": "secret_password"}
    charm.model.get_secret.return_value = mock_secret

    requirer = AuthorizationServiceInfoRequirer(charm, relation_name="authorization-service-info")
    info = requirer.get_info()

    assert info is not None
    assert info.workload_version == "2.0.0"
    assert info.migration_version == "2.0.0"
    assert info.openfga_store_id == "store1"
    assert info.openfga_model_id == "model1"
    assert info.db_host == "postgres-host"
    assert info.db_port == "5432"
    assert info.db_name == "authorization_service"
    assert info.db_user == "authz_user"
    assert info.db_password == "secret_password"
    assert info.is_ready is True


def test_provider_relation_broken_cleans_up_secret() -> None:
    """Test provider revokes secret and removes all revisions when no relations remain."""
    charm = _make_mock_charm()
    charm.unit.is_leader.return_value = True

    mock_secret = MagicMock()
    charm.model.get_secret.return_value = mock_secret

    relation = MagicMock()
    relation.id = 1
    charm.model.relations.get.return_value = [relation]

    provider = AuthorizationServiceInfoProvider(charm, relation_name="authorization-service-info")

    event = MagicMock()
    event.relation = relation
    provider._on_relation_broken(event)

    mock_secret.revoke.assert_called_once_with(relation)
    mock_secret.remove_all_revisions.assert_called_once()


def test_provider_relation_broken_non_leader() -> None:
    """Test provider relation broken does nothing when unit is not leader."""
    charm = _make_mock_charm()
    charm.unit.is_leader.return_value = False

    provider = AuthorizationServiceInfoProvider(charm, relation_name="authorization-service-info")

    event = MagicMock()
    provider._on_relation_broken(event)

    charm.model.get_secret.assert_not_called()


def test_provider_relation_broken_secret_not_found() -> None:
    """Test provider relation broken handles SecretNotFoundError gracefully."""
    charm = _make_mock_charm()
    charm.unit.is_leader.return_value = True
    charm.model.get_secret.side_effect = SecretNotFoundError("Not found")

    provider = AuthorizationServiceInfoProvider(charm, relation_name="authorization-service-info")

    event = MagicMock()
    provider._on_relation_broken(event)

    charm.model.get_secret.assert_called_once()


def test_provider_relation_broken_multiple_relations_remains() -> None:
    """Test provider revokes secret for departing relation but does not delete secret if active relations remain."""
    charm = _make_mock_charm()
    charm.unit.is_leader.return_value = True

    mock_secret = MagicMock()
    charm.model.get_secret.return_value = mock_secret

    relation1 = MagicMock()
    relation1.id = 1
    relation2 = MagicMock()
    relation2.id = 2
    charm.model.relations.get.return_value = [relation1, relation2]

    provider = AuthorizationServiceInfoProvider(charm, relation_name="authorization-service-info")

    event = MagicMock()
    event.relation = relation1
    provider._on_relation_broken(event)

    mock_secret.revoke.assert_called_once_with(relation1)
    mock_secret.remove_all_revisions.assert_not_called()


def test_provider_relation_broken_model_error_handling() -> None:
    """Test provider relation broken handles ModelError on revoke and remove_all_revisions gracefully."""
    charm = _make_mock_charm()
    charm.unit.is_leader.return_value = True

    mock_secret = MagicMock()
    mock_secret.revoke.side_effect = ModelError("Revoke failed")
    mock_secret.remove_all_revisions.side_effect = ModelError("Remove failed")
    charm.model.get_secret.return_value = mock_secret

    relation = MagicMock()
    relation.id = 1
    charm.model.relations.get.return_value = [relation]

    provider = AuthorizationServiceInfoProvider(charm, relation_name="authorization-service-info")

    event = MagicMock()
    event.relation = relation
    # Should not raise exception
    provider._on_relation_broken(event)

    mock_secret.revoke.assert_called_once_with(relation)
    mock_secret.remove_all_revisions.assert_called_once()
