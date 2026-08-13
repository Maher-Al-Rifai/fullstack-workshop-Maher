# Module 05 — FastAPI Application Foundation
## Summary, Evidence & Presentation Guide

---

## What we built (file by file)

### New package structure created

```
backend/app/
├── api/
│   ├── __init__.py
│   ├── router.py              — mounts all /api/v1 routes
│   └── routes/
│       ├── __init__.py
│       ├── health.py          — /health/live, /health/ready, /health
│       └── status.py          — /api/v1/status, /api/v1/ping
├── core/
│   ├── config.py              — enhanced (was 2 fields, now 8)
│   └── exceptions.py          — NEW: domain error hierarchy
├── db/
│   └── session.py             — added get_db() DI + SessionLocal
└── main.py                    — rebuilt: CORS + routers + exception handlers

backend/tests/
├── conftest.py                — NEW: shared pytest fixture
├── test_health.py             — updated: added combined health test
├── test_status.py             — NEW: status shape + secret leak + 422
└── test_exceptions.py         — NEW: all 4 domain error handlers
```

---

## Step-by-step evidence

### Step 1 — Package structure established

The starter had all routes in `main.py` as flat functions. We split them into:
- Unversioned health routes at `/health/*` (no prefix — probes must not carry an API version)
- Versioned API routes at `/api/v1/*`

This separation means health checks work independently of the API version lifecycle.

### Step 2 — Typed settings (`core/config.py`)

**Before:** 2 fields — `app_name`, `database_url`

**After:** 8 typed fields with clear classification:

| Setting | Type | Classification |
|---|---|---|
| `app_name` | `str` | Public (safe to show) |
| `app_version` | `str` | Public |
| `environment` | `str` | Operational |
| `api_prefix` | `str` | Operational |
| `database_url` | `str` | **Secret** — never expose |
| `cors_origins` | `list[str]` | Operational |
| `secret_key` | `str` | **Secret** — never expose |
| `access_token_expire_minutes` | `int` | Operational |

`@lru_cache` on `get_settings()` means settings are read from the environment once.
Tests override this by setting `DATABASE_URL` before any import.

### Step 3 — Application factory and routers (`main.py`)

```python
app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, ...)

app.include_router(health_router)                        # unversioned
app.include_router(api_router, prefix=settings.api_prefix)  # /api/v1
```

CORS uses `allow_credentials=True` with explicit origins — wildcard (`*`) is
intentionally avoided when credentials/cookies are involved (security requirement).

### Step 4 — Health and status endpoints

| Endpoint | Versioned? | DB dependency? | Purpose |
|---|---|---|---|
| `GET /health/live` | No | No | Is the process running? |
| `GET /health/ready` | No | Yes (SELECT 1) | Can it serve traffic? |
| `GET /health` | No | Yes | Combined human-readable check |
| `GET /api/v1/status` | Yes | No | Name/version/environment only |

**Key design rule:** `/health/live` must NOT depend on the database.
If it did, a temporary DB outage would cause the orchestrator to kill and
restart the container — which cannot fix a database problem.

Status endpoint response:
```json
{"name": "Workboard API", "version": "0.1.0", "environment": "development"}
```
`secret_key` and `database_url` are intentionally absent from this response.

### Step 5 — Domain exception hierarchy (`core/exceptions.py`)

```
WorkboardError (base)
├── NotFoundError       → 404  {"code": "not_found"}
├── UnauthorizedError   → 401  {"code": "unauthorized"}
├── ForbiddenError      → 403  {"code": "forbidden"}
└── ConflictError       → 409  {"code": "conflict"}
    └── InvalidTransitionError  (state-machine errors)
```

Exception handlers in `main.py` convert domain errors to a stable JSON shape:
```json
{"detail": "Human-readable message", "code": "stable_machine_code"}
```
Unexpected exceptions (not in this hierarchy) remain `500` — safe for clients,
useful in server logs.

### Step 6 — Schema-backed route (ping endpoint)

Added `POST /api/v1/ping` to demonstrate Pydantic request/response validation:

```python
class PingRequest(BaseModel):
    message: str

class PingResponse(BaseModel):
    echo: str
```

Sending a missing field returns `422 Unprocessable Entity` with FastAPI's
structured validation error — not `400` or `200`.

### Step 7 — Dependency injection (`db/session.py`)

```python
def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
```

The `yield` makes this a context manager dependency — the session opens before
the route function runs and closes automatically after the response is sent,
even if an exception is raised. Routes declare it as:

```python
def my_route(db: Session = Depends(get_db)) -> ...:
```

This replaces the anti-pattern of module-level global session objects.

### Step 8 — Foundation tests

**Test results:**
```
10 passed — ruff lint: All checks passed — ruff format: 16 files already formatted
```

**Test coverage breakdown:**

| File | Tests | What is verified |
|---|---|---|
| `test_health.py` | 2 | liveness without DB; combined health response shape |
| `test_status.py` | 4 | status shape; secret fields absent; ping 201; missing field 422 |
| `test_exceptions.py` | 4 | NotFoundError→404, UnauthorizedError→401, ForbiddenError→403, ConflictError→409 |

**Dependency override pattern (key concept):**
```python
# Tests set DATABASE_URL before importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
```
This makes `get_settings()` cache the SQLite URL instead of the real Postgres URL.
Tests never touch the developer database.

---

## Key concepts to present

### 1. Route function as HTTP adapter
A FastAPI route should only:
1. Parse/validate input via Pydantic schema
2. Receive dependencies (db session, current user)
3. Call a service
4. Return a declared response model

It should NOT contain business logic, raw SQL, or global state.

### 2. Liveness vs Readiness (reinforced)
- Liveness: "Is the process alive?" — No DB check. Never fail just because a dependency is temporarily down.
- Readiness: "Can it serve traffic?" — Checks DB. Fail if DB is unreachable.

### 3. Settings classification
| Classification | Examples | Can appear in response? |
|---|---|---|
| Public | app_name, version, environment | Yes |
| Operational | api_prefix, cors_origins, token durations | No (internal config) |
| Secret | secret_key, database_url | Never |

### 4. Exception handler contract
Domain errors use a consistent body so the frontend can handle them programmatically:
```json
{"detail": "readable message", "code": "machine_readable_code"}
```
Unknown errors stay `500` — never leak internal details externally.

---

## Validation checklist (completed)

- [x] Application imports and starts through `app.main:app`
- [x] Versioned API (`/api/v1/*`) and unversioned health (`/health/*`) paths are distinct
- [x] Settings are typed; secrets classified and never returned by any endpoint
- [x] Readiness uses database check; liveness does not
- [x] Known domain errors have stable safe JSON responses with machine-readable codes
- [x] OpenAPI at `/docs` shows declared schemas, status codes, and tags
- [x] 10 foundation tests pass using SQLite override, not developer database

---

## Commit message

```
feat(api): establish FastAPI application foundation
```
