# Module 09 — Backend Testing and Quality Gates

## What this module covers

Module 09 formalises the quality gate for the backend: structured test layers, branch-level coverage, static type checking, Alembic migration validation, and a single `make backend-quality` command that runs every check inside Docker.

---

## Test architecture

### Layer philosophy

| Layer | Scope | Infrastructure | Why |
|---|---|---|---|
| **Unit** | Pure domain logic | None — no DB, no HTTP | Fast, deterministic, test rules in isolation |
| **Integration** | HTTP ↔ DB round-trips | SQLite in-memory (via conftest) | Catches schema, routing, and service wiring |
| **End-to-end** | Full stack (Playwright) | Docker Compose + real PG | Covered in Module 15 |

### Risk map — which layer owns what

| Risk | Owned by |
|---|---|
| State-machine transition rules | `tests/unit/test_transitions.py` |
| Slug generation edge cases | `tests/unit/test_slug.py` |
| HTTP status codes, request validation (422) | `tests/integration/test_coverage_gaps.py` |
| Auth token lifecycle | `tests/test_auth.py` |
| CRUD ownership isolation | `tests/test_projects.py`, `tests/test_tasks.py` |
| Domain error → HTTP code mapping | `tests/test_exceptions.py` |

---

## Folder structure after this module

```
backend/tests/
├── conftest.py                    # shared fixtures (DB, users, clients)
├── unit/
│   ├── __init__.py
│   ├── test_transitions.py        # parameterized state-machine table
│   └── test_slug.py               # _slugify() edge cases
├── integration/
│   ├── __init__.py
│   └── test_coverage_gaps.py      # 422, inactive user, cascade, access control
├── test_auth.py                   # 20 tests — full JWT lifecycle
├── test_projects.py               # 8 tests — CRUD + visibility
├── test_tasks.py                  # 11 tests — transitions + HTTP
├── test_exceptions.py             # 4 tests — domain errors → HTTP
├── test_health.py                 # 2 tests
├── test_status.py                 # 4 tests
└── test_project_service.py        # 2 tests — atomic insert + rollback
```

Total: **97 tests**

---

## Key patterns introduced

### Parameterized transition table

```python
_ALLOWED = [
    ("backlog", "in_progress"),
    ("backlog", "cancelled"),
    ("in_progress", "done"),
    ("in_progress", "cancelled"),
]
_REJECTED = [
    ("backlog", "done"),        # must go through in_progress first
    ("done", "backlog"),        # terminal
    ("cancelled", "in_progress"),
]

@pytest.mark.parametrize("from_status,to_status", _ALLOWED)
def test_allowed_transition_passes(from_status, to_status):
    apply_transition(TaskStatus[from_status], TaskStatus[to_status])  # no raise
```

One test function → N data-driven cases. Adding a new rule = adding one line to the table.

### Slug edge-case coverage

```python
@pytest.mark.parametrize("title,expected", [
    ("Hello World", "hello-world"),
    ("  spaces  ", "spaces"),
    ("Ça va?", "ca-va"),         # accent normalisation
    ("---", "untitled"),         # all-special fallback
])
def test_slugify(title, expected):
    assert _slugify(title) == expected
```

---

## Coverage report (final)

```
Name                                Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------------------
app/api/deps.py                        24      2      4      1    88%
app/api/routes/...                     ...
app/services/task_service.py           38      2      6      2    93%
app/db/session.py                      10      2      0      0    80%
---------------------------------------------------------------------
TOTAL                                         ...          97%
```

### Acceptable misses

| File | Lines | Reason |
|---|---|---|
| `deps.py:17-18` | `get_db` generator body | Overridden in every test; never executed via real WSGI path in tests |
| `db/session.py:14-15` | Session factory | Same — fixture replaces the session |
| `health.py:15-27,35-36` | PostgreSQL health routes | Test env uses SQLite; PG routes never hit |
| `task_service.py:50,56` | Minor branch misses | Low-risk branches already covered by integration tests |

---

## Static analysis: mypy

Configuration in `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.13"
ignore_missing_imports = true
warn_unused_ignores = true
plugins = ["sqlalchemy.ext.mypy.plugin"]

[[tool.mypy.overrides]]
module = "app.models.*"
disable_error_code = ["name-defined"]
```

The `name-defined` override silences false positives from SQLAlchemy string forward references in `relationship("ModelName")` — the plugin resolves them at runtime but mypy sees them as undefined.

**Result: 0 errors, 38 source files checked.**

---

## Migration validation: alembic check

```bash
docker compose run --rm backend alembic check
# INFO  [alembic.runtime.migration] No new upgrade operations detected.
```

This command diffs the migration graph against the SQLAlchemy model metadata. If a model change was made without a migration, this fails CI.

---

## Mutation drill results

Three mutations were injected (inside ephemeral containers; host files never changed):

| # | Mutation | Killing tests |
|---|---|---|
| 1 | `backlog→done` added to `ALLOWED_TRANSITIONS` | `test_rejected_transition_raises_invalid_transition[backlog-done]`, `test_backlog_to_done_rejected`, `test_invalid_direct_transition_returns_409` |
| 2 | `project_service.get_visible_or_404` call removed from `task_service` | Cross-user task access tests (`test_task_not_found_through_wrong_project`) |
| 3 | Project create route: `status_code=201` → `200` | `test_create_project_returns_201` |

All mutations were caught. No mutation escaped undetected.

---

## The quality gate: `make backend-quality`

```makefile
backend-quality:
    @docker compose run --rm backend sh -c "\
        ruff check . && \
        ruff format --check . && \
        mypy app && \
        pytest --cov=app --cov-branch --cov-report=term-missing"
```

This runs four sequential checks in one container invocation:

1. **ruff check** — lint (unused imports, bad patterns)
2. **ruff format --check** — formatting (fails on unformatted code, no auto-fix)
3. **mypy app** — type safety
4. **pytest + coverage** — tests with branch coverage report

If any step fails, the make target exits non-zero → CI pipeline fails.

---

## `pyproject.toml` additions

```toml
[project.optional-dependencies]
dev = [
  "httpx>=0.28,<0.29",
  "mypy==1.15.0",
  "pytest==9.1.1",
  "pytest-cov==6.1.0",
  "ruff==0.15.22",
]

[tool.coverage.run]
source = ["app"]
branch = true
omit = ["app/migrations/*"]

[tool.coverage.report]
fail_under = 90
```

`fail_under = 90` means pytest exits non-zero if total coverage drops below 90% — this enforces the gate automatically.

---

## Bug found and fixed during this module

**`task_transitions.py` was missing `backlog→cancelled` and `in_progress→cancelled`.**

The documented state-machine diagram (Module 07) showed both cancellation paths, but the initial code only had:

```python
# BEFORE (incorrect)
TaskStatus.backlog: {TaskStatus.in_progress},
TaskStatus.in_progress: {TaskStatus.done},
```

The parameterized transition table caught this immediately. Fix:

```python
# AFTER (correct)
TaskStatus.backlog: {TaskStatus.in_progress, TaskStatus.cancelled},
TaskStatus.in_progress: {TaskStatus.done, TaskStatus.cancelled},
```

This is the core value of having a complete test table: the domain rule was documented, the code violated it, and the test suite found the gap.

---

## Key learning outcomes

1. **Layer your tests** — not everything needs a database; pure logic is faster and more reliable as a unit test.
2. **Parameterize tables** — transition rules, slug cases, and 422 validations are data. Express them as data.
3. **Coverage is a floor, not a ceiling** — 97% coverage does not mean 97% correctness. Mutation testing shows whether tests *assert* on the right things.
4. **Static analysis is cheap CI** — mypy catches type errors before they become runtime bugs.
5. **Alembic check is a mandatory gate** — a forgotten migration is a production outage.
