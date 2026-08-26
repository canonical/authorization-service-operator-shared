# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Service layer: PebbleService and WorkloadService."""

import logging
from collections.abc import Mapping
from typing import TYPE_CHECKING, Protocol, TypeAlias

import ops
from ops.pebble import Layer, LayerDict

from .constants import APP_BINARY, GRPC_PORT, HTTP_PORT, PEBBLE_SERVICE_NAME

if TYPE_CHECKING:
    from .cli import CommandLine

logger = logging.getLogger(__name__)

EnvVars: TypeAlias = Mapping[str, str | bool | int | None]


class EnvVarConvertible(Protocol):
    """Protocol for objects that can produce workload environment variables."""

    def to_env_vars(self) -> EnvVars:
        """Return a mapping of environment variable names to values."""
        ...


DEFAULT_CONTAINER_ENV: EnvVars = {
    "GRPC_PORT": str(GRPC_PORT),
    "HTTP_PORT": str(HTTP_PORT),
    "LOG_FORMAT": "json",
    "TELEMETRY_ENABLED": "false",
    "OTEL_SERVICE_NAME": "authorization-service",
}


def make_pebble_layer_dict(
    command: str = f"{APP_BINARY} serve",
    service_name: str = PEBBLE_SERVICE_NAME,
) -> LayerDict:
    """Generate a Pebble layer dictionary with configurable service name and command.

    Args:
        command: Command string to execute for the service.
        service_name: Pebble service name.

    Returns:
        Pebble LayerDict structure.
    """
    return {
        "summary": f"{service_name} layer",
        "services": {
            service_name: {
                "override": "replace",
                "summary": "Authorization Service",
                "command": command,
                "startup": "disabled",
                "on-check-failure": {"ready": "restart"},
            }
        },
        "checks": {
            "ready": {
                "override": "replace",
                "level": "ready",
                "http": {"url": f"http://localhost:{HTTP_PORT}/healthz"},
            }
        },
    }


PEBBLE_LAYER_DICT: LayerDict = make_pebble_layer_dict()


class PebbleService:
    """Encapsulates Pebble operations for the authorization service container.

    Args:
        container: The Pebble container to manage.
        service_name: Pebble service name. Defaults to PEBBLE_SERVICE_NAME.
        command: Command to execute for the service. Defaults to f"{APP_BINARY} serve".
    """

    def __init__(
        self,
        container: ops.Container,
        service_name: str = PEBBLE_SERVICE_NAME,
        command: str = f"{APP_BINARY} serve",
    ) -> None:
        self._container = container
        self.service_name = service_name
        self.command = command

    def render_pebble_layer(
        self,
        *env_var_sources: EnvVarConvertible,
        command: str | None = None,
    ) -> Layer:
        """Build the Pebble layer by merging environment variable sources.

        Args:
            *env_var_sources: Objects implementing EnvVarConvertible. Their
                to_env_vars() outputs are merged in order over DEFAULT_CONTAINER_ENV.
            command: Optional command override for the Pebble service.

        Returns:
            A Pebble Layer with the merged environment.
        """
        env: dict[str, str] = {k: str(v) for k, v in DEFAULT_CONTAINER_ENV.items() if v is not None}
        for source in env_var_sources:
            if hasattr(source, "to_env_vars"):
                source_env = source.to_env_vars()
            elif hasattr(source, "get_env_vars"):
                source_env = source.get_env_vars()
            elif isinstance(source, dict):
                source_env = source
            else:
                source_env = {}
            env.update({k: str(v) for k, v in source_env.items() if v is not None})

        cmd = command or self.command
        base_layer_dict = make_pebble_layer_dict(command=cmd, service_name=self.service_name)
        layer_dict: LayerDict = {
            **base_layer_dict,
            "services": {
                self.service_name: {
                    **base_layer_dict["services"][self.service_name],  # type: ignore[index]
                    "environment": env,
                }
            },
        }
        return Layer(layer_dict)

    def plan(self, layer: Layer, force_restart: bool = False) -> None:
        """Apply the Pebble layer and start or restart the service.

        Args:
            layer: The layer to apply.
            force_restart: If True, restart regardless of current state.
        """
        self._container.add_layer(self.service_name, layer, combine=True)
        self._restart_service(restart=force_restart)

    def _restart_service(self, restart: bool = False) -> None:
        """Start or restart the Pebble service.

        Args:
            restart: If True, force a restart. Otherwise start if stopped,
                or replan if already running.
        """
        if restart:
            self._container.restart(self.service_name)
        elif not self._container.get_service(self.service_name).is_running():
            self._container.start(self.service_name)
        else:
            self._container.replan()

    def stop(self) -> None:
        """Stop the Pebble service."""
        try:
            if self._container.can_connect():
                self._container.stop(self.service_name)
                logger.debug("Service %s stopped", self.service_name)
        except Exception as e:
            logger.warning("Failed to stop service %s: %s", self.service_name, e)


class WorkloadService:
    """Manages the authorization-service workload.

    Args:
        unit: The Juju unit.
        cli: The CommandLine wrapper.
        container: The Pebble container.
        service_name: Name of the Pebble service.
    """

    def __init__(
        self,
        unit: ops.Unit,
        cli: "CommandLine",
        container: ops.Container,
        service_name: str = PEBBLE_SERVICE_NAME,
    ) -> None:
        self._unit = unit
        self._cli = cli
        self._container = container
        self.service_name = service_name

    @property
    def version(self) -> str:
        """Workload version string."""
        return self._cli.get_service_version()

    def update_workload_version(self) -> None:
        """Set the workload version on the unit; absorbs all errors."""
        try:
            v = self.version
            if v:
                self._unit.set_workload_version(v)
        except Exception as e:
            logger.error("Failed to update workload version: %s", e)

    def is_running(self) -> bool:
        """Return True if the service is running and the ready check passes."""
        try:
            svc = self._container.get_service(self.service_name)
            return svc.is_running()
        except Exception:
            return False

    def is_failing(self) -> bool:
        """Return True if the ready check is in a failure state."""
        try:
            check = self._container.get_check("ready")
            return check.status == ops.pebble.CheckStatus.DOWN
        except Exception:
            return False

    def open_port(self) -> None:
        """Open HTTP and gRPC ports on the unit."""
        self._unit.open_port("tcp", HTTP_PORT)
        self._unit.open_port("tcp", GRPC_PORT)

    def create_openfga_model(self, store_id: str, env: dict[str, str] | None = None) -> str:
        """Write the OpenFGA authorization model and return its ID.

        Args:
            store_id: The OpenFGA store ID to write the model into.
            env: Optional environment variables for OpenFGA connection.

        Returns:
            The authorization model ID.

        Raises:
            CreateFgaModelError: If the model creation fails.
        """
        return self._cli.create_openfga_model(store_id, env)
