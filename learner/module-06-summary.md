# Module 06 — PostgreSQL, SQLAlchemy & Alembic
## Summary, Evidence & Presentation Guide

---

## What we built (file by file)

```
backend/
├── app/
│   ├── models/
│   │   ├── __init__.py        — exports all models + registers them with metadata
│   │   ├── base.py            — DeclarativeBase + TimestampMixin
│   │   ├── user.py            — User model
│   │   ├── project.py         — Project model
│   │   ├── project_member.py  — ProjectMember association table
│   │   ├── task.py            — Task model with enums + composite index
│   │   └── comment.py         — Comment model
│   └── services/
│       └── project_service.py — atomic create_project_with_owner()
├── migrations/
│   ├── env.py                 — configured: imports models, URL from settings
│   └── versions/
│       ├── 3dd58abcb2b8_initial_workboard_schema.py
│       └── aebbaa09a1bc_add_task_estimate_hours.py
├── alembic.ini                — no credentials committed
├── tests/
│   └── test_project_service.py — atomic insert + rollback tests
└── pyproject.toml             — added alembic==1.16.4
```

---

## Step 1 — Design before coding (ER diagram)

```
USERS ||--o{ PROJECTS         : owns
USERS ||--o{ PROJECT_MEMBERS  : joins
PROJECTS ||--o{ PROJECT_MEMBERS : includes
PROJECTS ||--o{ TASKS         : contains
USERS ||--o{ TASKS            : assigned
TASKS ||--o{ COMMENTS         : has
USERS ||--o{ COMMENTS         : writes
```

**Rule placement:**

| Rule | Where enforced |
|---|---|
| Unique user email | PostgreSQL `UNIQUE` + Pydantic format validation |
| Unique project slug | PostgreSQL `UNIQUE` index |
| Project must have an owner | PostgreSQL `NOT NULL` FK on `owner_id` |
| One membership per (project, user) | PostgreSQL composite PK `(project_id, user_id)` |
| Task status/priority values | PostgreSQL `ENUM` type + Python `str enum` |
| Optional assignee | Nullable FK (`ondelete="SET NULL"`) |
| Timestamps | `server_default=func.now()` — database sets the value |
| Referential integrity on delete | `ondelete="CASCADE"` on child FKs |

---

## Step 2 — SQLAlchemy models (SQLAlchemy 2 typed mappings)

All models use `Mapped[type]` and `mapped_column()` — the modern SQLAlchemy 2 style.

**TimestampMixin** — shared by all entities except Comment and ProjectMember:
```python
created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

**Key design choices:**

| Model | Notable constraint |
|---|---|
| `User` | `email` — `unique=True`, indexed |
| `Project` | `slug` — `unique=True`, indexed; `owner_id` FK NOT NULL |
| `ProjectMember` | Composite PK `(project_id, user_id)` — prevents duplicate membership |
| `Task` | `status` / `priority` PostgreSQL ENUMs; composite index `(project_id, status)` |
| `Comment` | No `updated_at` — comments are immutable once posted |

**Why the `(project_id, status)` composite index?**
The most common query is "give me all in-progress tasks for this project." Without an index, PostgreSQL scans every task row. With the compound index, it goes directly to matching rows.

---

## Step 3 — Alembic configuration

**alembic.ini** — no database credential:
```ini
# URL is loaded from environment in migrations/env.py — no credential committed
sqlalchemy.url = postgresql+psycopg://placeholder/placeholder
```

**migrations/env.py** — key additions:
```python
from app.core.config import get_settings
import app.models  # registers all tables with Base.metadata
from app.models.base import Base

config.set_main_option("sqlalchemy.url", get_settings().database_url)
target_metadata = Base.metadata
```

**Why import `app.models` in env.py?**
Alembic autogenerate compares `Base.metadata` (what the code says) against the
live database. If a model is never imported, its table is invisible to metadata
and autogenerate produces an empty migration. Every model must be imported before
`target_metadata` is set.

---

## Step 4 — Initial migration lifecycle

```
alembic revision --autogenerate -m "initial workboard schema"  → created 3dd58abcb2b8
alembic upgrade head       → created: users, projects, project_members, tasks, comments
alembic current            → 3dd58abcb2b8 (head)
alembic history --verbose  → shows full revision chain
alembic downgrade base     → dropped all tables + enum types
alembic upgrade head       → recreated everything cleanly
alembic check              → "No new upgrade operations detected" ✓
```

**Autogenerate detected:**
- 5 tables: `users`, `projects`, `project_members`, `tasks`, `comments`
- 3 indexes: `ix_users_email`, `ix_projects_slug`, `ix_tasks_project_status`
- 2 PostgreSQL enum types: `task_status`, `task_priority`

**Manual review fix applied:**
Autogenerate's downgrade did NOT drop the PostgreSQL enum types (known gap).
Added explicit drop to the downgrade function:
```python
op.execute("DROP TYPE IF EXISTS task_status")
op.execute("DROP TYPE IF EXISTS task_priority")
```

**Why not use `Base.metadata.create_all()` for deployment?**
`create_all` has no version history, no rollback, no incremental change tracking,
and silently skips existing tables. It is suitable only for tests. Migrations are
the production deployment strategy.

---

## Step 5 — Incremental migration

Added `estimate_hours: Mapped[int | None]` to the `Task` model — nullable so
existing rows are not affected. Safe staged approach:

1. Added as `nullable=True` (no `NOT NULL` with no default strategy)
2. Generated new revision: `aebbaa09a1bc_add_task_estimate_hours.py`
3. Lifecycle: `upgrade head` → `downgrade -1` → `upgrade head` → `check` ✓

**Why add it nullable first?**
Adding a `NOT NULL` column to a table with existing rows requires either a default
value or a data backfill. Without one, the migration fails or corrupts data.
Safe pattern: add nullable → deploy → backfill → add constraint in a later revision.

---

## Step 6 — Atomic transaction

**Service function** (`services/project_service.py`):
```python
def create_project_with_owner(db, *, name, slug, owner, ...):
    project = Project(name=name, slug=slug, owner_id=owner.id, ...)
    db.add(project)
    db.flush()   # assigns project.id — still inside the transaction

    membership = ProjectMember(project_id=project.id, user_id=owner.id, role="owner")
    db.add(membership)
    db.commit()  # both rows committed atomically here
```

**Why `flush()` before `commit()`?**
`flush()` sends the INSERT to the database and gets the auto-generated `id` back,
but keeps the transaction open. This lets us use `project.id` for the membership
foreign key before committing anything. If anything fails before `commit()`, the
whole transaction rolls back.

**Rollback test result:**
```
test_rollback_prevents_partial_writes PASSED
```
After a simulated mid-transaction failure and `db.rollback()`:
- `Project` count = 0
- `ProjectMember` count = 0

Both rows were prevented from persisting — atomicity confirmed.

---

## Step 8 — SQL echo / generated SQL

With `echo=True` on the engine, SQLAlchemy prints every statement. Key things visible:

- `BEGIN` before any write
- `INSERT INTO users ...` on `db.add() + db.flush()`
- `INSERT INTO project_members ...`
- `COMMIT` — both rows land in the database together
- On rollback: `ROLLBACK` — database discards both inserts

---

## Test results

```
12 passed — ruff lint: All checks passed — ruff format: 29 files already formatted
```

| Test file | Tests | What is verified |
|---|---|---|
| `test_project_service.py` | 2 | atomic insert of project+membership; rollback prevents partial writes |
| `test_exceptions.py` | 4 | domain error → HTTP status code mapping |
| `test_health.py` | 2 | liveness + combined health |
| `test_status.py` | 4 | status shape, secret leak, 422 validation |

---

## Key concepts to present

### 1. ORM layer responsibilities

| Layer | Responsibility |
|---|---|
| Pydantic schema | Shape, required fields, type parsing, length limits |
| Service | Business rules: project access, workflow transitions, owner-only actions |
| Repository | Query mechanics: add, flush, query, filter |
| Database | PK/FK constraints, unique constraints, NOT NULL, referential integrity |

### 2. Why migrations instead of `create_all`

| `create_all` | Alembic migrations |
|---|---|
| No history | Full version history |
| No rollback | Downgrade to any revision |
| Skips existing tables silently | Detects drift with `alembic check` |
| Cannot modify existing columns | Incremental schema evolution |

### 3. Transaction atomicity
A transaction is all-or-nothing. `flush()` sends SQL to the DB but keeps the
transaction open. `commit()` makes it permanent. `rollback()` undoes everything
since the last commit. Without atomicity, a crash between the project insert and
membership insert would leave an orphaned project with no owner.

### 4. autoflush and expire_on_commit
- `autoflush=True` (default): ORM flushes pending changes before any query in the same session — prevents reading stale data
- `expire_on_commit=True` (default): after commit, all loaded objects are "expired" — next access re-reads from DB

---

## Validation checklist (completed)

- [x] ER model and implemented relationships agree
- [x] Empty PostgreSQL reaches head using migrations only (`alembic upgrade head`)
- [x] Incremental revision (`estimate_hours`) downgraded and reapplied safely
- [x] `alembic check` reports "No new upgrade operations detected"
- [x] Project + owner membership atomic under injected failure (rollback test passes)
- [x] Layer responsibilities documented (Pydantic / service / repository / database)
- [x] No credential in `alembic.ini` or migration files

---

## Commit message

```
feat(db): model workboard data and add reviewed migrations
```
