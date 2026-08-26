# Module 09 — Demo Guide: Backend Testing and Quality Gates

This guide walks through everything you can show live to demonstrate Module 09 mastery.

---

## 1. Show the test folder layout

```powershell
# From project root:
Get-ChildItem backend/tests -Recurse -Filter "*.py" | Select-Object FullName
```

Point out:
- `unit/` — pure Python, no database
- `integration/` — HTTP round-trips over SQLite
- Top-level test files — integration tests for auth, projects, tasks, exceptions

---

## 2. Run the full test suite

```powershell
docker compose run --rm backend pytest -v --no-header
```

Expected output: **97 passed**

Show that tests are organized in layers:
- `tests/unit/test_transitions.py` — state machine rules
- `tests/unit/test_slug.py` — slug generation edge cases
- `tests/integration/test_coverage_gaps.py` — HTTP + DB scenarios

---

## 3. Explain a parameterized test (test_transitions.py)

Open `backend/tests/unit/test_transitions.py` and show:

```python
_ALLOWED = [
    ("backlog", "in_progress"),
    ("backlog", "cancelled"),
    ("in_progress", "done"),
    ("in_progress", "cancelled"),
]

@pytest.mark.parametrize("from_status,to_status", _ALLOWED)
def test_allowed_transition_passes(from_status, to_status):
    apply_transition(TaskStatus[from_status], TaskStatus[to_status])
```

Key teaching point: **one test function covers N cases**. When you add a new transition rule, you add one line to the table — not a new function.

---

## 4. Run coverage report

```powershell
docker compose run --rm backend pytest --cov=app --cov-branch --cov-report=term-missing
```

Walk through the output:
- Total: ~97%
- Show the files with misses and explain why each is acceptable (see summary)
- Point to `fail_under = 90` in `pyproject.toml` — this enforces the gate

---

## 5. Run mypy type checking

```powershell
docker compose run --rm backend mypy app
```

Expected output: `Success: no issues found in 38 source files`

Show the `pyproject.toml` config:
```toml
[tool.mypy]
python_version = "3.13"
ignore_missing_imports = true
plugins = ["sqlalchemy.ext.mypy.plugin"]

[[tool.mypy.overrides]]
module = "app.models.*"
disable_error_code = ["name-defined"]
```

Explain: the `name-defined` override is required because SQLAlchemy string references in `relationship("ModelName")` are false positives — the plugin resolves them at runtime.

---

## 6. Run Alembic migration check

```powershell
docker compose run --rm backend alembic check
```

Expected output: `No new upgrade operations detected.`

Explain: if you change a SQLAlchemy model without writing a migration, this fails. It's a mandatory CI gate — a missed migration is a production outage.

To show a failure, add a column to a model temporarily and re-run:
```python
# In any model, temporarily add:
new_column = Column(String, nullable=True)
```
Then run `alembic check` — it will warn about the unmapped change.
Remove the column after showing.

---

## 7. Run the full quality gate

```powershell
make backend-quality
```

This runs all 4 checks in sequence inside a single container:
1. `ruff check .` — lint
2. `ruff format --check .` — formatting
3. `mypy app` — type checking
4. `pytest --cov=app --cov-branch --cov-report=term-missing` — tests + coverage

Expected output: all four steps succeed, final line is `97 passed`.

---

## 8. Mutation drill demo

Show that your tests actually *assert* on the right things, not just execute code.

### Mutation 1 — Allow illegal transition

```powershell
docker compose run --rm backend sh -c "
  sed -i 's/TaskStatus.backlog: {TaskStatus.in_progress, TaskStatus.cancelled}/TaskStatus.backlog: {TaskStatus.in_progress, TaskStatus.cancelled, TaskStatus.done}/' app/services/task_transitions.py &&
  pytest tests/unit/test_transitions.py tests/test_tasks.py -v --no-header -q 2>&1 | grep -E 'PASSED|FAILED'
"
```

Expected: 3 tests **FAIL** — the suite caught the broken rule. Container is ephemeral; host file unchanged.

### Mutation 3 — Wrong HTTP status code

```powershell
docker compose run --rm backend sh -c "
  sed -i 's/status_code=201/status_code=200/' app/api/routes/projects.py &&
  pytest tests/test_projects.py::test_create_project_returns_201 -v 2>&1 | grep -E 'PASSED|FAILED'
"
```

Expected: `FAILED` — the test explicitly checks for 201. Container is ephemeral; host file unchanged.

---

## 9. Show a coverage gap test (integration layer)

Open `backend/tests/integration/test_coverage_gaps.py` and walk through a few:

```python
def test_create_project_with_empty_name_returns_422(auth_client):
    r = auth_client.post("/api/v1/projects", json={"name": ""})
    assert r.status_code == 422

def test_inactive_user_rejected_by_get_current_user(client, db_session):
    # create user, deactivate, try to use token
    ...
    assert r.status_code == 401
```

Key point: these tests cover paths that the happy-path CRUD tests don't reach.

---

## Summary checklist for the demo

- [ ] 97 tests, all green
- [ ] Coverage report showing ~97% with justified misses
- [ ] `mypy app` shows 0 errors
- [ ] `alembic check` shows no upgrade operations
- [ ] `make backend-quality` passes end-to-end
- [ ] Mutation 1 (transition rule) caught by 3 tests
- [ ] Mutation 3 (status code) caught by 1 test
- [ ] Can explain unit vs integration layer choice for any given test
