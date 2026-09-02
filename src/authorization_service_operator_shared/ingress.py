# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Coordinates Istio Gateway API configuration for HTTP and gRPC ingress."""

import logging

try:
    from charmlibs.interfaces.istio_ingress_route import (
        BackendRef,
        HTTPPathMatch,
        HTTPPathMatchType,
        HTTPRoute,
        HTTPRouteMatch,
        IstioIngressRouteConfig,
        IstioIngressRouteRequirer,
        Listener,
        ProtocolType,
    )
except ImportError:

    class IstioIngressRouteRequirer:  # type: ignore[no-redef]
        """Fallback provider when charmlibs-interfaces-istio-ingress-route is not available."""

        def __init__(self, *args, **kwargs) -> None:
            pass

    BackendRef = HTTPPathMatch = HTTPPathMatchType = HTTPRoute = HTTPRouteMatch = IstioIngressRouteConfig = Listener = (
        ProtocolType
    ) = None  # type: ignore[misc,assignment]


logger = logging.getLogger(__name__)


class IstioIngressIntegration:
    """Encapsulates the Istio Gateway API configuration for HTTP ingress."""

    def __init__(self, charm, relation_name: str = "ingress") -> None:
        self.requirer = IstioIngressRouteRequirer(charm, relation_name=relation_name)
        self.app_name = charm.app.name
        self.model_name = charm.model.name

    @property
    def external_url(self) -> str | None:
        """Public URL if provided by the Istio gateway."""
        if not self.requirer.external_host:
            return None
        scheme = "https" if self.requirer.tls_enabled else "http"
        return f"{scheme}://{self.requirer.external_host}"

    def submit_routes(self, path_prefix: str = "/v1", service_port: int = 8070) -> None:
        """Compile and submit HTTP routes to the Istio Ingress Gateway."""
        ingress_port = 443 if self.requirer.tls_enabled else 80
        http_listener = Listener(port=ingress_port, protocol=ProtocolType.HTTP)
        config = IstioIngressRouteConfig(
            model=self.model_name,
            listeners=[http_listener],
            http_routes=[
                HTTPRoute(
                    name="authz-http-route",
                    listener=http_listener,
                    matches=[
                        HTTPRouteMatch(path=HTTPPathMatch(type=HTTPPathMatchType.PathPrefix, value=path_prefix)),
                    ],
                    backends=[BackendRef(service=self.app_name, port=service_port)],
                )
            ],
        )
        self.requirer.submit_config(config)
