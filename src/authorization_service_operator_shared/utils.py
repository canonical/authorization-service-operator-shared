# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Utility functions."""

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import ops

logger = logging.getLogger(__name__)

CharmEventHandler = TypeVar("CharmEventHandler", bound=Callable[..., Any])


def leader_unit(func: CharmEventHandler) -> CharmEventHandler:
    """Decorator that ensures the handler only runs on the leader unit."""

    @wraps(func)
    def wrapper(charm: ops.CharmBase, *args: Any, **kwargs: Any) -> Any | None:
        if not charm.unit.is_leader():
            return None
        return func(charm, *args, **kwargs)

    return wrapper  # type: ignore[return-value]


def container_connectivity(charm: ops.CharmBase, container_name: str) -> bool:
    """Check if the workload container is reachable."""
    return charm.unit.get_container(container_name).can_connect()


def integration_existence(relation_name: str) -> Callable[[ops.CharmBase], bool]:
    """Return a condition function checking if a relation exists on the charm model."""

    def condition(charm: ops.CharmBase) -> bool:
        return bool(charm.model.relations.get(relation_name))

    return condition
