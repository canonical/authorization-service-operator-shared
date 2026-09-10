## ADDED Requirements

### Requirement: STS Connection Configuration Object
The library SHALL provide an `StsConfig` frozen dataclass holding `jwks_url`, `grpc_address`, `http_address`, and `tls_enabled`.

#### Scenario: STS environment variable conversion
- **WHEN** `StsConfig` is populated with a valid `jwks_url`
- **THEN** `to_env_vars()` SHALL return a dictionary containing `STS_ADDRESS`, `STS_USE_TLS`, `STS_JWKS_URI`, and `EXTAUTHZ_JWK_SET_URL`
