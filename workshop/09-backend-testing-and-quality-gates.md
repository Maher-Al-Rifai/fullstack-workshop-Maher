# Module 09: Backend testing and quality gates

**Guided effort:** 10 hours  
**Required branch:** `learning/09-backend-quality`  
**Phase:** Backend

## Objectives

- Choose backend unit, API integration, PostgreSQL/migration, and manual exploratory tests based on risk.
- Build isolated fixtures and dependency overrides without relying on developer data.
- Use branch-aware coverage as a diagnostic guardrail, not a target by itself.
- Run Ruff, Mypy, Pytest, migration checks, and mutation drills as one quality gate.

## Prerequisites

- Modules 05–08 implemented.
- Ability to run Pytest and understand fixtures.

## Concepts and context

A test is valuable when it fails for a plausible regression and explains the broken contract. Unit tests protect pure rules quickly; API tests protect routing/auth/schema/service integration; PostgreSQL tests protect engine-specific behavior; migration checks protect reproducibility. End-to-end tests come later and should not replace lower-level diagnosis.

Fixtures must isolate state. Tests that pass only in an order, share a developer database, or use sleeps hide risk. Coverage points to unexecuted code but does not prove assertions, authorization completeness, or production behavior.

## Step-by-step lab

### 1. Build a test risk map

For each backend risk, choose the lowest useful layer:

- slug normalization;
- task transition;
- project creation transaction;
- request validation;
- duplicate registration;
- cross-user authorization;
- migration from empty PostgreSQL;
- PostgreSQL constraint behavior;
- production startup/readiness.

Explain why not every risk belongs in TestClient.

### 2. Create isolated fixtures

Use an engine/session per test or controlled transaction rollback. Override `get_db` and clear overrides after tests. Generate unique users/data. Never read `.env` production values or call the local development database accidentally.

Understand the baseline's SQLite speed tradeoff. Add a CI PostgreSQL service and migration step. Add at least one PostgreSQL-specific test when using behavior SQLite cannot prove.

### 3. Strengthen unit tests

Test the complete transition table, slug edge cases, and any extracted authorization/policy functions. Use parameterization for a table of behavior, not to hide scenario meaning.

### 4. Strengthen API tests

Organize by capability and cover:

- status/health;
- registration/login/me;
- project create/list/read/update/delete;
- public/private project;
- task create/list/update/delete;
- validation/conflict/not-found;
- two-user authorization.

Assert status and important response/side-effect fields. Avoid asserting an entire volatile JSON object when only part is contractually important.

### 5. Validate migrations against PostgreSQL

Use the CI service or local Compose database:

```bash
cd backend
alembic upgrade head
alembic current
alembic check
```

For the latest learner migration, exercise downgrade/re-upgrade in disposable state. Start the application after upgrade.

### 6. Run static quality

```bash
ruff check .
ruff format --check .
mypy app
pytest
```

Review warnings and suppress only a verified false positive at the narrowest location with explanation.

### 7. Interpret coverage

Inspect branch misses:

```bash
pytest --cov=app --cov-branch --cov-report=term-missing
```

For each important miss, add a behavior test or document why it is unreachable/defensive glue. Do not add empty assertions or remove branches solely to increase the number.

### 8. Mutation drill

Make three temporary mutations:

1. allow `backlog → done`;
2. remove project access check from task update;
3. change project-create status from `201` to `200`.

Run the narrow tests and record which fail. Restore changes. Any mutation that survives reveals a missing or weak test; add one.

### 9. Define backend quality command

Confirm `make backend-quality` runs lint, type check, and tests in a reproducible container. Document host equivalents for fast iteration, but the container command is the shared gate.

## Validation checklist

- [ ] Risk map assigns tests to justified layers.
- [ ] Tests do not depend on developer data or order.
- [ ] Two-user authorization and invalid transition are protected.
- [ ] Alembic builds an empty PostgreSQL database and reports no drift.
- [ ] Ruff, Mypy, and Pytest pass.
- [ ] Coverage misses are reviewed rather than gamed.
- [ ] All three deliberate mutations are detected after test improvements.

## Independent challenge

Add a PostgreSQL-backed test that proves a database constraint or transaction behavior not guaranteed by SQLite. Explain why the extra test cost is justified and keep it isolated from fast unit tests.

## Common failure modes

- Using one end-to-end test to cover every backend rule.
- Reusing a session/database across tests without isolation.
- Asserting only status 200 and ignoring response/side effects.
- Raising coverage with tests that cannot fail meaningfully.
- Disabling Mypy/Ruff rules broadly to finish a PR.

## Evidence to submit

- Test risk map.
- Quality command output with coverage summary.
- Migration/PostgreSQL validation output.
- Mutation table showing expected failing tests.
- One weak test improved through review.

## Commit checkpoint

```text
test(api): enforce backend behavior and quality gates
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [testing-strategy.md](../docs/testing-strategy.md)
- [https://fastapi.tiangolo.com/tutorial/testing/](https://fastapi.tiangolo.com/tutorial/testing/)
- [https://docs.pytest.org/en/stable/](https://docs.pytest.org/en/stable/)
- [https://coverage.readthedocs.io/](https://coverage.readthedocs.io/)
- [autogenerate.html](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
