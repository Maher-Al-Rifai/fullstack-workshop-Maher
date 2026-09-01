# Module 15 — Demo Guide: Playwright API and Browser Testing

**Audience:** Instructor / reviewer  
**Stack required:** `make e2e-test` (acceptance stack) or `docker compose up --build -d` (dev stack for local run)

---

## Demo 1 — Run the full acceptance stack and see all tests pass (3 min)

```bash
make e2e-test
```

Narrate as it runs:
- Docker builds the production backend and frontend images
- Health chain: `db-test → backend-test → frontend-test`
- `playwright` container starts, runs `npm install`, then `npx playwright test`
- You see `list` reporter output: readiness, journey, api-contract
- Stack tears down cleanly with volumes removed

Point out: **no host ports published** — all traffic is inside Docker. The browser (Chromium) in the Playwright container talks to `frontend-test:3000` via Docker DNS. Client-side API calls go to `backend-test:8000` via Docker DNS.

---

## Demo 2 — Show accessible locators in the journey test (2 min)

Open [e2e/tests/journey.spec.ts](../e2e/tests/journey.spec.ts). Walk through the locators:

```typescript
await page.getByLabel('Full name').fill('E2E User')
await page.getByRole('button', { name: 'Create account' }).click()
await page.getByRole('button', { name: 'Move task to in progress' }).click()
```

Explain:
- `getByLabel` matches the `<label for="...">` element — the same thing a screen reader announces. If the label is wrong, this test fails AND accessibility is broken.
- `getByRole('button', { name: '...' })` matches by accessible name — from button text or `aria-label`. The `TaskCard` button uses `aria-label="Move task to in progress"`, so this is a role + accessible name match.
- No CSS class selectors anywhere — refactoring styles never breaks the tests.

---

## Demo 3 — API contract: invalid transition returns 409 (2 min)

Open [e2e/tests/api-contract.spec.ts](../e2e/tests/api-contract.spec.ts). Show the invalid transition test:

```typescript
const res = await api.patch(`/api/v1/projects/${projectId}/tasks/${taskId}`, {
  headers: { Authorization: `Bearer ${accessToken}` },
  data: { status: 'done' },
})
expect(res.status()).toBe(409)
expect(body.detail.code).toBe('invalid_transition')
```

Explain:
- This uses `APIRequestContext` — no browser, no Chromium, pure HTTP
- The task starts as `backlog` by default. `backlog → done` skips `in_progress` — the state machine rejects it
- We assert `code: 'invalid_transition'` — not just the HTTP status. If the backend changes the error shape, this test catches it
- This test **could not be written** at the Vitest layer because it crosses the real service boundary (FastAPI + PostgreSQL, not mocks)

---

## Demo 4 — SSR proof: project name in raw HTML (2 min)

Show the SSR test in api-contract.spec.ts:

```typescript
const res = await frontend.get(`/public/projects/${projectSlug}`)
expect(res.status()).toBe(200)
const html = await res.text()
expect(html).toContain(projectName)
```

Explain: This is an HTTP GET, not a browser navigation. The response is raw HTML from the Nuxt Nitro server. The `expect(html).toContain(projectName)` assertion proves the project name is in the initial HTML payload — not deferred to a client-side fetch after hydration.

To make this concrete: if you changed the route rule from `swr: 60` to `ssr: false`, the Nuxt server would return an empty shell. This test would **fail** because the project name would only appear after client JavaScript ran. That's exactly the regression we're protecting against.

---

## Demo 5 — Deliberate failure and trace (3 min)

Temporarily break a locator. In `journey.spec.ts`, change:

```typescript
await page.getByRole('button', { name: 'Create account' }).click()
// to:
await page.getByRole('button', { name: 'Submit' }).click()   // wrong name
```

Run:
```bash
docker compose -f compose.test.yaml run --rm playwright
```

You'll see the journey test fail with a timeout. The test artifacts (screenshot, trace) are in `e2e/test-results/`. Show the screenshot: it captures exactly what the page looked like when the test failed — the form is visible, showing the actual button text "Create account".

Restore the locator and re-run to show green.

---

## Demo 6 — Why unique test data matters (1 min)

Point to the timestamp pattern:

```typescript
const ts = Date.now()
const email = `e2e-${ts}@workboard.test`
const projectName = `E2E Project ${ts}`
```

If two CI runs overlap (or you re-run without tearing down), the second run would hit "email already registered" (409) on registration. Unique timestamps guarantee independence.

Show that `make e2e-test` always ends with `down -v` — the database volume is destroyed. The next run starts completely clean.

---

## Key talking points

- **"Every E2E test should be independent."** Shared accounts or projects create ordering dependencies. One test failure cascades into all subsequent tests.
- **"Accessible locators are a quality gate."** If `getByLabel('Email address')` fails because someone removed the `<label>`, the test stops a regression in both the product and its accessibility.
- **"SSR tests are different from E2E tests."** The SSR test is an HTTP assertion, not a browser journey. It runs in milliseconds and proves a specific server-rendering guarantee.
- **"Playwright API request context is not just for setup."** It's the right tool for testing API contracts, HTTP headers, status codes, and response shapes — without the overhead of a browser.
