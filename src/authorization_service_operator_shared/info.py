# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Interface module for sharing Authorization Service info across components.

Provides provider and requirer components for sharing deployment info such as workload version
and database migration state via the authorization-service-info relation.
"""

import logging

from ops.charm import (
    CharmBase,
    HookEvent,
    RelationBrokenEvent,
    RelationChangedEvent,
    RelationCreatedEvent,
)
from ops.framework import EventBase, EventSource, Object, ObjectEvents
from pydantic import BaseModel, ValidationError

DEFAULT_RELATION_NAME = "authorization-service-info"

logger = logging.getLogger(__name__)


class AuthorizationServiceInfo(BaseModel):
    """Data model representing Authorization Service deployment information."""

    workload_version: str = ""
    migration_version: str = ""
    openfga_store_id: str = ""
    openfga_model_id: str = ""

    @property
    def is_migration_ready(self) -> bool:
        """True when workload version and migration version are present."""
        return bool(self.workload_version and self.migration_version)

    @property
    def is_openfga_ready(self) -> bool:
        """True when OpenFGA store ID and model ID are present."""
        return bool(self.openfga_store_id and self.openfga_model_id)

    @property
    def is_ready(self) -> bool:
        """True when workload version, migration version, store ID, and model ID are present."""
        return self.is_migration_ready and self.is_openfga_ready


class AuthorizationServiceInfoRelationError(Exception):
    """Base exception for authorization_service_info relation errors."""


class AuthorizationServiceInfoDataMissingError(AuthorizationServiceInfoRelationError):
    """Raised when expected relation data is missing or incomplete."""


class AuthorizationServiceInfoRelationMissingError(AuthorizationServiceInfoRelationError):
    """Raised when relation is missing."""


class AuthorizationServiceInfoUpdatedEvent(EventBase):
    """Event emitted when authorization service info relation data is updated."""


class AuthorizationServiceInfoBrokenEvent(EventBase):
    """Event emitted when authorization service info relation is broken."""


class AuthorizationServiceInfoRelationReadyEvent(EventBase):
    """Event emitted when an authorization service info relation is joined/ready on provider side."""


class AuthorizationServiceInfoRequirerEvents(ObjectEvents):
    """Events for the AuthorizationServiceInfoRequirer."""

    authorization_service_info_updated = EventSource(AuthorizationServiceInfoUpdatedEvent)
    authorization_service_info_broken = EventSource(AuthorizationServiceInfoBrokenEvent)


class AuthorizationServiceInfoProviderEvents(ObjectEvents):
    """Events for the AuthorizationServiceInfoProvider."""

    authorization_service_info_relation_ready = EventSource(AuthorizationServiceInfoRelationReadyEvent)


class AuthorizationServiceInfoProvider(Object):
    """Provider component for sharing Authorization Service info."""

    on = AuthorizationServiceInfoProviderEvents()

    def __init__(
        self,
        charm: CharmBase,
        relation_name: str = DEFAULT_RELATION_NAME,
    ) -> None:
        super().__init__(charm, relation_name)
        self._charm = charm
        self._relation_name = relation_name

        self.framework.observe(
            self._charm.on[self._relation_name].relation_joined,
            self._on_relation_joined,
        )

    def _on_relation_joined(self, event: HookEvent) -> None:
        self.on.authorization_service_info_relation_ready.emit()

    def publish_info(
        self,
        workload_version: str,
        migration_version: str | None = None,
        openfga_store_id: str = "",
        openfga_model_id: str = "",
    ) -> None:
        """Publish workload version, migration version, and OpenFGA parameters into application relation data.

        Args:
            workload_version: The workload version string.
            migration_version: The database migration version string (defaults to workload_version).
            openfga_store_id: The OpenFGA store ID created by server.
            openfga_model_id: The OpenFGA authorization model ID created by server.
        """
        if not self._charm.unit.is_leader():
            return

        relations = self._charm.model.relations.get(self._relation_name, [])
        if not relations:
            return

        mig_version = migration_version or workload_version
        for relation in relations:
            databag = relation.data[self._charm.app]
            databag["workload_version"] = workload_version
            databag["migration_version"] = mig_version
            databag["openfga_store_id"] = openfga_store_id
            databag["openfga_model_id"] = openfga_model_id
            logger.debug(
                "Updated relation %s data with workload_version=%s, migration_version=%s, openfga_store_id=%s, openfga_model_id=%s",
                relation.id,
                workload_version,
                mig_version,
                openfga_store_id,
                openfga_model_id,
            )


class AuthorizationServiceInfoRequirer(Object):
    """Requirer component for consuming Authorization Service info."""

    on = AuthorizationServiceInfoRequirerEvents()

    def __init__(
        self,
        charm: CharmBase,
        relation_name: str = DEFAULT_RELATION_NAME,
    ) -> None:
        super().__init__(charm, relation_name)
        self._charm = charm
        self._relation_name = relation_name

        self.framework.observe(
            self._charm.on[self._relation_name].relation_created,
            self._on_relation_changed,
        )
        self.framework.observe(
            self._charm.on[self._relation_name].relation_changed,
            self._on_relation_changed,
        )
        self.framework.observe(
            self._charm.on[self._relation_name].relation_broken,
            self._on_relation_broken,
        )

    def _on_relation_changed(self, event: RelationCreatedEvent | RelationChangedEvent) -> None:
        self.on.authorization_service_info_updated.emit()

    def _on_relation_broken(self, event: RelationBrokenEvent) -> None:
        self.on.authorization_service_info_broken.emit()

    def get_info(self) -> AuthorizationServiceInfo | None:
        """Fetch Authorization Service info from the relation databag.

        Returns:
            AuthorizationServiceInfo if present and valid, None otherwise.
        """
        relations = self._charm.model.relations.get(self._relation_name)
        if not relations:
            return None

        relation = relations[0]
        if not relation or not relation.app or relation.app not in relation.data:
            return None

        databag = relation.data[relation.app]
        try:
            return AuthorizationServiceInfo(
                workload_version=databag.get("workload_version", ""),
                migration_version=databag.get("migration_version", ""),
                openfga_store_id=databag.get("openfga_store_id", ""),
                openfga_model_id=databag.get("openfga_model_id", ""),
            )
        except ValidationError as exc:
            logger.warning("Failed to parse authorization service info: %s", exc)
            return None
