# Module 16 Summary — GitHub Actions CI and Delivery Controls

## What was built

A complete, least-privilege pull-request pipeline in `.github/workflows/ci.yml` that enforces every quality gate from Modules 05–15 on every push and pull request.

## Job DAG

```
backend ──┐
          ├──► containers ──► e2e
frontend ──┘
```

- **backend** and **frontend** run in parallel (fail close to the defect).
- **containers** runs after both pass (validates production build).
- **e2e** runs after containers (validates integration with real infrastructure).

## Workflow file: `.github/workflows/ci.yml`

### Triggers and concurrency

```yaml
on:
  workflow_call:     # reused by deploy-gcp.yml
  pull_request:
  push:
    branches: [main]

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # cancels stale runs on new push
```

### Permissions

```yaml
permissions:
  contents: read   # least privilege; id-token: write stays in deploy only
```

### Backend job — key decisions

| Decision | Reason |
|---|---|
| PostgreSQL service container | Tests real compatibility of ORM schema |
| `cache: pip` with `cache-dependency-path` | Faster re-runs when pyproject.toml is unchanged |
| Separate ruff/mypy/pytest steps | Each failure is attributed to the right tool |
| `--cov-fail-under=80` | Enforces the coverage gate from Module 09 |
| Test secrets in `env:` block | Never committed to org secrets; never available to untrusted PRs |

**Why SQLite tests + PostgreSQL schema verification?**

TestClient fixtures use SQLite for speed and isolation — no service dependency, tests run anywhere. The separate `Base.metadata.create_all(engine)` step verifies that the ORM schema applies cleanly to the real database engine. Once Alembic migrations are scaffolded (Module 06), `alembic upgrade head` replaces the schema step and also validates migration history.

### Frontend job — key decisions

- `npm install --legacy-peer-deps` until `package-lock.json` is committed; then switch to `npm ci` with `cache: npm`.
- `NUXT_TELEMETRY_DISABLED=1` prevents interactive telemetry prompts in CI.
- Four separate steps: lint → typecheck → vitest → build. Each produces a distinct log section.

### Containers job — key decisions

- `docker/setup-buildx-action@v3` enables BuildKit and registry cache.
- `cache-from/cache-to: type=gha,scope=<name>` scoped per image to avoid collisions.
- `push: false` — no registry credentials required on PRs.

### E2E job — key decisions

- Rebuilds images via `docker compose -f compose.test.yaml build` (images are not shared between jobs in GitHub Actions).
- Extracts Playwright artifacts from the named Docker volume using an alpine container — volumes persist after `run --rm` until `down -v`.
- `if: always()` on teardown and artifact upload guarantees cleanup even when tests fail.
- `retention-days: 7` limits storage; artifacts may contain traces with user data.

## Workflow security model

| Concern | Mitigation |
|---|---|
| Untrusted PR code | `pull_request` (not `pull_request_target`) — no write permissions granted |
| Cloud credentials | `id-token: write` present only in `deploy-gcp.yml` job requiring `production` environment |
| Action pinning | Major version pins (`@v7`, `@v6`) with Dependabot weekly updates |
| Secrets exposure | Test credentials are workflow-local `env:` values, not repository secrets |
| Cache poisoning | Scoped caches per image/language reduce blast radius |

## Local vs CI alignment

| Gate | `make verify` | CI |
|---|---|---|
| ruff check/format | ✅ | ✅ |
| mypy | ✅ | ✅ |
| pytest + coverage | ✅ | ✅ |
| eslint | ✅ | ✅ |
| typecheck | ✅ | ✅ |
| vitest | ✅ | ✅ |
| nuxt build | ✅ | ✅ |
| Production image build | via `make up` | ✅ Buildx + cache |
| E2E acceptance | `make e2e-test` | ✅ + artifact upload |

Unavoidable differences: runner architecture (linux/amd64 in CI vs Windows locally), artifact upload, branch protection, cloud OIDC identity.

## Concepts mastered

- **Concurrency groups** cancel redundant in-flight runs on force-push.
- **Service containers** provide real database connectivity without Docker Compose overhead for unit tests.
- **`workflow_call`** enables the deploy workflow to reuse CI as a required gate (`needs: verify`).
- **`if: always()`** ensures teardown and evidence collection regardless of test outcome.
- **Scoped GHA cache** (`scope=backend-prod`) prevents frontend cache invalidating backend layers.

## Files changed

| File | Change |
|---|---|
| `.github/workflows/ci.yml` | Complete rewrite — four jobs, PostgreSQL service, Buildx, E2E with artifact upload |
