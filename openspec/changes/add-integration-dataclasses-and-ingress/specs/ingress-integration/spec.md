## ADDED Requirements

### Requirement: Istio Ingress Route Submission
The library SHALL provide an `IstioIngressIntegration` class wrapping `IstioIngressRouteRequirer`.

#### Scenario: External URL calculation
- **WHEN** `external_host` is provided by the Istio gateway
- **THEN** `external_url` SHALL return `https://<host>` when TLS is enabled or `http://<host>` otherwise

#### Scenario: Route submission
- **WHEN** `submit_routes()` is called with a path prefix and service port
- **THEN** it SHALL compile and submit `IstioIngressRouteConfig` to the Istio Gateway API
