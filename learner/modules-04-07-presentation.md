# Modules 04 → 07 — Presentation Summary

---

## Module 04 — Docker & Container Fundamentals

### Core idea
An **image** is a frozen blueprint. A **container** is a running process built from that image. The filesystem resets when the container stops; named volumes persist separately.

### What we proved

**Multi-stage Dockerfiles** — both backend and frontend use stages:
- `dependencies / build` stage compiles and installs everything
- `production` stage ships only the final output — no build tools, no dev packages

**Non-root runtime** — both images run as user `app` (uid 999), not root:
```
docker run --rm --entrypoint whoami workboard-backend:module04  →  app
```

**Layer cache order matters:**
```dockerfile
COPY pyproject.toml ./    # slow-changing → stays cached
RUN pip install .         # only re-runs when deps change
COPY . .                  # fast-changing → invalidates nothing above
```
Wrong order means a full `pip install` on every code change.

**`.dockerignore` is a security control** — `.env`, `.git`, and `node_modules` must be excluded so secrets never enter an image layer.

### Key distinctions

| | `EXPOSE` | `ports:` in compose | Compose service DNS |
|---|---|---|---|
| What it does | Documentation only | Maps host → container | Containers talk by name |
| Who sees it | Humans | Your browser / curl | Other containers only |

`docker compose down` keeps volumes. `docker compose down -v` **deletes** them.

---

## Module 05 — FastAPI Application Foundation

### Core idea
The application is split into three tiers of routing: **unversioned health probes**, **versioned API routes**, and **typed settings** that classify every config value as public, operational, or secret.

### What we built

```
app/
├── api/routes/health.py   — /health/live (no DB), /health/ready (DB check), /health
├── api/routes/status.py   — /api/v1/status, /api/v1/ping
├── core/config.py         — 8 typed settings via pydantic-settings
└── core/exceptions.py     — domain error hierarchy
```

**Liveness vs Readiness — why it matters:**
- `/health/live` — process check only. If it also checked the DB, a temporary DB outage would cause the orchestrator to kill a perfectly healthy app process.
- `/health/ready` — DB check. Fail here if you cannot serve traffic.

**Exception hierarchy → stable HTTP codes:**
```
WorkboardError
├── NotFoundError       → 404   {"code": "not_found"}
├── UnauthorizedError   → 401   {"code": "unauthorized"}
├── ForbiddenError      → 403   {"code": "forbidden"}
└── ConflictError       → 409   {"code": "conflict"}
    └── InvalidTransitionError
```

**Settings classification — what can appear in a response:**

| Type | Examples | In response? |
|---|---|---|
| Public | `app_name`, `version`, `environment` | Yes |
| Operational | `api_prefix`, `cors_origins` | No |
| Secret | `secret_key`, `database_url` | Never |

**Dependency injection pattern:**
```python
def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session   # session closes automatically after response
```

### Test results: 10 passed — SQLite override, no real DB touched

---

## Module 06 — PostgreSQL, SQLAlchemy & Alembic

### Core idea
Models describe the data structure in Python. Alembic translates model changes into versioned SQL migrations that can be applied, rolled back, and audited.

### Data model

```
USERS ──< PROJECTS ──< TASKS ──< COMMENTS
              │
              └──< PROJECT_MEMBERS >── USERS
```

**Key constraint decisions:**

| Rule | Where enforced |
|---|---|
| Unique email | PostgreSQL UNIQUE + Pydantic validation |
| One membership per (project, user) | Composite PK `(project_id, user_id)` |
| Task status/priority values | PostgreSQL ENUM type + Python `str enum` |
| Delete cascade | `ondelete="CASCADE"` on child FKs |
| Timestamps | `server_default=func.now()` — DB sets the value |

**Why the `(project_id, status)` composite index?**
The most common query is "all in-progress tasks for this project." The compound index goes directly to matching rows instead of scanning every task.

### Alembic migration lifecycle
```
alembic revision --autogenerate   → generates SQL diff
alembic upgrade head               → applies to DB
alembic downgrade base             → rolls back all
alembic check                      → confirms no drift
```

**`create_all()` vs migrations:**

| `create_all` | Alembic |
|---|---|
| No version history | Full revision chain |
| No rollback | Downgrade to any point |
| Skips existing tables silently | Detects drift |
| One-shot only | Incremental schema evolution |

### Atomic transaction
```python
db.add(project)
db.flush()       # gets project.id — transaction still open
db.add(ProjectMember(project_id=project.id, ...))
db.commit()      # both rows land together, or neither does
```
`flush()` sends SQL to get the auto-generated ID without committing. Any failure before `commit()` rolls back both inserts.

### Test results: 12 passed

---

## Module 07 — Backend Domain Architecture & CRUD

### Core idea
Three clean layers: **routes** handle HTTP, **services** own business rules, **repositories** own queries. Each layer has one responsibility and nothing else.

### Architecture

```
Request → routes/ → services/ → repositories/ → SQLAlchemy models
                         ↓
                    schemas/ (Pydantic I/O)
```

| Layer | Owns | Never does |
|---|---|---|
| Routes | HTTP verbs, status codes, schema binding | Business logic, raw SQL |
| Services | Auth checks, slug gen, transition guard | HTTP concerns, raw SQL |
| Repositories | Query mechanics | Authorization, business rules |

### What was built

**11 API endpoints:**

| Group | Endpoints |
|---|---|
| Projects | `GET /public/{slug}` (no auth), `GET/POST /projects`, `GET/PATCH/DELETE /projects/{id}` |
| Tasks | `GET/POST /projects/{id}/tasks`, `PATCH/DELETE /projects/{id}/tasks/{task_id}` |

**Task state machine:**
```
backlog ──► in_progress ──► done
                │
                └──► cancelled
```
Any skipped step (e.g., `backlog → done`) raises `InvalidTransitionError → 409`.

**Privacy leak prevention:**
Private projects return **404**, not 403, to non-members — so existence is not revealed.

**Slug generation with collision handling:**
```
"My Project" → "my-project"
"My Project" (again) → "my-project-2"
```

### Test patterns

**Transaction-per-test rollback** — every test runs in a transaction that is rolled back at teardown, so no truncation is needed between tests.

**Dependency override for auth:**
```python
app.dependency_overrides[get_current_user] = lambda: owner
```

**Multi-user tests — override inline, not via a second fixture:**
Two fixtures both modifying `app.dependency_overrides` conflict — the last one wins and corrupts both users. Switch the override inline inside the test instead.

### Test results: 31 passed — ruff lint: 0 errors — format: clean

---

## Overall progress

| Module | Topic | Tests | Status |
|---|---|---|---|
| 04 | Docker & Container Fundamentals | — | ✅ |
| 05 | FastAPI Application Foundation | 10 passed | ✅ |
| 06 | PostgreSQL, SQLAlchemy & Alembic | 12 passed | ✅ |
| 07 | Backend Domain Architecture & CRUD | 31 passed | ✅ |

**Stack running:** FastAPI backend · PostgreSQL 17 · Nuxt 3 frontend — all via Docker Compose.

**Next:** Module 08 — Authentication, Authorization & API Security (JWT, password hashing, protected routes).
