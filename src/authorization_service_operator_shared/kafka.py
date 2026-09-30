# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Coordinates Kafka client relations and environment parsing."""

import logging
from typing import Any

try:
    from charms.data_platform_libs.v0.data_interfaces import KafkaRequires
except ImportError:

    class KafkaRequires:  # type: ignore[no-redef]
        """Fallback provider when charms.data_platform_libs is not available."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.topic = kwargs.get("topic", "")
            self.extra_user_roles = kwargs.get("extra_user_roles")
            self.consumer_group_prefix = kwargs.get("consumer_group_prefix")


logger = logging.getLogger(__name__)


class KafkaRelationHandler:
    """Coordinates Kafka client relations and environment parsing."""

    def __init__(
        self,
        charm,
        relation_name: str = "kafka",
        consumer_group: str = "authorization-service",
        topic: str = "authorization-service.permissions",
        extra_user_roles: str = "producer,consumer",
        federated_services: str = "",
    ):
        self.charm = charm
        self.relation_name = relation_name
        self.consumer_group = consumer_group
        self.topic = topic
        self.extra_user_roles = extra_user_roles
        self.federated_services = federated_services
        self.kafka = KafkaRequires(
            charm,
            relation_name=relation_name,
            topic=topic,
            extra_user_roles=extra_user_roles,
            consumer_group_prefix=consumer_group,
        )

    def _get_relation_data(self) -> dict[str, str]:
        """Fetch all Kafka relation fields from the relation that has endpoints."""
        fields = ["endpoints", "username", "password", "tls", "tls-ca"]
        if hasattr(self.kafka, "fetch_relation_data"):
            rel_data = self.kafka.fetch_relation_data(fields=fields)
            for data in rel_data.values():
                if data.get("endpoints"):
                    return {k: str(v) for k, v in data.items() if v is not None}
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
        """Checks if Kafka details are ready in the relation databag."""
        relation = self.charm.model.get_relation(self.relation_name)
        if not relation or not relation.units:
            return False
        return bool(self.bootstrap_server)

    def get_env_vars(self) -> dict[str, str]:
        """Parses relation details and returns standard Go-binary Kafka environment variables."""
        if not self.is_ready():
            return {}

        rel_data = self._get_relation_data()
        env = {
            "KAFKA_ENABLED": "true",
            "KAFKA_BROKERS": rel_data.get("endpoints", ""),
            "KAFKA_CONSUMER_GROUP": self.consumer_group,
        }
        if self.federated_services:
            env["FEDERATED_SERVICES"] = self.federated_services
        if username := rel_data.get("username"):
            env["KAFKA_SASL_USERNAME"] = username
        if password := rel_data.get("password"):
            env["KAFKA_SASL_PASSWORD"] = password
        if tls := rel_data.get("tls"):
            is_tls = str(tls).lower() in ("enabled", "true")
            env["KAFKA_TLS_ENABLED"] = str(is_tls).lower()
        if (tls_ca := rel_data.get("tls-ca")) and tls_ca != "disabled":
            env["KAFKA_TLS_CA"] = tls_ca
        return env

    def to_env_vars(self) -> dict[str, str]:
        """Produce workload environment variables (EnvVarConvertible protocol)."""
        return self.get_env_vars()
