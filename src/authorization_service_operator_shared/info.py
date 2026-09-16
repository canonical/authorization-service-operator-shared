# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Interface module for sharing Authorization Service info across components.

Provides provider and requirer components for sharing deployment info such as workload version,
database migration state, and database credentials via the authorization-service-info relation.
"""

import logging

from ops import ModelError, SecretNotFoundError
from ops.charm import (
    CharmBase,
    HookEvent,
    RelationBrokenEvent,
    RelationChangedEvent,
    RelationCreatedEvent,
)
from ops.framework import EventBase, EventSource, Object, ObjectEvents
from pydantic import BaseModel, Field, ValidationError

DEFAULT_RELATION_NAME = "authorization-service-info"

logger = logging.getLogger(__name__)


class AuthorizationServiceInfo(BaseModel):
    """Data model representing Authorization Service deployment information."""

    workload_version: str = ""
    migration_version: str = ""
    openfga_store_id: str = ""
    openfga_model_id: str = ""
    db_host: str = ""
    db_port: str = ""
    db_name: str = ""
    db_user: str = ""
    db_secret_id: str = ""

    db_password: str | None = Field(default=None, exclude=True)

    @property
    def is_migration_ready(self) -> bool:
        """True when workload version and migration version are present."""
        return bool(self.workload_version and self.migration_version)

    @property
    def is_openfga_ready(self) -> bool:
        """True when OpenFGA store ID and model ID are present."""
        return bool(self.openfga_store_id and self.openfga_model_id)

    @property
    def is_db_ready(self) -> bool:
        """True when database connection details are present."""
        return bool(self.db_host and self.db_port and self.db_name and self.db_user and self.db_password)

    @property
    def is_ready(self) -> bool:
        """True when workload version, migration version, store ID, model ID, and DB details are present."""
        return self.is_migration_ready and self.is_openfga_ready and self.is_db_ready


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
        self.framework.observe(
            self._charm.on[self._relation_name].relation_broken,
            self._on_relation_broken,
        )

    def _on_relation_joined(self, event: HookEvent) -> None:
        self.on.authorization_service_info_relation_ready.emit()

    def _on_relation_broken(self, event: RelationBrokenEvent) -> None:
        """Revoke secret access on relation broken and remove secret if no relations remain."""
        if not self._charm.unit.is_leader():
            return

        label = f"{self._charm.app.name}-db-credentials"
        try:
            secret = self._charm.model.get_secret(label=label)
        except SecretNotFoundError:
            return

        try:
            secret.revoke(event.relation)
        except ModelError as exc:
            logger.warning(
                "Failed to revoke secret %s for relation %s: %s",
                secret.id,
                event.relation.id,
                exc,
            )

        remaining = [r for r in self._charm.model.relations.get(self._relation_name, []) if r.id != event.relation.id]
        if not remaining:
            try:
                secret.remove_all_revisions()
                logger.debug("Removed secret %s as no active relations remain", secret.id)
            except ModelError as exc:
                logger.warning("Failed to remove secret %s: %s", secret.id, exc)

    def publish_info(
        self,
        workload_version: str,
        migration_version: str = "",
        openfga_store_id: str = "",
        openfga_model_id: str = "",
        db_host: str = "",
        db_port: str = "",
        db_name: str = "",
        db_user: str = "",
        db_password: str = "",
    ) -> None:
        """Publish workload version, migration version, OpenFGA parameters, and DB credentials into application relation data.

        Args:
            workload_version: The workload version string.
            migration_version: The database migration version string.
            openfga_store_id: The OpenFGA store ID created by server.
            openfga_model_id: The OpenFGA authorization model ID created by server.
            db_host: The PostgreSQL database host.
            db_port: The PostgreSQL database port.
            db_name: The PostgreSQL database name.
            db_user: The PostgreSQL database username.
            db_password: The PostgreSQL database password (will be granted via Juju secret).
        """
        if not self._charm.unit.is_leader():
            return

        relations = self._charm.model.relations.get(self._relation_name, [])
        if not relations:
            return

        db_secret_id = ""
        if db_password:
            label = f"{self._charm.app.name}-db-credentials"
            secret_content = {"db-password": db_password}
            try:
                secret = self._charm.model.get_secret(label=label)
                secret.set_content(secret_content)
            except SecretNotFoundError:
                secret = self._charm.app.add_secret(
                    secret_content,
                    label=label,
                )
            db_secret_id = secret.id
            for relation in relations:
                try:
                    secret.grant(relation)
                except ModelError as exc:
                    logger.debug(
                        "Failed to grant secret %s to relation %s: %s",
                        secret.id,
                        relation.id,
                        exc,
                    )

        mig_version = migration_version or ""
        for relation in relations:
            databag = relation.data[self._charm.app]
            databag["workload_version"] = workload_version
            databag["migration_version"] = mig_version
            databag["openfga_store_id"] = openfga_store_id
            databag["openfga_model_id"] = openfga_model_id
            databag["db_host"] = db_host
            databag["db_port"] = db_port
            databag["db_name"] = db_name
            databag["db_user"] = db_user
            databag["db_secret_id"] = db_secret_id
            logger.debug(
                "Updated relation %s data with workload_version=%s, migration_version=%s, openfga_store_id=%s, openfga_model_id=%s, db_host=%s, db_user=%s",
                relation.id,
                workload_version,
                mig_version,
                openfga_store_id,
                openfga_model_id,
                db_host,
                db_user,
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
        self.framework.observe(
            self._charm.on.secret_changed,
            self._on_relation_changed,
        )

    def _on_relation_changed(self, event: RelationCreatedEvent | RelationChangedEvent | HookEvent) -> None:
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
            db_secret_id = databag.get("db_secret_id", "")
            db_password = None
            if db_secret_id:
                try:
                    secret = self._charm.model.get_secret(id=db_secret_id)
                    secret_content = secret.get_content(refresh=True)
                    db_password = secret_content.get("db-password", "")
                except (SecretNotFoundError, ModelError) as exc:
                    logger.warning("Failed to retrieve database secret %s: %s", db_secret_id, exc)

            return AuthorizationServiceInfo(
                workload_version=databag.get("workload_version", ""),
                migration_version=databag.get("migration_version", ""),
                openfga_store_id=databag.get("openfga_store_id", ""),
                openfga_model_id=databag.get("openfga_model_id", ""),
                db_host=databag.get("db_host", ""),
                db_port=databag.get("db_port", ""),
                db_name=databag.get("db_name", ""),
                db_user=databag.get("db_user", ""),
                db_secret_id=db_secret_id,
                db_password=db_password,
            )
        except ValidationError as exc:
            logger.warning("Failed to parse authorization service info: %s", exc)
            return None
