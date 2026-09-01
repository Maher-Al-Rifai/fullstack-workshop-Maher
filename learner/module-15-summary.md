# Module 15 — Playwright API and Browser End-to-End Testing

**Date:** 2026-09-01
**Branch:** `learning/15-playwright`

---

## Objectives in my own words

Write stable, independent Playwright tests that protect the critical full-stack user journey and the API contract. Use browser locators based on accessible roles and labels — not CSS selectors. Prove that public pages are server-rendered by asserting content in the raw HTTP response, not after client hydration. Use the API for setup and the browser only for what the browser proves.

---

## Key concepts

### Which layer tests what

| Risk | Layer |
|---|---|
| Date formatting, status labels | Vitest unit |
| API client bearer token + 401 retry | Vitest unit |
| TaskCard render, advance button, events | Vitest component |
| Invalid task transition returns 409 | Playwright API request |
| Public SSR page content in raw HTML | Playwright API request |
| Register → task lifecycle → sign out | Playwright browser |
| Service health before browser journey | Playwright API request |

E2E tests are expensive. Keep them on critical paths and integration risks that no lower layer can prove.

### Accessible locators

Playwright's `getByRole`, `getByLabel`, and `getByText` match the DOM the way a user (or screen reader) experiences it. They are resilient to CSS refactoring and enforce accessibility as a side effect. Use `data-testid` only when no role/label unambiguously identifies the element.

```typescript
// ✅ Role + name — survives CSS changes, checks accessibility
page.getByRole('button', { name: 'Create account' })
page.getByLabel('Email address')

// ❌ CSS selector — breaks on class renames
page.locator('.btn-primary')
```

### Auto-wait vs fixed sleep

Playwright auto-waits for elements to be actionable before interacting. `expect(locator).toBeVisible()` waits for visibility. Never use `waitForTimeout` — it makes tests slower and still flaky.

```typescript
// ✅ Observable state
await expect(page.getByText('Done')).toBeVisible()
await expect(page).toHaveURL('/dashboard')

// ❌ Fixed sleep
await page.waitForTimeout(2000)
```

### Independent test data

Each test run generates a unique email and project name via `Date.now()`. Tests never share mutable records — no flaky dependency on insertion order or leftover state from a previous run.

### API request context

`playwrightRequest.newContext({ baseURL })` creates an HTTP client with no browser overhead. It is used to:
- check service readiness before browser tests
- create setup data without going through the UI
- assert API contract (status codes, response shapes) directly

---

## Files created

### `e2e/package.json`
- `@playwright/test@1.49.0` — matches the Docker image `mcr.microsoft.com/playwright:v1.49.0-noble`.

### `e2e/playwright.config.ts`
- `baseURL` from `BASE_URL` env var (default `localhost:3000`).
- `workers: 1` — sequential; the acceptance stack is a single shared environment.
- `retries: 1` in CI — covers transient container startup timing.
- `trace: 'retain-on-failure'` + `screenshot: 'only-on-failure'` — artifacts only when needed.
- Chromium only — widest browser support for the product, lowest CI cost.

### `e2e/tests/readiness.spec.ts` — 2 tests
- `GET /health/ready` on the backend returns 200 + `{ status: 'ready' }`.
- `GET /` on the frontend returns 200 with `text/html` content type.
- Runs before browser journeys; a failure here diagnoses container startup, not the app.

### `e2e/tests/journey.spec.ts` — 1 test
Critical authenticated path:
1. Register with unique email
2. Verify redirect to `/dashboard` and user name visible
3. Create a public project (unique name)
4. Capture slug from card footer
5. Open project → create task → verify "Backlog" badge
6. Advance: "Move task to in progress" → verify "In Progress" badge
7. Advance: "Move task to done" → verify "Done" badge, no further advance button
8. Navigate to `/public/projects/{slug}` → verify project heading
9. Sign out → verify `URL: /` + "Sign in" link visible
10. Navigate to `/dashboard` → verify redirect to `/login`

### `e2e/tests/api-contract.spec.ts` — 2 tests
`test.describe.serial` with shared `beforeAll` setup:
- Register + login via API → access token
- Create project + task via API

**Test 1 — invalid transition:**
`PATCH /api/v1/projects/{id}/tasks/{id}` with `{ status: 'done' }` on a backlog task → 409 + `body.detail.code === 'invalid_transition'`.

**Test 2 — SSR proof:**
`GET /public/projects/{slug}` as raw HTTP → assert response HTML contains the project name. This fails if the page degrades to client-only rendering.

---

## Commands and evidence

```text
# Run the full acceptance stack (build → test → teardown)
make e2e-test

# Or step by step:
docker compose -f compose.test.yaml build
docker compose -f compose.test.yaml run --rm playwright
docker compose -f compose.test.yaml down -v --remove-orphans

# Run locally against the dev stack (requires frontend on :3000, backend on :8000)
cd e2e
npm install
BASE_URL=http://localhost:3000 BACKEND_URL=http://localhost:8000 npx playwright test
npx playwright show-report test-results/report
```

---

## Failure investigated

**Symptom:** `backlog → done` PATCH test fails with status 200 instead of 409.

**Smallest reproduction:** Change the test data so `taskId` refers to a task already in `in_progress` state. That transition IS valid, so the API returns 200.

**Root cause:** `beforeAll` created the task but a previous test run left an `in_progress` task with the same ID in the acceptance database. The test is not independent.

**Fix:** The acceptance stack starts with an empty database (fresh volume on every `make e2e-test` run). Unique `Date.now()` emails and project names ensure no row reuse. Each `make e2e-test` call also runs `down -v` at the end, so the next run is always clean.

**Prevention:** Never share mutable records across test runs. Unique identifiers per run + ephemeral acceptance volume.

---

## Decision and tradeoff

**Decision:** Workers = 1 (sequential tests), Chromium only.

**Alternative:** `fullyParallel: true` with isolated accounts per test, Firefox + WebKit coverage.

**Why chosen:** The acceptance stack is a single shared environment — parallel browser tests against the same database require careful account isolation that adds complexity. Chromium covers the majority browser and is fastest in CI. Firefox/WebKit can be added as a separate project when cross-browser regression is actually observed.

---

## Security, privacy, and operations

- Test accounts use `@workboard.test` domain — clearly non-production addresses.
- The acceptance database is ephemeral and torn down after every run — no test data persists.
- `SECRET_KEY` in the acceptance stack is `test-only-secret-not-for-production` — never reused elsewhere.
- Playwright artifacts (traces, screenshots) are written to a named volume mounted at `e2e/test-results` — not baked into images.
- No passwords or tokens are logged; HTTP-only refresh cookies are never readable by JavaScript.
