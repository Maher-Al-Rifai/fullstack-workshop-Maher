# Module 06 — PostgreSQL, SQLAlchemy & Alembic Demo Guide
## What to open and show the lead

---

## 1. Open the models folder and walk through each file

Navigate to `backend/app/models/`. Open them in this order:

### `base.py`

**What to point out:**
```python
class Base(DeclarativeBase): pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```
"All entities share `TimestampMixin` — the database sets the value with `server_default=func.now()`, not Python. This is timezone-aware and consistent even across multiple app instances."

---

### `user.py`

**What to point out:**
- `email: Mapped[str] = mapped_column(String(255), unique=True, index=True)`
- "We use `Mapped[type]` — modern SQLAlchemy 2 typed mappings. The ORM knows the Python type from the annotation."
- `password_hash` — "We store a hash, never the plaintext password. That comes in Module 08."

---

### `project.py`

**What to point out:**
- `slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)` — "URL-safe identifier, enforced unique at DB level"
- `owner_id FK NOT NULL` — "Every project must have an owner — no orphaned projects"
- `members` relationship with `cascade="all, delete-orphan"` — "Deleting a project cascades to memberships and tasks automatically"

---

### `project_member.py`

**What to point out:**
```python
__tablename__ = "project_members"
project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
role: Mapped[str] = mapped_column(String(50))
```
"Composite primary key `(project_id, user_id)` — PostgreSQL rejects duplicate membership at the database level, not just in Python."

---

### `task.py`

**What to point out:**
```python
class TaskStatus(str, enum.Enum):
    backlog = "backlog"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"
```
- "Python `str enum` — values are plain strings so JSON serialization works without extra steps"
- `__table_args__ = (Index("ix_tasks_project_status", "project_id", "status"),)` — "Composite index for the most common query: all tasks with a given status in a project"

---

### `comment.py`

**What to point out:**
- No `updated_at` field
- "Comments are immutable — once posted they cannot be edited. This is a business rule enforced by the schema."

---

## 2. Open `backend/alembic.ini`

**What to point out — find this line:**
```ini
sqlalchemy.url = postgresql+psycopg://placeholder/placeholder
```
"No real credential in version control. The actual URL is loaded from the environment at runtime inside `migrations/env.py`."

---

## 3. Open `backend/migrations/env.py`

**What to point out:**
```python
from app.core.config import get_settings
import app.models                         # registers all tables with Base.metadata
from app.models.base import Base

config.set_main_option("sqlalchemy.url", get_settings().database_url)
target_metadata = Base.metadata
```
"The `import app.models` line is critical. Alembic autogenerate compares `Base.metadata` against the live database. If a model is never imported, its table is invisible — autogenerate produces an empty migration."

---

## 4. Open both migration files

**Files to open:**
- `backend/migrations/versions/3dd58abcb2b8_initial_workboard_schema.py`
- `backend/migrations/versions/aebbaa09a1bc_add_task_estimate_hours.py`

**On the initial migration — point out:**
- `revision`, `down_revision = None` → "This is the root of the chain"
- The `upgrade()` function creates all 5 tables
- At the bottom, manually added:
  ```python
  op.execute("DROP TYPE IF EXISTS task_status")
  op.execute("DROP TYPE IF EXISTS task_priority")
  ```
  "Alembic autogenerate does NOT drop PostgreSQL enum types on downgrade — known gap. We added these manually after reviewing the generated migration."

**On the second migration — point out:**
```python
op.add_column("tasks", sa.Column("estimate_hours", sa.Integer(), nullable=True))
```
"Added as nullable — adding a `NOT NULL` column to a table with existing rows requires a default or a backfill. Nullable first is the safe staged approach."

---

## 5. Run the migration lifecycle live in the terminal

Show these commands one by one:

```powershell
# Show current state
docker compose run --rm backend alembic current

# Show full history
docker compose run --rm backend alembic history --verbose

# Confirm no drift
docker compose run --rm backend alembic check
```

Expected from `alembic check`: `No new upgrade operations detected.`

**What to say:** "This is the difference from `Base.metadata.create_all()`. Alembic knows what version the database is at, can roll forward and backward, and detects if the models have drifted from what was last migrated."

---

## 6. Open `backend/app/services/project_service.py`

**Point to the `create_project` function:**

```python
def create_project(db, owner, data):
    slug = project_repository.unique_slug(db, data.name)
    project = Project(name=data.name, slug=slug, owner_id=owner.id, ...)
    project_repository.add(db, project)
    db.flush()                                                    # gets project.id
    db.add(ProjectMember(project_id=project.id, user_id=owner.id, role="owner"))
    db.commit()                                                   # both rows, atomically
```

**What to say:** "`flush()` sends the INSERT to the database and gets the auto-generated `id` back, but keeps the transaction open. This lets us use `project.id` for the membership foreign key. If anything fails before `commit()`, both inserts are rolled back — no orphaned project without an owner."

---

## 7. Run the tests live

```powershell
docker compose run --rm backend pytest tests/test_project_service.py tests/test_health.py tests/test_status.py tests/test_exceptions.py -v
```

**Expected output:**
```
tests/test_project_service.py::test_create_project_inserts_project_and_membership PASSED
tests/test_project_service.py::test_rollback_prevents_partial_writes PASSED
tests/test_health.py::...  2 PASSED
tests/test_status.py::...  4 PASSED
tests/test_exceptions.py::... 4 PASSED
12 passed
```

**For `test_rollback_prevents_partial_writes` — what to say:**
"After a simulated mid-transaction failure and `db.rollback()`, both the project count and membership count are 0. Neither row persisted — atomicity confirmed."

---

## 8. Show the database schema directly (bonus — if time allows)

```powershell
docker compose exec db psql -U workboard -d workboard -c "\dt"
```

**Expected output — show the 5 tables:**
```
 public | comments        | table | workboard
 public | project_members | table | workboard
 public | projects        | table | workboard
 public | tasks           | table | workboard
 public | users           | table | workboard
```

Then show the task status enum:
```powershell
docker compose exec db psql -U workboard -d workboard -c "\dT+"
```

---

## Questions the lead may ask

**Q: Why use Alembic instead of `Base.metadata.create_all()`?**
A: `create_all` has no version history and silently skips existing tables. Alembic tracks every change, supports rollback to any revision, and detects schema drift with `alembic check`. It is the only production-safe strategy.

**Q: What is the risk of adding a `NOT NULL` column without a default?**
A: PostgreSQL rejects the migration if rows exist in the table — the new column has no value for them. The safe pattern is: add nullable → deploy → backfill the column → add the constraint in a separate later migration.

**Q: Why does `flush()` exist — why not just `commit()` immediately?**
A: After `flush()`, the transaction is still open — you can still roll it back. It also lets you use the auto-generated `id` for relationships before committing. `commit()` makes the data permanent and visible to other connections.

**Q: Why is `(project_id, status)` a composite index instead of two separate indexes?**
A: The query "all tasks with status X in project Y" needs both columns together. A composite index on `(project_id, status)` satisfies this in one index scan. Two separate indexes would require PostgreSQL to scan both and merge the results, which is slower.
