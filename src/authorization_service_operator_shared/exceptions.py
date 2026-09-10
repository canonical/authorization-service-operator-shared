# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Exception hierarchy for Charmed Authorization Service operator charms and library."""


class AuthorizationServiceCharmError(Exception):
    """Base exception for all authorization service charm errors."""

    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message


class ConfigError(AuthorizationServiceCharmError):
    """Exception raised when configuration parameters are invalid or missing."""


class IntegrationDataError(AuthorizationServiceCharmError):
    """Exception raised when relation integration data is invalid, incomplete, or missing."""


class WorkloadError(AuthorizationServiceCharmError):
    """Exception raised when a workload command fails or container interaction is invalid."""


class CreateFgaModelError(WorkloadError):
    """Exception raised when writing or initializing the OpenFGA model fails."""
