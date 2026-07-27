# Module 13: Frontend testing with Vitest

**Guided effort:** 10 hours  
**Required branch:** `learning/13-frontend-tests`  
**Phase:** Frontend

## Objectives

- Choose unit, component, API-client, Nuxt route/SSR, and browser tests based on distinct risks.
- Write Vitest tests that assert user-observable behavior and typed transport behavior.
- Mock boundaries deliberately without mocking the subject under test.
- Use failures/mutations to improve weak frontend tests.

## Prerequisites

- Modules 10–12 complete.
- Frontend builds and communicates with backend.

## Concepts and context

Frontend tests often become brittle when they assert component internals, exact markup, or implementation-specific calls. Prefer user-visible text, accessible roles/names, emitted domain events, and transport contracts. A component test does not prove the backend; an E2E test does not explain a pure formatter failure.

Nuxt-aware tests can provide runtime context, while pure utilities should remain in a simple environment. Keep mocks small and representative. Test error/loading/empty behavior because those states are where real integrations fail.

## Step-by-step lab

### 1. Build a frontend risk map

Assign the lowest useful layer to:

- date formatting;
- status label mapping;
- task card advance event;
- form disabled while saving;
- API base/header/body behavior;
- one refresh/retry after 401;
- auth middleware redirect;
- server-rendered public metadata;
- complete registration/project/task journey.

Reserve the last for Playwright in Module 15.

### 2. Configure Vitest/Nuxt test utilities

Inspect `vitest.config.ts`. Keep test files under `frontend/tests/`. Understand `happy-dom`/Nuxt environment limits compared with real browsers. Add setup only for shared behavior that genuinely applies to every test.

### 3. Test pure utilities

Add table-driven tests for:

- status and priority labels;
- date formatting including null/invalid policy;
- API error normalization.

Avoid snapshots for simple strings. Assert exact contract.

### 4. Test components

For `TaskCard` and at least one form/display component:

- render representative props;
- assert visible status/priority/title;
- interact with an accessible button;
- assert emitted `advance`/`remove` payload;
- assert unavailable transitions do not show/enable incorrect controls;
- assert loading/disabled state where applicable.

Use `data-testid` only when role/name cannot identify a domain element reliably.

### 5. Test API client

Inject a fake fetcher and token/refresh callbacks. Cover:

- request base URL and bearer header;
- body/method forwarding;
- normal success;
- first 401 triggers refresh and one retry with new token;
- refresh failure calls unauthenticated handler;
- second 401 does not recurse;
- non-401 error is normalized.

Do not mock the API client's own request function.

### 6. Test auth store or middleware

Choose one meaningful behavior such as initialized unauthenticated redirect or logout state clearing after network failure. Use Nuxt test utilities when route/plugin context is required.

### 7. Mutation drill

Temporarily:

- reverse the status label;
- emit the wrong task ID;
- allow API client to refresh repeatedly.

Run narrow tests and record failures. Improve any surviving case.

### 8. Run quality and inspect test duration

```bash
npm run lint
npm run typecheck
npm test
npm run build
```

Tests should be fast enough for every PR. Do not move stable component behavior into Playwright merely because setup feels easier.

## Validation checklist

- [ ] Risk map separates unit, component, API-client, Nuxt, and E2E responsibilities.
- [ ] Utility tests protect deterministic contracts.
- [ ] Component tests assert visible behavior and emitted domain events.
- [ ] API client tests prove one refresh/retry and no infinite loop.
- [ ] At least one auth/middleware state is protected.
- [ ] Three deliberate mutations are detected after improvements.
- [ ] Lint, typecheck, tests, and production build pass.

## Independent challenge

Add an accessibility-focused component test that queries by role/name and verifies an error is announced/associated appropriately. Explain what still requires a real browser/manual assistive-technology review.

## Common failure modes

- Testing private refs or exact component implementation.
- Mocking the function being tested.
- Using snapshots as the only assertion for interactive behavior.
- Testing only success and ignoring loading/error/empty.
- Duplicating every component scenario in Playwright.

## Evidence to submit

- Frontend test risk map.
- Test output and duration.
- Mutation table.
- One component test explanation.
- One API-client refresh test explanation and what it does not prove.

## Commit checkpoint

```text
test(web): protect components and API client behavior
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [testing-strategy.md](../docs/testing-strategy.md)
- [testing](https://nuxt.com/docs/getting-started/testing)
- [https://vitest.dev/guide/](https://vitest.dev/guide/)
- [https://test-utils.vuejs.org/](https://test-utils.vuejs.org/)
