# Module 05: FastAPI application foundation

**Guided effort:** 8 hours  
**Required branch:** `learning/05-fastapi-foundation`  
**Phase:** Backend

## Objectives

- Create a FastAPI application factory/module with versioned routers and settings.
- Define Pydantic request/response models and explicit status codes.
- Use dependency injection for database/current-user boundaries rather than global mutable state.
- Implement liveness/readiness/status endpoints and a consistent domain error mapping.

## Prerequisites

- Foundation gate passed.
- Basic Python functions, classes, imports, exceptions, and type hints.
- HTTP contract from Module 03.

## Concepts and context

FastAPI uses Python type annotations and Pydantic models to validate requests, serialize responses, and generate OpenAPI. A route function should remain an HTTP adapter: parse/validate through schemas, receive dependencies, call a service, and return a declared response.

Settings should be loaded from environment with typed validation. Development convenience must not make insecure production defaults silently acceptable. Liveness checks process health; readiness checks dependencies required to serve traffic.

## Step-by-step lab

### 1. Establish package structure

In the starter, create or inspect:

```text
backend/app/
├── api/router.py
├── api/routes/health.py
├── api/routes/status.py
├── core/config.py
├── core/exceptions.py
├── db/session.py
└── main.py
```

Add `__init__.py` files where required. Run imports from the backend directory or installed package, not by manipulating `sys.path` in production code.

### 2. Define typed settings

Use `pydantic-settings` for application name/version, environment, API prefix, database URL, CORS origins, token durations, and cookie settings. Cache settings only after understanding that tests may need to clear/override the cache.

Validate that a production environment cannot start with a known short demonstration signing key. Document which settings are secret, public, or operational.

### 3. Create the application and routers

Build `app.main:app`, include a root health router and an API router under `/api/v1`. Configure CORS from parsed origins. Avoid wildcard origins when credentials/cookies are involved.

Run:

```bash
cd backend
uvicorn app.main:app --reload
```

Or use Compose. Inspect `/docs` and `/openapi.json`.

### 4. Implement health and status contracts

Required:

```text
GET /health/live
GET /health/ready
GET /health
GET /api/v1/status
```

Readiness executes a minimal database query through an injected session. Do not expose database URLs or secret configuration in status output.

### 5. Add domain exceptions

Create a small hierarchy such as not found, unauthorized, forbidden, conflict, and invalid transition. Map known domain errors to a stable JSON response through an exception handler. Unexpected exceptions should remain `500` with safe external detail and useful internal logs.

### 6. Add a first schema-backed route

Before project persistence is complete, implement a small typed request/response exercise or status representation. Declare `response_model` and status explicitly. Send malformed data and observe the `422` structure.

### 7. Write foundation tests

Add tests for:

- liveness success without a dependency query;
- readiness success with the test database;
- status response shape;
- one invalid schema;
- one mapped domain error if a route exercises it.

Use dependency override rather than connecting tests to the developer database.

### 8. Check quality

```bash
cd backend
ruff check .
ruff format --check .
mypy app
pytest -q
```

Fix the cause rather than suppressing type/lint rules broadly.

## Validation checklist

- [ ] Application imports and starts through `app.main:app`.
- [ ] Versioned API and unversioned health paths are distinct.
- [ ] Settings are typed and production secret defaults are guarded.
- [ ] Readiness uses an injected database session; liveness does not.
- [ ] Known domain errors have a stable safe response.
- [ ] OpenAPI shows declared schemas/status/security where applicable.
- [ ] Foundation tests pass without using the developer database.

## Independent challenge

Add a request-ID middleware that accepts or creates an ID, returns it in a response header, and makes it available for logs. Test header preservation/generation without logging tokens or bodies.

## Common failure modes

- Putting database sessions or service objects in module-global mutable variables.
- Returning ORM objects without declared response schemas.
- Making readiness and liveness identical.
- Exposing configuration values in a status endpoint.
- Catching every exception and returning 200 or generic 400.

## Evidence to submit

- OpenAPI screenshot or path/schema excerpt.
- Health/status curl responses.
- Settings classification table.
- Test output and one explanation of dependency override.
- Request-ID challenge evidence if completed.

## Commit checkpoint

```text
feat(api): establish FastAPI application foundation
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [README.md](../backend/README.md)
- [api-contract.md](../docs/api-contract.md)
- [https://fastapi.tiangolo.com/tutorial/first-steps/](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [https://fastapi.tiangolo.com/tutorial/dependencies/](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [https://docs.pydantic.dev/latest/concepts/pydantic_settings/](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
