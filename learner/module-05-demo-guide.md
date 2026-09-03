# Module 05 — FastAPI Demo Guide
## What to open and show the lead

---

## 1. Open the folder structure in VS Code Explorer

Navigate to `backend/app/` and expand it. Show the lead this tree:

```
app/
├── api/
│   ├── router.py          ← mounts all /api/v1 routes
│   └── routes/
│       ├── health.py      ← unversioned probes
│       └── status.py      ← versioned status + ping
├── core/
│   ├── config.py          ← typed settings
│   └── exceptions.py      ← domain error hierarchy
├── db/
│   └── session.py         ← session factory + get_db()
└── main.py                ← app factory + middleware + exception handlers
```

**What to say:** "The starter had all routes as flat functions in `main.py`. We split this into layers: each file has one responsibility."

---

## 2. Open `backend/app/core/config.py`

**What to point out:**

```python
class Settings(BaseSettings):
    app_name: str = "Workboard API"       # public — safe to show
    app_version: str = "0.1.0"            # public
    environment: str = "development"       # operational
    api_prefix: str = "/api/v1"           # operational
    database_url: str = "postgresql+..."  # SECRET — never expose
    cors_origins: list[str] = [...]       # operational
    secret_key: str = "changeme-..."      # SECRET — never expose
    access_token_expire_minutes: int = 30 # operational
```

**What to say:**
- "Every config value is typed — no raw `os.getenv()` calls with silent `None` fallbacks"
- "`@lru_cache` on `get_settings()` means the environment is read exactly once at startup"
- "Settings are classified: `secret_key` and `database_url` never appear in any API response"

---

## 3. Open `backend/app/core/exceptions.py`

**What to point out:**

```python
WorkboardError          ← base
├── NotFoundError       → 404
├── UnauthorizedError   → 401
├── ForbiddenError      → 403
└── ConflictError       → 409
    └── InvalidTransitionError
```

**What to say:** "Business logic raises Python exceptions — never HTTP status codes directly. The exception handlers in `main.py` translate them. This means a service function doesn't need to know about HTTP."

---

## 4. Open `backend/app/main.py`

**What to point out — three sections:**

**Section 1 — Middleware:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    ...
)
```
"CORS uses an explicit list from settings — never `allow_origins=["*"]` when credentials are involved."

**Section 2 — Router mounting:**
```python
app.include_router(health_router)                          # no prefix — /health/*
app.include_router(api_router, prefix=settings.api_prefix) # /api/v1/*
```
"Health probes are intentionally unversioned. Kubernetes/Docker must probe them independently of the API version lifecycle."

**Section 3 — Exception handlers:**
```python
@app.exception_handler(NotFoundError)
async def not_found_handler(...) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": ..., "code": "not_found"})
```
"Every domain error maps to a stable `code` string. The frontend can branch on `"not_found"` without parsing the human-readable `detail`."

---

## 5. Open `backend/app/api/routes/health.py` and `status.py`

**health.py — point out:**
- `/health/live` has NO database call → "A DB outage must not kill the process. Liveness and readiness are separate probes."
- `/health/ready` runs `SELECT 1` → "This fails if the DB is unreachable — the load balancer stops routing traffic here."

**status.py — point out:**
- Response includes `name`, `version`, `environment` only
- `secret_key` and `database_url` are intentionally absent

---

## 6. Open `backend/app/db/session.py`

**What to point out:**

```python
def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
```

**What to say:** "The `yield` makes this a context manager dependency. The session opens before the route runs and closes automatically after the response — even if an exception is raised. This replaces the anti-pattern of module-level global session objects."

---

## 7. Run the tests live

```powershell
docker compose run --rm backend pytest tests/test_health.py tests/test_status.py tests/test_exceptions.py -v
```

**Expected output to show:**
```
tests/test_health.py::test_liveness_returns_ok PASSED
tests/test_health.py::test_combined_health_shape PASSED
tests/test_status.py::test_status_shape PASSED
tests/test_status.py::test_status_does_not_leak_secret PASSED
tests/test_status.py::test_ping_returns_201 PASSED
tests/test_status.py::test_ping_missing_field_returns_422 PASSED
tests/test_exceptions.py::test_not_found_returns_404 PASSED
tests/test_exceptions.py::test_unauthorized_returns_401 PASSED
tests/test_exceptions.py::test_forbidden_returns_403 PASSED
tests/test_exceptions.py::test_conflict_returns_409 PASSED
10 passed
```

**What to say:** "Tests use SQLite in-memory — we set `DATABASE_URL` before importing any app module so `@lru_cache` caches the SQLite URL. Tests never touch the developer database."

---

## 8. Show the OpenAPI docs in the browser

Open `http://localhost:8000/docs`

**What to show:**
- Expand `GET /api/v1/status` — show the declared response model
- Expand `POST /api/v1/ping` — show the request schema and 422 response
- Expand `GET /health/live` — show it has no prefix `/api/v1`
- Point out the version shown in the top-left matches `config.py`

---

## Questions the lead may ask

**Q: Why not just use `os.getenv()` everywhere?**
A: Untyped `getenv` returns `None` silently. `pydantic-settings` gives you type coercion, validation at startup, and a single source of truth that is testable.

**Q: Why is the status endpoint at `/api/v1/status` but health at `/health`?**
A: Health probes are called by infrastructure (Docker, Kubernetes). They must not carry an API version because they are not part of the application contract — they are an operational concern.

**Q: Why does `get_db()` use `yield` instead of `return`?**
A: `yield` turns it into a generator. FastAPI runs the code after `yield` as cleanup — the session is always closed, even if the route raises an exception. `return` would require the route to manually close the session.

**Q: What happens if someone passes an unknown field to `/api/v1/ping`?**
A: Pydantic ignores extra fields by default. Only the declared fields are used. A missing required field returns 422 with a structured error body — not 400 or 500.
