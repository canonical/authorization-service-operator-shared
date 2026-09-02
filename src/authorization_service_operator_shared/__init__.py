# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Shared library for Charmed Authorization Service operators."""

from .cli import CommandLine
from .configs import CharmConfig
from .database import DatabaseConfig, DatabaseRelationHandler
from .exceptions import (
    AuthorizationServiceCharmError,
    ConfigError,
    CreateFgaModelError,
    IntegrationDataError,
    WorkloadError,
)
from .info import (
    AuthorizationServiceInfo,
    AuthorizationServiceInfoProvider,
    AuthorizationServiceInfoRequirer,
)
from .ingress import IstioIngressIntegration
from .kafka import KafkaRelationHandler
from .observability import GrafanaDashboardHandler, MetricsRelationHandler, TracingConfig
from .openfga import OpenFGAConfig, OpenFGAModelData, OpenFGARelationHandler
from .peer import PeerData
from .services import PebbleService, WorkloadService
from .sts import StsConfig, STSRelationHandler
from .utils import container_connectivity, integration_existence, leader_unit

__all__ = [
    "AuthorizationServiceCharmError",
    "AuthorizationServiceInfo",
    "AuthorizationServiceInfoProvider",
    "AuthorizationServiceInfoRequirer",
    "CharmConfig",
    "CommandLine",
    "ConfigError",
    "CreateFgaModelError",
    "DatabaseConfig",
    "DatabaseRelationHandler",
    "GrafanaDashboardHandler",
    "IntegrationDataError",
    "IstioIngressIntegration",
    "KafkaRelationHandler",
    "MetricsRelationHandler",
    "OpenFGAConfig",
    "OpenFGAModelData",
    "OpenFGARelationHandler",
    "PebbleService",
    "PeerData",
    "STSRelationHandler",
    "StsConfig",
    "TracingConfig",
    "WorkloadError",
    "WorkloadService",
    "container_connectivity",
    "integration_existence",
    "leader_unit",
]
