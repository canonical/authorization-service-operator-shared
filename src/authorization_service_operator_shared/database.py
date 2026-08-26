# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Coordinates PostgreSQL client relations and environment parsing."""

import logging
from dataclasses import dataclass
from string import Template

try:
    from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
except ImportError:

    class DatabaseRequires:  # type: ignore[no-redef]
        """Fallback provider when charms.data_platform_libs is not available."""

        def __init__(self, *args, **kwargs) -> None:
            pass


logger = logging.getLogger(__name__)

POSTGRESQL_DSN_TEMPLATE = Template("postgres://$username:$password@$endpoint/$database")


@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    """Database connection settings for the workload."""

    host: str = ""
    port: str = ""
    dbname: str = ""
    username: str = ""
    password: str = ""

    @property
    def is_ready(self) -> bool:
        """True when all connection fields are populated."""
        return bool(self.host and self.port and self.dbname and self.username and self.password)

    @property
    def dsn(self) -> str:
        """PostgreSQL DSN connection string."""
        return POSTGRESQL_DSN_TEMPLATE.substitute(
            username=self.username,
            password=self.password,
            endpoint=f"{self.host}:{self.port}",
            database=self.dbname,
        )

    def to_env_vars(self) -> dict[str, str]:
        """Convert database settings to workload environment variables."""
        if not self.is_ready:
            return {}
        return {
            "POSTGRES_HOST": self.host,
            "POSTGRES_PORT": self.port,
            "POSTGRES_USER": self.username,
            "POSTGRES_PASSWORD": self.password,
            "POSTGRES_DB": self.dbname,
        }

    @classmethod
    def load(cls, requirer: DatabaseRequires) -> "DatabaseConfig":
        """Load database settings from the database relation requirer helper."""
        if not hasattr(requirer, "relations") or not requirer.relations:
            return cls()

        integration_id = requirer.relations[0].id
        integration_data: dict[str, str] = requirer.fetch_relation_data().get(integration_id, {})

        endpoint = integration_data.get("endpoints", "").split(",")[0]
        host, _, port = endpoint.rpartition(":")

        dbname = ""
        raw_db = getattr(requirer, "database", None)
        if isinstance(raw_db, str) and raw_db:
            dbname = raw_db
        else:
            raw_db_name = getattr(requirer, "database_name", None)
            if isinstance(raw_db_name, str):
                dbname = raw_db_name

        return cls(
            host=host,
            port=port or "5432",
            dbname=dbname,
            username=integration_data.get("username", ""),
            password=integration_data.get("password", ""),
        )


class DatabaseRelationHandler:
    """Coordinates PostgreSQL client relations and environment parsing."""

    def __init__(self, charm, relation_name: str = "database", database_name: str = "authorization_service") -> None:
        self.charm = charm
        self.relation_name = relation_name
        self.database_name = database_name
        self.postgres = DatabaseRequires(charm, relation_name=relation_name, database_name=database_name)

    @property
    def config(self) -> DatabaseConfig:
        """Return the current database configuration."""
        return DatabaseConfig.load(self.postgres)

    @property
    def dsn(self) -> str:
        """Return the PostgreSQL DSN connection string."""
        return self.config.dsn

    def is_ready(self) -> bool:
        """Checks if database credentials are ready in the relation databag."""
        relation = self.charm.model.get_relation(self.relation_name)
        if not relation or not relation.units:
            return False
        return self.config.is_ready

    def get_env_vars(self) -> dict[str, str]:
        """Parses relation credentials and returns standard Go-binary postgres environment variables."""
        return self.config.to_env_vars()

    def to_env_vars(self) -> dict[str, str]:
        """Convert database settings to workload environment variables."""
        return self.get_env_vars()
