# Testing strategy

## Principle

Tests are executable risk controls. Select the lowest layer that can fail for the behavior being protected, and add a higher layer only for a distinct integration risk.

```text
Many fast focused tests
├── pure backend domain rules
├── frontend utilities/composables
├── service/repository behavior
├── API and component contracts
├── migration and production builds
└── few critical browser journeys
```

Do not duplicate every scenario at every layer.

## Backend unit tests

Location: `backend/tests/unit/`

Use for deterministic functions and business rules without HTTP or database dependencies. Examples:

- slug normalization;
- allowed task transition;
- authorization policy function if extracted;
- date/priority calculation.

A unit test should be fast, explicit, and free from network/filesystem/database setup unless that dependency is the unit.

## Backend API integration tests

Location: `backend/tests/integration/`

FastAPI `TestClient` exercises routing, dependencies, schemas, auth, service coordination, and response contracts. The baseline uses an isolated in-memory SQLite database for speed, while CI separately runs Alembic against PostgreSQL.

Important limitation: SQLite does not reproduce every PostgreSQL behavior. Add PostgreSQL-backed repository/constraint tests when a query, type, transaction, or index depends on PostgreSQL semantics.

Required behavior categories:

- happy path;
- invalid request;
- missing authentication;
- resource authorization denial;
- not found;
- conflict/business-rule failure;
- side effect/persistence.

## Migration tests

At minimum, CI applies `alembic upgrade head` to empty PostgreSQL. Stronger projects should also:

- upgrade from the last released revision;
- run data backfill assertions;
- execute a supported downgrade for reversible changes;
- run `alembic check` to detect model drift;
- start the new application against the migrated schema.

## Frontend unit tests

Location: `frontend/tests/unit/`

Protect deterministic formatting, mapping, validation, and composable logic. Avoid testing Vue or browser behavior through a pure utility test.

## Component tests

Location: `frontend/tests/components/`

Render a component and assert user-visible behavior:

- text and semantic elements;
- prop-driven states;
- emitted events after interaction;
- disabled/loading behavior;
- accessible label/name where practical.

Do not assert private refs, internal method names, or exact implementation markup without a user contract.

## Frontend API-client tests

Location: `frontend/tests/services/`

Use a controlled fetcher to protect:

- base URL and headers;
- request body/method forwarding;
- one refresh-and-retry after `401`;
- prevention of infinite refresh loops;
- normalized error behavior.

These tests do not prove the real backend contract; the end-to-end stack covers that boundary.

## Playwright API tests

Use Playwright's request context for:

- readiness checks;
- creating deterministic test data through public APIs;
- verifying a small number of deployed HTTP contracts;
- cleaning up data when appropriate.

Do not bypass the browser for the user behavior the test is supposed to prove.

## Browser end-to-end tests

Location: `e2e/tests/`

Protect only critical journeys:

- frontend and backend health;
- registration/sign-in;
- project and task creation;
- status transition and invalid transition;
- sign-out/protected route;
- public server-rendered project metadata.

Stability rules:

- wait for observable UI/network state, never arbitrary sleep;
- use accessible roles/labels or deliberate `data-testid` for ambiguous domain elements;
- create unique data per test;
- keep tests independent;
- retain trace/screenshot/video only on failure to control storage and sensitive evidence;
- use the version-matched Playwright container image.

## Contract and schema tests

The generated OpenAPI schema can be snapshotted selectively or validated for required paths/security definitions. Avoid a huge snapshot that turns every harmless ordering change into noise. A stronger extension generates the TypeScript API client from OpenAPI and checks drift.

## Coverage

Backend CI enforces a minimum branch-aware coverage threshold as a guardrail. Coverage cannot prove assertion quality, production configuration, authorization completeness, concurrency, or performance.

Review coverage changes by asking:

- which risk became protected;
- whether the test fails under a plausible mutation;
- whether uncovered code is intentional glue or an untested branch;
- whether a high number hides weak assertions.

## Manual exploratory testing

Automated tests do not replace exploration. Before a gate, inspect:

- slow network and offline behavior;
- keyboard navigation and focus;
- narrow/mobile viewport;
- long text and empty content;
- expired token and database outage;
- duplicate submissions;
- logs without secret/personal-data leakage;
- fresh database and existing database upgrade.

Record discovered defects as reproducible tests whenever the regression risk is material.
