# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Access peer relation app-level databag with JSON serialization."""

import json
import logging
from typing import Any

from ops.model import Model

logger = logging.getLogger(__name__)


class PeerData:
    """Access peer relation app-level databag.

    Only the leader unit may write; all units may read.
    Values are JSON-encoded to support non-string types.
    """

    def __init__(self, model: Model, relation_name: str = "authorization-service-peers") -> None:
        self._model = model
        self._app = model.app
        self.relation_name = relation_name

    def __getitem__(self, key: str) -> Any:
        """Return the JSON-decoded value for *key*, or an empty dict if absent."""
        if not (peers := self._model.get_relation(self.relation_name)):
            return {}
        value = peers.data[self._app].get(key)
        return json.loads(value) if value else {}

    def __setitem__(self, key: str, value: Any) -> None:
        """Write *value* (JSON-encoded) for *key*."""
        if not (peers := self._model.get_relation(self.relation_name)):
            logger.warning("Peer relation %s not found; cannot write key %s", self.relation_name, key)
            return
        peers.data[self._app][key] = json.dumps(value)

    def get(self, key: str, default: Any = None) -> Any:
        """Return the JSON-decoded value for *key*, or *default* if absent."""
        if not (peers := self._model.get_relation(self.relation_name)):
            return default
        if key not in peers.data[self._app]:
            return default
        value = peers.data[self._app].get(key)
        return json.loads(value) if value else default

    def pop(self, key: str) -> Any:
        """Remove and return the value for *key*, or an empty dict if absent."""
        if not (peers := self._model.get_relation(self.relation_name)):
            return {}
        data = peers.data[self._app].pop(key, None)
        return json.loads(data) if data else {}
