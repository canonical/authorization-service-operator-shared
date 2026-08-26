# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Coordinates Secure Token Service (STS) client relations and environment parsing."""

import logging
from dataclasses import dataclass

try:
    from charms.secure_token_service.v0.sts_info import StsInfoRequirer
except ImportError:

    class StsInfoRequirer:  # type: ignore[no-redef]
        """Fallback provider when charms.secure_token_service is not available."""

        def __init__(self, *args, **kwargs) -> None:
            pass


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class StsConfig:
    """Secure Token Service configuration for the workload."""

    jwks_url: str = ""
    grpc_address: str = ""
    http_address: str = ""
    tls_enabled: bool = False

    @property
    def is_ready(self) -> bool:
        """True when mandatory JWKS URL is present."""
        return bool(self.jwks_url)

    def to_env_vars(self) -> dict[str, str]:
        """Convert STS settings to workload environment variables."""
        if not self.is_ready:
            return {}
        return {
            "STS_ADDRESS": self.grpc_address,
            "STS_USE_TLS": str(self.tls_enabled).lower(),
            "STS_JWKS_URI": self.jwks_url,
            "EXTAUTHZ_JWK_SET_URL": self.jwks_url,
        }

    @classmethod
    def load(cls, requirer: StsInfoRequirer) -> "StsConfig":
        """Load STS settings from the sts-info relation requirer helper."""
        try:
            sts_info = requirer.get_sts_info()
            if not sts_info:
                return cls()
            return cls(
                jwks_url=getattr(sts_info, "jwks_url", "") or "",
                grpc_address=getattr(sts_info, "grpc_address", "") or "",
                http_address=getattr(sts_info, "http_address", "") or "",
                tls_enabled=bool(getattr(sts_info, "tls_enabled", False)),
            )
        except Exception:
            return cls()


class STSRelationHandler:
    """Coordinates Secure Token Service (STS) client relations and environment parsing."""

    def __init__(self, charm, relation_name: str = "sts-info") -> None:
        self.charm = charm
        self.relation_name = relation_name
        self.requirer = StsInfoRequirer(charm, relation_name=relation_name)

    @property
    def config(self) -> StsConfig:
        """Return the current STS configuration."""
        return StsConfig.load(self.requirer)

    def is_ready(self) -> bool:
        """Checks if STS integration details are ready."""
        relation = self.charm.model.get_relation(self.relation_name)
        if not relation or not relation.units:
            return False
        return self.config.is_ready

    def get_env_vars(self) -> dict[str, str]:
        """Parses relation details and returns standard Go-binary STS environment variables."""
        return self.config.to_env_vars()

    def to_env_vars(self) -> dict[str, str]:
        """Convert STS settings to workload environment variables."""
        return self.get_env_vars()
