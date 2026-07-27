# Module 15: Playwright API and browser end-to-end testing

**Guided effort:** 10 hours  
**Required branch:** `learning/15-playwright`  
**Phase:** Integration

## Objectives

- Use Playwright request contexts for readiness/data setup and browsers for user-observable journeys.
- Write stable independent tests using accessible locators, unique data, and observable waits.
- Capture traces/screenshots/logs on failure and diagnose a deliberate flake.
- Validate public SSR content and critical authenticated workflows across real service boundaries.

## Prerequisites

- Module 14 acceptance stack available.
- Critical product journey works manually.

## Concepts and context

End-to-end tests provide broad confidence at high cost. Keep them focused on critical paths and integration risks that lower layers cannot prove. They should use the same production images and real PostgreSQL schema used by the acceptance stack.

Playwright auto-waits for actionable conditions. Fixed sleeps make tests slower and still flaky. Accessible role/label locators align tests with user interaction; deliberate test IDs are acceptable for ambiguous domain instances.

## Step-by-step lab

### 1. Inspect Playwright configuration

Read `e2e/playwright.config.ts`, package version, and Docker image tag. Confirm the Playwright package and browser image versions match. Understand base URL, retries, workers, reporter, trace, screenshot, video, and artifact directories.

### 2. Add API readiness checks

Use Playwright's request fixture/context to call backend readiness and frontend health. Assert status/body. This provides early diagnosis before a browser journey fails on a blank page.

### 3. Create independent test data

Generate a unique email/project name per test using deterministic timestamp/UUID-safe values. Prefer public APIs for setup when the UI behavior is not under test. Do not insert directly into the database unless the explicit objective is a database fixture.

### 4. Implement critical browser journey

A complete baseline test:

1. register;
2. verify protected projects page;
3. create a public project;
4. open project;
5. create a task;
6. move backlog to in progress to done;
7. verify visible state;
8. open public page;
9. sign out;
10. verify protected navigation returns to login.

Use labels/roles and domain test IDs only where repeated cards require identity.

### 5. Test invalid transition through API or UI

The UI may hide direct backlog-to-done controls. Use Playwright API request to create a backlog task and call the invalid patch, asserting `409` and stable error code. This protects real deployed API behavior without distorting the UI.

### 6. Test SSR and metadata

Request the public page as HTTP and/or navigate in browser. Assert title, description, heading, and project content. Ensure the test would fail if content only appeared after a delayed client fetch when SSR is the objective.

### 7. Remove nondeterminism

Search for `waitForTimeout` and replace with:

- `expect(locator).toBeVisible()`;
- response wait tied to the action;
- URL/navigation assertion;
- readiness endpoint;
- stable state text.

Keep tests independent of order and shared seeded mutable records except the intentionally read-only seeded public page.

### 8. Failure and trace drill

Temporarily break a locator or backend behavior. Run with trace retention and inspect:

```bash
cd e2e
npx playwright test
npx playwright show-report
# or inspect artifacts produced by make e2e-test
```

Identify the first incorrect observable state, not only the final timeout. Restore and verify.

### 9. Cross-browser decision

Run critical smoke in Chromium by default. Evaluate Firefox/WebKit based on product browser support and CI cost. Document the support matrix rather than assuming all browsers or none.

## Validation checklist

- [ ] Playwright package and browser image versions match.
- [ ] Readiness failures are distinguishable from browser journey failures.
- [ ] Tests create unique independent data.
- [ ] Critical authenticated journey runs against production images and PostgreSQL.
- [ ] Invalid transition returns 409 through the real API boundary.
- [ ] Public SSR metadata/content is protected.
- [ ] No arbitrary fixed sleeps remain.
- [ ] A deliberate failure produced a useful trace and diagnosis.

## Independent challenge

Add a mobile viewport journey that checks responsive navigation and task creation without duplicating the entire desktop suite. Explain which responsive risk merits the extra test.

## Common failure modes

- Using one shared account/project across parallel tests.
- Waiting a fixed number of milliseconds.
- Selecting by fragile CSS/layout text when a role/label exists.
- Testing every edge case through the browser.
- Ignoring traces and increasing timeouts instead.

## Evidence to submit

- Playwright report/trace from a passing and deliberate failing run.
- Critical journey outline and locator choices.
- Invalid transition API evidence.
- SSR test explanation.
- Cross-browser support decision.

## Commit checkpoint

```text
test(e2e): protect critical full-stack user journeys
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [README.md](../e2e/README.md)
- [testing-strategy.md](../docs/testing-strategy.md)
- [intro](https://playwright.dev/docs/intro)
- [api-testing](https://playwright.dev/docs/api-testing)
- [trace-viewer](https://playwright.dev/docs/trace-viewer)
