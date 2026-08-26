# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Constants used by Charmed Authorization Service operator charms and library."""

# Workload binary details
APP_BINARY = "/usr/bin/app"

# Service defaults
PEBBLE_SERVICE_NAME = "authorization-service"
DEFAULT_PORT = 8080
HTTP_PORT = 8070
GRPC_PORT = 9091

# Metrics / Observability defaults
DEFAULT_METRICS_PORT = 9090
DEFAULT_METRICS_PATH = "/metrics"

# Log and directory config defaults
DEFAULT_LOG_LEVEL = "info"
