# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Coordinates Kafka client relations and environment parsing."""

import logging
from typing import Any

try:
    from charms.data_platform_libs.v1.data_interfaces import (
        KafkaRequestModel,
        KafkaResponseModel,
        ResourceRequirerEventHandler,
    )
except ImportError:

    class KafkaRequestModel:  # type: ignore[no-redef]
        """Fallback request model when charms.data_platform_libs is not available."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.topic = kwargs.get("topic", "")
            self.resource = kwargs.get("topic") or kwargs.get("resource", "")
            self.extra_user_roles = kwargs.get("extra_user_roles")
            self.consumer_group_prefix = kwargs.get("consumer_group_prefix")

    class KafkaResponseModel:  # type: ignore[no-redef]
        """Fallback response model when charms.data_platform_libs is not available."""

    class ResourceRequirerEventHandler:  # type: ignore[no-redef]
        """Fallback requirer when charms.data_platform_libs is not available."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            reqs = kwargs.get("requests", [])
            self.extra_user_roles = reqs[0].extra_user_roles if reqs else None
            self.consumer_group_prefix = reqs[0].consumer_group_prefix if reqs else None
            self.topic = getattr(reqs[0], "topic", getattr(reqs[0], "resource", "")) if reqs else ""
            self.on = getattr(args[0], "on", None) if args else None


logger = logging.getLogger(__name__)


class KafkaRelationHandler:
    """Coordinates Kafka client relations and environment parsing."""

    def __init__(
        self,
        charm,
        relation_name: str = "kafka",
        consumer_group: str = "authorization-service",
        extra_user_roles: str = "producer,consumer",
        topic: str = "permissions.authorization_service",
    ):
        self.charm = charm
        self.relation_name = relation_name
        self.consumer_group = consumer_group
        self.topic = topic
        self.extra_user_roles = extra_user_roles
        self.kafka = ResourceRequirerEventHandler(
            charm,
            relation_name=relation_name,
            requests=[
                KafkaRequestModel(
                    topic=topic,
                    extra_user_roles=extra_user_roles,
                    consumer_group_prefix=consumer_group,
                )
            ],
            response_model=KafkaResponseModel,
        )

    def _get_relation_data(self) -> dict[str, str]:
        """Fetch Kafka relation data using V1 model."""
        relation = self.charm.model.get_relation(self.relation_name)
        if not relation or not relation.app:
            return {}

        try:
            model = self.kafka.interface.build_model(relation.id, component=relation.app)
            for req in getattr(model, "requests", []):
                if req.endpoints:
                    data = {"endpoints": req.endpoints}
                    if req.username:
                        data["username"] = str(req.username)
                    if req.password:
                        data["password"] = str(req.password)
                    if req.tls is not None:
                        data["tls"] = str(req.tls).lower()
                    if req.tls_ca:
                        data["tls-ca"] = str(req.tls_ca)
                    return data
        except Exception:
            logger.debug("Failed to build V1 model from relation data", exc_info=True)

        return {}

    @property
    def bootstrap_server(self) -> str:
        """Extract Kafka bootstrap server endpoints."""
        return self._get_relation_data().get("endpoints", "")

    @property
    def username(self) -> str:
        """Extract Kafka username from relation data."""
        return self._get_relation_data().get("username", "")

    @property
    def password(self) -> str:
        """Extract Kafka password from relation data."""
        return self._get_relation_data().get("password", "")

    @property
    def tls(self) -> str:
        """Extract Kafka TLS setting from relation data."""
        return self._get_relation_data().get("tls", "")

    @property
    def tls_ca(self) -> str:
        """Extract Kafka TLS CA certificate from relation data."""
        return self._get_relation_data().get("tls-ca", "")

    def is_ready(self) -> bool:
        """Check if Kafka relation is present and endpoints are provided."""
        relation = self.charm.model.get_relation(self.relation_name)
        if not relation:
            return False
        return bool(self.bootstrap_server)

    def get_env_vars(self) -> dict[str, str]:
        """Parse relation details and return Go-binary Kafka environment variables."""
        if not self.is_ready():
            return {}

        rel_data = self._get_relation_data()
        env = {
            "KAFKA_ENABLED": "true",
            "KAFKA_BROKERS": rel_data.get("endpoints", ""),
            "KAFKA_CONSUMER_GROUP": self.consumer_group,
            "FEDERATED_SERVICES_STRATEGY": "fs",
        }
        if tls := rel_data.get("tls"):
            is_tls = str(tls).lower() in ("enabled", "true")
            env["KAFKA_TLS_ENABLED"] = str(is_tls).lower()
        if (tls_ca := rel_data.get("tls-ca")) and tls_ca != "disabled":
            env["KAFKA_TLS_CA"] = tls_ca
        return env

    def to_env_vars(self) -> dict[str, str]:
        """Produce workload environment variables (EnvVarConvertible protocol)."""
        return self.get_env_vars()
