# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Coordinates Kafka client relations and environment parsing."""

import logging

try:
    from charms.data_platform_libs.v0.data_interfaces import KafkaRequires
except ImportError:

    class KafkaRequires:  # type: ignore[no-redef]
        """Fallback provider when charms.data_platform_libs is not available."""

        def __init__(self, *args, **kwargs) -> None:
            pass


logger = logging.getLogger(__name__)


class KafkaRelationHandler:
    """Coordinates Kafka client relations and environment parsing."""

    def __init__(
        self,
        charm,
        relation_name: str = "kafka",
        consumer_group: str = "authorization-service",
        topic: str = "authorization-service",
    ):
        self.charm = charm
        self.relation_name = relation_name
        self.consumer_group = consumer_group
        self.topic = topic
        self.kafka = KafkaRequires(charm, relation_name=relation_name, topic=topic)

    @property
    def bootstrap_server(self) -> str:
        """Extract Kafka bootstrap server endpoints from KafkaRequires or relation databag."""
        if hasattr(self.kafka, "fetch_relation_data"):
            rel_data = self.kafka.fetch_relation_data(fields=["endpoints"])
            for data in rel_data.values():
                if endpoints := data.get("endpoints"):
                    return endpoints

        relation = self.charm.model.get_relation(self.relation_name)
        if not relation or not relation.app:
            return ""

        return relation.data[relation.app].get("endpoints") or ""

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

        return {
            "KAFKA_BROKERS": self.bootstrap_server,
            "KAFKA_CONSUMER_GROUP": self.consumer_group,
        }
