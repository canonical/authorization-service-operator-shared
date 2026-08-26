# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""CLI wrapper for the /usr/bin/app binary via Pebble exec."""

import json
import logging
from dataclasses import dataclass

import ops

from .constants import APP_BINARY, PEBBLE_SERVICE_NAME
from .exceptions import CreateFgaModelError, WorkloadError

logger = logging.getLogger(__name__)


@dataclass
class CmdExecConfig:
    """Configuration for a Pebble exec command.

    Attributes:
        service_context: The Pebble service context to exec within.
        environment: Extra environment variables for the process.
        timeout: Maximum seconds to wait for the command.
        stdin: Optional stdin content.
    """

    service_context: str
    environment: dict[str, str]
    timeout: int
    stdin: str | None = None


class CommandLine:
    """Wraps workload binary execution via Pebble exec.

    Args:
        container: The Pebble container to exec within.
        app_binary: Binary path to run. Defaults to APP_BINARY (/usr/bin/app).
        service_context: Pebble service context. Defaults to PEBBLE_SERVICE_NAME.
    """

    def __init__(
        self,
        container: ops.Container,
        app_binary: str = APP_BINARY,
        service_context: str = PEBBLE_SERVICE_NAME,
    ) -> None:
        self._container = container
        self.app_binary = app_binary
        self.service_context = service_context

    def _run_cmd(self, cmd: list[str], exec_config: CmdExecConfig) -> tuple[str, str]:
        """Run a command via Pebble exec and return (stdout, stderr).

        Args:
            cmd: Command and arguments.
            exec_config: Execution configuration.

        Returns:
            Tuple of (stdout, stderr) strings.

        Raises:
            WorkloadError: If the command exits with a non-zero status.
        """
        try:
            process = self._container.exec(
                cmd,
                service_context=exec_config.service_context,
                environment=exec_config.environment,
                timeout=exec_config.timeout,
                stdin=exec_config.stdin,
            )
            stdout, stderr = process.wait_output()
            return stdout, stderr
        except ops.pebble.ExecError as e:
            raise WorkloadError(f"Command {cmd} failed with exit code {e.exit_code}: {e.stderr}") from e
        except Exception as e:
            raise WorkloadError(f"Command {cmd} failed: {e}") from e

    def _default_config(self) -> CmdExecConfig:
        return CmdExecConfig(
            service_context=self.service_context,
            environment={},
            timeout=30,
        )

    def get_service_version(self) -> str:
        """Return the workload version string.

        Returns:
            Version string from `<app_binary> version`.

        Raises:
            WorkloadError: If the command fails.
        """
        stdout, _ = self._run_cmd([self.app_binary, "version"], self._default_config())
        text = stdout.strip()
        if ":" in text:
            text = text.split(":", 1)[1].strip()
        return text

    def run_migration(self, dsn: str) -> None:
        """Run database migrations.

        Args:
            dsn: The PostgreSQL DSN connection string.

        Raises:
            WorkloadError: If the migration command exits non-zero.
        """
        config = CmdExecConfig(
            service_context=self.service_context,
            environment={},
            timeout=120,
        )
        self._run_cmd([self.app_binary, "migrate", "--dsn", dsn], config)

    def migrate_status(self, dsn: str) -> bool:
        """Check whether a database migration is pending.

        Args:
            dsn: The PostgreSQL DSN connection string.

        Returns:
            True if migration is needed, False if up-to-date.

        Raises:
            WorkloadError: On unexpected failure.
        """
        config = CmdExecConfig(
            service_context=self.service_context,
            environment={},
            timeout=30,
        )
        try:
            stdout, _ = self._run_cmd([self.app_binary, "migrate", "status", "--dsn", dsn], config)
            return "pending" in stdout.lower()
        except WorkloadError as e:
            if "exit code 1" in str(e):
                return True
            raise

    def create_openfga_model(self, store_id: str, env: dict[str, str] | None = None) -> str:
        """Write the OpenFGA authorization model and return its ID.

        The OpenFGA connection details (address, API key) are read from env
        or the container's environment variables set by the Pebble layer.

        Args:
            store_id: The OpenFGA store ID to write the model into.
            env: Optional environment variables for OpenFGA connection.

        Returns:
            The authorization model ID.

        Raises:
            CreateFgaModelError: If the command fails or the model ID cannot
                be found in the output.
        """
        exec_env = dict(env) if env else {}
        if store_id:
            exec_env["OPENFGA_STORE_ID"] = store_id
        if not exec_env.get("OPENFGA_AUTHORIZATION_MODEL_ID"):
            exec_env["OPENFGA_AUTHORIZATION_MODEL_ID"] = "0"

        cmd = [self.app_binary, "authz", "write-model", store_id]
        if address := exec_env.get("OPENFGA_ADDRESS"):
            cmd.extend(["--fga-address", address])
        if api_key := exec_env.get("OPENFGA_API_KEY"):
            cmd.extend(["--fga-api-key", api_key])

        logger.info(
            "Executing write-model command store_id=%s with env_keys=%s, has_token=%s",
            store_id,
            list(exec_env.keys()),
            bool(exec_env.get("OPENFGA_API_KEY")),
        )

        config = CmdExecConfig(
            service_context=self.service_context,
            environment=exec_env,
            timeout=60,
        )

        try:
            stdout, stderr = self._run_cmd(cmd, config)
            logger.info("write-model completed. stdout=%s, stderr=%s", stdout, stderr)

        except WorkloadError as err:
            logger.error("Failed to write OpenFGA model: %s", err)
            raise CreateFgaModelError(f"Failed to write OpenFGA model: {err}") from err

        for line in f"{stdout}\n{stderr}".splitlines():
            try:
                if model_id := json.loads(line).get("model_id"):
                    return model_id
            except json.JSONDecodeError:
                continue

        raise CreateFgaModelError(
            f"write-model output did not contain a model_id. stdout: {stdout}, stderr: {stderr}"
        )
