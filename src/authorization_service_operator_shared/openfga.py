# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Coordinates OpenFGA integration details and token parsing."""

import logging
from dataclasses import dataclass
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class OpenFGAConfig:
    """OpenFGA client configuration for the workload."""

    address: str = ""
    token: str = ""
    store_id: str = ""
    authorization_model_id: str = ""

    @property
    def is_ready(self) -> bool:
        """True when mandatory connection fields are present."""
        return bool(self.address and self.store_id and self.token)

    @property
    def api_scheme(self) -> str:
        """URL scheme (e.g. ``http`` or ``https``)."""
        return urlparse(self.address).scheme or "http"

    @property
    def api_host(self) -> str:
        """Host and port portion of the address URL."""
        return urlparse(self.address).netloc or self.address

    def to_env_vars(self) -> dict[str, str]:
        """Convert OpenFGA settings to workload environment variables."""
        if not self.is_ready:
            return {}
        return {
            "OPENFGA_ADDRESS": self.address,
            "OPENFGA_STORE_ID": self.store_id,
            "OPENFGA_API_KEY": self.token,
            "OPENFGA_API_SCHEME": self.api_scheme,
            "OPENFGA_API_HOST": self.api_host,
            "OPENFGA_AUTHORIZATION_MODEL_ID": self.authorization_model_id,
        }


@dataclass(frozen=True, slots=True)
class OpenFGAModelData:
    """OpenFGA authorization model settings for the workload."""

    model_id: str = ""

    def to_env_vars(self) -> dict[str, str]:
        """Convert OpenFGA model settings to workload environment variables."""
        return {"OPENFGA_AUTHORIZATION_MODEL_ID": self.model_id}

    @classmethod
    def load(cls, source: dict | str | None) -> "OpenFGAModelData":
        """Load OpenFGA model data from a dict (e.g. peer databag) or string."""
        if not source:
            return cls()
        if isinstance(source, str):
            return cls(model_id=source)
        if isinstance(source, dict):
            model_id = (
                source.get("openfga_model_id") or source.get("authorization_model_id") or source.get("model_id") or ""
            )
            return cls(model_id=model_id)
        return cls()


class OpenFGARelationHandler:
    """Wrapper around OpenFGARequires for structured data access."""

    def __init__(self, openfga_requirer) -> None:
        self.openfga = openfga_requirer

    @property
    def config(self) -> OpenFGAConfig:
        """Return current OpenFGA configuration."""
        if not self.openfga or not (provider_data := self.openfga.get_store_info()):
            return OpenFGAConfig()

        return OpenFGAConfig(
            address=getattr(provider_data, "http_api_url", "") or getattr(provider_data, "address", "") or "",
            store_id=getattr(provider_data, "store_id", "") or "",
            token=getattr(provider_data, "token", "") or "",
            authorization_model_id=getattr(provider_data, "authorization_model_id", "") or "",
        )

    def is_ready(self) -> bool:
        """Checks if OpenFGA details are ready in the relation databag."""
        return self.config.is_ready

    def get_env_vars(self) -> dict[str, str]:
        """Parses relation details and returns standard Go-binary OpenFGA environment variables."""
        return self.config.to_env_vars()

    def to_env_vars(self) -> dict[str, str]:
        """Convert OpenFGA settings to workload environment variables."""
        return self.get_env_vars()
