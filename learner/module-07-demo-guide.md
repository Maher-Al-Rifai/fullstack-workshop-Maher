# Module 07 — Backend Domain Architecture Demo Guide
## What to open and show the lead

---

## 1. Show the full layer structure

Open `backend/app/` in the VS Code Explorer and point to this tree:

```
app/
├── schemas/
│   ├── project.py       ← Pydantic I/O contracts (external shape only)
│   └── task.py
├── repositories/
│   ├── project_repository.py  ← query mechanics, nothing else
│   └── task_repository.py
├── services/
│   ├── project_service.py     ← business rules + access + transactions
│   ├── task_service.py
│   └── task_transitions.py    ← pure state-machine function
└── api/
    ├── deps.py                ← auth dependency stub
    └── routes/
        ├── projects.py        ← HTTP contract only
        └── tasks.py
```

**What to say:** "Every layer has exactly one reason to change. Routes change when the HTTP contract changes. Services change when business rules change. Repositories change when query mechanics change. They do not mix."

---

## 2. Open `backend/app/schemas/project.py` and `task.py`

**In `project.py` — what to point out:**

```python
class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)   # length validated before DB
    description: str | None = None
    is_public: bool = False

class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    is_public: bool | None = None
```
"`ProjectUpdate` has all fields optional — a PATCH only changes what the caller sends. `ProjectCreate` and `ProjectUpdate` are separate classes because their rules differ."

```python
class PublicProjectRead(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    task_count: int
    done_count: int
```
"The public endpoint returns a different schema — `owner_id`, timestamps, and membership data are not included. Callers get only what they need."

**In `task.py` — what to point out:**
```python
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    priority: TaskPriority = TaskPriority.medium   # sensible default
    estimate_hours: int | None = Field(default=None, ge=1)  # ≥ 1 if provided
```
"Validation happens in the schema before the service or database sees the data. Invalid input returns 422 — no defensive code needed inside the service."

---

## 3. Open `backend/app/repositories/project_repository.py`

**What to point out — the slug uniqueness logic:**

```python
def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "project"

def unique_slug(db: Session, name: str) -> str:
    base = _slugify(name)
    slug = base
    counter = 1
    while slug_exists(db, slug):
        slug = f"{base}-{counter}"
        counter += 1
    return slug
```
"The repository generates URL-safe slugs and handles collisions. 'My Project' → `my-project`. If that exists → `my-project-1`, then `my-project-2`, and so on."

**What to point out — the visibility query:**

```python
def get_visible_to_user(db: Session, user_id: int) -> list[Project]:
    stmt = (
        select(Project)
        .outerjoin(ProjectMember, ProjectMember.project_id == Project.id)
        .where(or_(
            Project.owner_id == user_id,
            ProjectMember.user_id == user_id,
        ))
        .distinct()
    )
```
"One query returns all projects where the user is the owner OR a member. The `DISTINCT` prevents duplicates when a user is both owner and an explicit member."

---

## 4. Open `backend/app/services/project_service.py`

**Point to `create_project`:**

```python
def create_project(db, owner, data):
    slug = project_repository.unique_slug(db, data.name)
    project = Project(name=data.name, slug=slug, owner_id=owner.id, ...)
    project_repository.add(db, project)
    db.flush()                     # gets project.id — transaction still open
    db.add(ProjectMember(project_id=project.id, user_id=owner.id, role="owner"))
    db.commit()                    # both rows land atomically
```
"Project and owner membership are committed in one transaction. If anything fails before `commit()`, neither row persists — no orphaned project without an owner."

**Point to `get_visible_or_404`:**

```python
def get_visible_or_404(db, project_id, user_id):
    project = project_repository.get_by_id(db, project_id)
    if project is None:
        raise NotFoundError("Project not found")
    is_owner = project.owner_id == user_id
    is_member = any(m.user_id == user_id for m in project.members)
    if not (is_owner or is_member or project.is_public):
        raise NotFoundError("Project not found")   # ← 404, not 403
    return project
```
"A non-member gets **404**, not 403. If we returned 403, the caller would know the project exists — that leaks private information."

---

## 5. Open `backend/app/services/task_transitions.py`

**What to point out:**

```python
ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.backlog:     {TaskStatus.in_progress},
    TaskStatus.in_progress: {TaskStatus.done},
    TaskStatus.done:        set(),
    TaskStatus.cancelled:   set(),
}

def validate_transition(current, next_status):
    if next_status == current:
        return          # same-state update is a no-op
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if next_status not in allowed:
        raise InvalidTransitionError(...)
```
"This is a pure function — no database call, no side effects. It takes two enum values and either returns or raises. Because it has no dependencies, it can be unit-tested in complete isolation."

**Draw the state machine on a whiteboard or point to the diagram:**
```
backlog ──► in_progress ──► done
                │
                └──► cancelled
```
"`backlog → done` is rejected. `done → backlog` is rejected. The service calls this before writing to the database."

---

## 6. Open `backend/app/services/task_service.py`

**Point to `update_task` — show the authorization chain:**

```python
def update_task(db, project_id, task_id, user, data):
    task = get_task_or_404(db, project_id, task_id, user)  # 1. verify project visible
                                                            # 2. verify task belongs to project
    if data.status is not None:
        validate_transition(task.status, data.status)      # 3. validate state machine
        task.status = data.status
    ...
    db.commit()                                            # 4. commit once at service boundary
```
"Three checks in order: can the caller see the project? does the task belong to that project? is the status transition allowed? Only then we write. You cannot update a task by ID alone — you must go through its project."

---

## 7. Open `backend/app/api/routes/projects.py`

**What to point out — the route functions are thin:**

```python
@router.post("/projects", response_model=ProjectRead, status_code=201)
def create_project(
    body: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.create_project(db, current_user, body)
```
"The route does three things: declares the HTTP contract (`POST`, schema, `201`), injects dependencies, and calls the service. No business logic here."

**Point to the public endpoint — no auth dependency:**
```python
@router.get("/projects/public/{slug}", response_model=PublicProjectRead)
def get_public_project(slug: str, db: Session = Depends(get_db)):
    return project_service.get_public_by_slug(db, slug)
```
"`get_current_user` is absent — this endpoint intentionally requires no authentication."

---

## 8. Run the tests live

```powershell
docker compose run --rm backend pytest -v
```

**Expected output — point out the two groups in `test_tasks.py`:**
```
tests/test_tasks.py::test_backlog_to_in_progress_allowed PASSED    ← pure unit test
tests/test_tasks.py::test_in_progress_to_done_allowed PASSED       ← pure unit test
tests/test_tasks.py::test_backlog_to_done_rejected PASSED          ← pure unit test
tests/test_tasks.py::test_same_state_is_noop PASSED
tests/test_tasks.py::test_backward_transition_rejected PASSED
tests/test_tasks.py::test_create_task_returns_201_with_backlog_status PASSED  ← HTTP
tests/test_tasks.py::test_list_tasks_for_project PASSED
tests/test_tasks.py::test_valid_two_step_transition PASSED
tests/test_tasks.py::test_invalid_direct_transition_returns_409 PASSED
tests/test_tasks.py::test_task_not_found_through_wrong_project PASSED
tests/test_tasks.py::test_delete_task_returns_204 PASSED

31 passed
```

---

## 9. Show the mutation test (rule mutation proof)

**What to say:** "The module requires proving that tests actually catch a broken rule — not just that they pass."

Temporarily break the transition rule in `task_transitions.py`:

```python
# Change this:
TaskStatus.backlog: {TaskStatus.in_progress},
# To this (breaks backlog→done rejection):
TaskStatus.backlog: {TaskStatus.in_progress, TaskStatus.done},
```

Run tests again:
```powershell
docker compose run --rm backend pytest tests/test_tasks.py -v
```

`test_backlog_to_done_rejected` and `test_invalid_direct_transition_returns_409` will fail. Revert the change.

**What to say:** "Two tests fail immediately — exactly the tests that guard the broken rule. The test suite has real coverage, not just green checkmarks."

---

## 10. Show the OpenAPI docs in the browser

Open `http://localhost:8000/docs`

**What to show:**
- Expand `POST /api/v1/projects` — show `ProjectCreate` request schema and `ProjectRead` response
- Expand `PATCH /api/v1/projects/{project_id}/tasks/{task_id}` — show `TaskUpdate` with `status` field and enum values
- Point out `GET /api/v1/projects/public/{slug}` returns `PublicProjectRead` — different schema, no auth lock icon
- Show `DELETE` endpoints return `204` with no response body

---

## Questions the lead may ask

**Q: Why not put the authorization check in the repository?**
A: The repository owns query mechanics. Authorization is a business rule — it changes independently of how the data is fetched. Mixing them makes both harder to test and change.

**Q: Why does `get_visible_or_404` return 404 for a private project instead of 403?**
A: 403 tells the caller the resource exists but they are not allowed. That leaks existence information about private projects. 404 is the correct response when a resource is not visible to the caller — regardless of whether it exists or not.

**Q: Why commit inside the service instead of in the route?**
A: The service owns the transaction boundary because it knows what constitutes a complete business operation. A route that commits would have to understand business rules to know when it is safe to commit. That is the wrong layer.

**Q: Why is `validate_transition` a standalone function instead of a method on `Task`?**
A: A pure function is easier to unit-test (no ORM, no DB, no fixtures needed), easier to read as a complete rulebook, and can be called from anywhere without loading a model instance first.

**Q: What prevents updating a task in project B by passing a task ID from project A?**
A: `task_repository.get_by_id_and_project(db, task_id, project_id)` filters by both `task.id` and `task.project_id`. A task from a different project will return `None` → 404, even if the task ID exists in the database.
