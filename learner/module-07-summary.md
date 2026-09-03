# Module 07 — Backend Domain Architecture and CRUD

## What this module covers

Building the real business logic layer of the API: repositories, services, and HTTP routes for the **Projects** and **Tasks** domains. The module enforces clean separation between HTTP concerns (routes), business rules (services), and query mechanics (repositories), and introduces a state-machine guard for task status transitions.

---

## Architecture layers added

```
HTTP request
     │
     ▼
routes/         ← FastAPI handlers, request/response schemas, HTTP verbs & status codes
services/       ← business rules, authorization checks, slug generation, transition guard
repositories/   ← raw SQLAlchemy queries, no business logic
models/         ← SQLAlchemy ORM classes (existed from Module 06)
schemas/        ← Pydantic I/O contracts (new this module)
```

---

## Files created / modified

### Schemas (`app/schemas/`)

| File | Purpose |
|---|---|
| `project.py` | `ProjectCreate`, `ProjectUpdate`, `ProjectRead`, `PublicProjectRead` |
| `task.py` | `TaskCreate`, `TaskUpdate`, `TaskRead` |
| `user.py` | `UserRead` (used by auth stub) |

All `Read` schemas use `model_config = ConfigDict(from_attributes=True)` so SQLAlchemy ORM objects serialize directly.

### Repositories (`app/repositories/`)

| File | Key functions |
|---|---|
| `project_repository.py` | `slug_exists`, `unique_slug`, `get_by_id`, `get_visible_to_user`, `get_public_by_slug`, `add`, `delete` |
| `task_repository.py` | `get_by_id_and_project`, `list_for_project`, `add`, `delete` |

Repositories **only query**. They never enforce authorization or business rules.

### Services (`app/services/`)

| File | Key responsibilities |
|---|---|
| `project_service.py` | Slug generation with collision suffix counter; atomic project + owner-membership insert; `get_visible_or_404` (hides existence for inaccessible private projects); ownership guard on update/delete |
| `task_transitions.py` | `ALLOWED_TRANSITIONS` dict; `validate_transition()` raises `InvalidTransitionError` (→ 409) |
| `task_service.py` | All task CRUD; verifies project visibility before touching tasks; calls `validate_transition` on status change |

### Dependencies (`app/api/deps.py`)

```python
async def get_current_user(db: Session = Depends(get_db)) -> User:
    raise UnauthorizedError("Authentication not implemented — override in tests")
```

Placeholder that enforces the pattern: all protected routes require auth, but tests override it per-fixture.

### Routes (`app/api/routes/`)

| Route file | Endpoints |
|---|---|
| `projects.py` | `GET /public/{slug}` (no auth), `GET /projects`, `POST /projects` (201), `GET /projects/{id}`, `PATCH /projects/{id}`, `DELETE /projects/{id}` (204) |
| `tasks.py` | `GET /projects/{project_id}/tasks`, `POST /projects/{project_id}/tasks` (201), `PATCH /projects/{project_id}/tasks/{task_id}`, `DELETE /projects/{project_id}/tasks/{task_id}` (204) |

---

## Task state machine

```
backlog ──► in_progress ──► done
                │
                └──► cancelled
```

Any other transition (e.g., `backlog → done`, `done → backlog`) raises `InvalidTransitionError` which the exception handler maps to **409 Conflict**.

---

## Slug generation algorithm

```
base_slug = name.lower().replace(" ", "-")        # "My Project" → "my-project"
if not slug_exists(db, base_slug):
    return base_slug
counter = 2
while slug_exists(db, f"{base_slug}-{counter}"):
    counter += 1
return f"{base_slug}-{counter}"                   # "my-project-2"
```

---

## Test design patterns learned

### Transaction-per-test rollback (conftest.py)

```python
@pytest.fixture(autouse=True)
def db_session():
    connection = _engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()      # ← every test starts clean, no truncation needed
    connection.close()
```

### Dependency override for auth

```python
@pytest.fixture
def client(db_session, owner):
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: owner
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Multi-user tests — override inline, not via a second fixture

Both `client` and `other_client` fixtures write to the same global `app.dependency_overrides`, so the last fixture to run wins and corrupts the first user's identity. The correct pattern is to change the override inline inside the test:

```python
def test_private_project_not_visible_to_other_user(client, other_user):
    r = client.post("/api/v1/projects", json={"name": "Secret", "is_public": False})
    project_id = r.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: other_user  # switch user
    response = client.get(f"/api/v1/projects/{project_id}")

    assert response.status_code == 404
```

---

## Test results

```
31 passed in 1.29s
```

| Test file | Count | What it covers |
|---|---|---|
| `test_projects.py` | 8 | Create, list, slug collision, private 404, public slug, update, 403 on hijack, delete |
| `test_tasks.py` | 11 | 5 pure transition unit tests + 6 HTTP integration tests |
| `test_exceptions.py` | 4 | Domain errors → correct HTTP codes |
| `test_health.py` | 2 | Live / ready probes |
| `test_status.py` | 4 | Status shape, no secret leak, ping 201/422 |
| `test_project_service.py` | 2 | Atomic insert + rollback |

---

## Quality checks

```
ruff check .        → 0 errors (1 unused import auto-fixed)
ruff format --check → all files formatted
```

---

## Key concepts to remember

| Concept | Detail |
|---|---|
| **Repository pattern** | Functions return ORM objects or raise; never raise HTTP errors |
| **Service layer** | Owns authorization checks and business invariants |
| **Privacy leak prevention** | Return 404 (not 403) for inaccessible private resources so existence isn't revealed |
| **Atomic operations** | `db.add(project); db.add(membership); db.flush()` — both rows or neither |
| **State machine guard** | `validate_transition()` called before any status update; `InvalidTransitionError → 409` |
| **SQLite for tests** | In-memory, no migrations needed; `Base.metadata.create_all(_engine)` at module load |
| **Dependency override scope** | `app.dependency_overrides` is a global dict — conflicts arise when two fixtures override the same key simultaneously |
