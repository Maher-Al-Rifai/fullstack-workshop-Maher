# Module 16 Demo Guide — GitHub Actions CI and Delivery Controls

## Prerequisites

- GitHub repository with the module 16 branch pushed.
- (Optional) Branch protection ruleset configured on `main`.

---

## Demo 1: Inspect the workflow DAG and explain each job

**Show the file:**

```
.github/workflows/ci.yml
```

**Walk through the DAG:**

```
backend ──┐
          ├──► containers ──► e2e
frontend ──┘
```

Point out:

- `workflow_call` trigger — this CI is also reused by `deploy-gcp.yml` so no duplicate gates.
- `concurrency: cancel-in-progress: true` — force-pushing a fixup cancels the stale run.
- `permissions: contents: read` at the top — every job inherits least privilege.

---

## Demo 2: Show a deliberate failure blocking a PR

**On the module branch, break a backend test:**

```bash
# In backend/tests/ — comment out the closing `assert` in any test
git add -A
git commit -m "deliberate test failure for demo"
git push origin learning/16-github-actions
```

Open the PR. Show:

- **backend** job turns red ⟹ **containers** and **e2e** are skipped (dependency gate).
- The PR cannot be merged if required checks are configured.

**Restore and push:**

```bash
git revert HEAD --no-edit
git push origin learning/16-github-actions
```

Show all four jobs turn green.

---

## Demo 3: Backend job — PostgreSQL service + separate steps

Navigate to the backend job log and point out:

1. **Postgres service health check** passes before any step runs.
2. **Ruff lint** — dedicated step, separate log entry.
3. **Ruff format** — separate step; a misplaced blank line is attributed here, not in pytest.
4. **Mypy** — catches type errors not caught by runtime tests.
5. **Schema verify** — runs `Base.metadata.create_all(engine)` against the real PostgreSQL service; shows `Schema applied to PostgreSQL — OK`.
6. **Pytest** — shows coverage table; fails if below 80%.

**Explain the SQLite vs PostgreSQL split:**

> TestClient fixtures always use SQLite for speed. The schema step verifies ORM compatibility with the real engine. Once Alembic migrations exist, `alembic upgrade head` replaces this and also validates migration ordering.

---

## Demo 4: Frontend job — four named steps

Point out in the log:

1. `npm install --legacy-peer-deps` — comment where to switch to `npm ci` + lockfile.
2. `ESLint` — catches style and import issues.
3. `TypeScript — type check` — Nuxt-aware typecheck, not just `tsc`.
4. `Vitest` — 41 tests, fast, no browser.
5. `Nuxt — production build` — confirms SSR bundle compiles.

---

## Demo 5: Containers job — Buildx + GHA cache

Show in the log:

- `docker/setup-buildx-action` enables BuildKit.
- `cache-from: type=gha,scope=backend-prod` — on second run, many layers are `CACHED`.
- `push: false` — no registry credentials needed for PRs; the image is discarded after verification.

**Explain scoped cache:**

> Each image has its own cache scope (`backend-prod`, `frontend-prod`). A Python dependency change invalidates only the backend cache, not the frontend cache.

---

## Demo 6: E2E job — artifact upload and teardown

Navigate to the e2e job log and show:

1. **Build acceptance stack** — separate from the containers job because GitHub Actions jobs don't share Docker images.
2. **Run Playwright tests** — all three spec files execute.
3. **Extract Playwright artifacts** — copies from named Docker volume using a one-off alpine container.
4. **Upload Playwright report** — even when tests pass, the artifact is available for 7 days.
5. **Tear down** — `down -v --remove-orphans` runs under `if: always()`.

**Trigger a failure to see the artifact:**

- Temporarily break a journey locator in `e2e/tests/journey.spec.ts`.
- Push and let CI run.
- Download the `playwright-report` artifact; open `index.html` to see the trace and screenshot.

---

## Demo 7: Security model walk-through

Point out in the workflow file:

```yaml
permissions:
  contents: read        # top-level default for all jobs
```

Open `deploy-gcp.yml` and show:

```yaml
permissions:
  contents: read
  id-token: write       # only here, in a production-environment-gated job
```

Explain:

- A PR from a fork cannot trigger `pull_request_target` because the workflow uses `pull_request`.
- Workflow-local `env:` values (test secrets) are never stored as repository secrets and are not accessible to cloud providers.
- Dependabot opens weekly PRs for action major-version bumps (`@v7` → `@v8`).

---

## Demo 8: Local vs CI parity

```bash
# Run the same gates locally
make verify       # backend ruff + mypy + pytest, frontend lint + typecheck + vitest + build
make e2e-test     # compose.test.yaml acceptance stack
```

Show that the output is equivalent to the CI log. Note unavoidable differences:

- Linux/amd64 runner vs Windows locally.
- Artifact upload only in CI.
- Branch protection enforcement only on GitHub.

---

## Validation checklist to complete before sign-off

- [ ] All four CI jobs pass on `learning/16-github-actions` branch.
- [ ] Deliberate failure demo shows blocked PR and correct job attribution.
- [ ] Playwright failure artifact downloaded and trace inspected.
- [ ] `id-token: write` confirmed absent from `ci.yml`.
- [ ] `make verify` output matches CI log for backend and frontend gates.
- [ ] Teardown step runs under `if: always()` — confirmed by checking logs even on success.
