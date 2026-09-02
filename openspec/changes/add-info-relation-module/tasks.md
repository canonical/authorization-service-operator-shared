## 1. Implementation

- [x] 1.1 Create `src/authorization_service_operator_shared/info.py` implementing `AuthorizationServiceInfo`, `AuthorizationServiceInfoProvider`, `AuthorizationServiceInfoRequirer`, and associated event classes.
- [x] 1.2 Export `AuthorizationServiceInfo`, `AuthorizationServiceInfoProvider`, and `AuthorizationServiceInfoRequirer` in `src/authorization_service_operator_shared/__init__.py`.

## 2. Testing & Quality

- [x] 2.1 Add comprehensive unit tests in `tests/unit/test_info.py` covering model readiness, leader/non-leader provider publishing, and requirer parsing.
- [x] 2.2 Verify code quality and formatting with `uv run ruff check` and `uv run pytest`.

## 3. Documentation

- [x] 3.1 Update `README.md` package layout and importing patterns.
- [x] 3.2 Update OpenSpec artifacts in `openspec/changes/add-info-relation-module/`.
