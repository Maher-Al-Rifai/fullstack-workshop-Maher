# Module 14 — Docker Compose and Full-Stack Integration

**Date:** 2026-09-01
**Branch:** `learning/14-compose-integration`

---

## Objectives in my own words

Configure Docker Compose so that both a development stack and an isolated acceptance stack start deterministically from a single command. Understand Docker service DNS (how containers find each other by name), health-condition startup ordering, volume persistence, and the separation between browser-facing URLs and server-side URLs.

---

## Key concepts

### Docker DNS vs host ports

| Caller | Reaches backend via |
|---|---|
| Browser on host machine | `http://localhost:8000` (published port) |
| Nuxt server-side (SSR) inside Docker | `http://backend:8000` (Docker service DNS) |
| Playwright inside Docker | `http://backend-test:8000` (Docker service DNS) |

If you point `NUXT_API_INTERNAL_BASE` at `localhost:8000` from inside a container, the request loops back to the container itself — not the backend. This is the most common cross-container mistake.

### `depends_on` + `condition: service_healthy`

`depends_on` alone only orders start, not readiness. Without `condition: service_healthy`, the backend can attempt to connect to a database that hasn't finished initialising. Health checks turn startup ordering into a readiness gate:

```
db (pg_isready) → backend (health/ready) → frontend → playwright
```

### Development vs acceptance stack

| Property | Dev (`compose.yaml`) | Acceptance (`compose.test.yaml`) |
|---|---|---|
| Images | Build `development` target (hot reload, source mount) | Build `production` target (compiled, no source) |
| Database | Persistent named volume | Ephemeral volume, torn down after run |
| Host ports | 8000, 3000 published | No unnecessary port publishing |
| Secret key | Dev default | `test-only-secret-not-for-production` |
| CORS origins | `localhost:3000` | `frontend-test:3000` |

### Volume persistence

Named volumes survive `docker compose restart` and `docker compose up -d --force-recreate`. They are destroyed only on `docker compose down -v`. This is how user data persists across code deployments.

---

## Changes made

### `compose.yaml`
- Added `NUXT_API_INTERNAL_BASE: http://backend:8000/api/v1` — SSR pages inside Docker now reach the backend via Docker DNS instead of trying `localhost`.
- Added `CORS_ORIGINS` env var so allowed origins are configurable without rebuilding.

### `compose.test.yaml`
- Added `SECRET_KEY` (test-only, never reused in production).
- Added `CORS_ORIGINS` allowing `frontend-test:3000` — Playwright's browser origin inside Docker.
- Added `NUXT_API_INTERNAL_BASE` and `NUXT_PUBLIC_API_BASE` both pointing to `backend-test:8000` (Playwright's Chromium runs inside Docker, so it can use Docker DNS).
- Added health check for `frontend-test`.
- Added `playwright` service with Playwright image, artifact volume mount, `BASE_URL` env, and dependency chain.
- Added `playwright-artifacts` volume for test evidence (Module 15 will populate it).
- No host ports published — the acceptance stack is self-contained.

### `backend/app/core/config.py`
- Added `cors_origins: list[str]` — pydantic-settings reads this from a JSON-array env var: `CORS_ORIGINS='["http://localhost:3000"]'`.

### `backend/app/main.py`
- Added FastAPI `lifespan` context manager that calls `Base.metadata.create_all(engine)` on startup.
  - Idempotent on the dev stack (tables already exist).
  - Creates all tables on the fresh acceptance database automatically — no manual migration step needed.
- CORS `allow_origins` now reads from `settings.cors_origins` instead of hardcoded list.

### `backend/pyproject.toml`
- Added explicit `pydantic>=2.13.0` lower bound.
  - Without it, the production pip resolver tried pydantic 2.9.x (the oldest version satisfying `>=2.9.0`), which requires pydantic-core 2.23.x — conflicting with pydantic-settings 2.14.2 which needs pydantic-core 2.46.x.

### `Makefile`
- Added `verify` target: runs `backend-quality` + `frontend-quality` (all lint, typecheck, test, build gates).
- Added `e2e-test` target: builds acceptance stack images, runs `playwright` service, tears down with volume removal.

---

## Commands and evidence

```text
# Dev stack — full rebuild with new config
docker compose up --build -d
docker compose ps
# → backend: healthy | db: healthy | frontend: up

# Docker DNS verification
docker compose exec frontend getent hosts backend
# → 172.18.0.3  backend

docker compose exec backend getent hosts db
# → 172.18.0.2  db

# CORS preflight check
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/register" -Method OPTIONS \
  -Headers @{ "Origin"="http://localhost:3000"; "Access-Control-Request-Method"="POST" }
# → 200, Access-Control-Allow-Origin: http://localhost:3000

# Backend tests
docker compose run --rm backend pytest -q
# → 67 passed  exit 0

# Frontend tests
docker compose exec frontend npm test
# → Test Files 3 passed | Tests 41 passed  exit 0

# Acceptance stack
docker compose -f compose.test.yaml build
docker compose -f compose.test.yaml run --rm playwright
# → db-test: healthy, backend-test: healthy, frontend-test: healthy
# → "Acceptance stack healthy. Module 15 adds Playwright specs."
docker compose -f compose.test.yaml down -v --remove-orphans
```

---

## Failure investigated

**Symptom:** Production backend image build fails with `ERROR: ResolutionImpossible` during `pip install .`.

**Smallest reproduction:** `docker compose -f compose.test.yaml build backend-test`

**Hypothesis:** Pip's resolver tries pydantic 2.9.x (oldest satisfying `pydantic>=2.9.0`) but that version requires pydantic-core 2.23.x, which conflicts with what pydantic-settings 2.14.2 needs.

**Evidence:** Build log line `pydantic 2.9.1 depends on pydantic-core==2.23.3` followed by `ResolutionImpossible`. Dev container has pydantic 2.13.5 + pydantic-core 2.46.5 (confirmed via `pip show`).

**Root cause:** No explicit lower bound on pydantic in `pyproject.toml`, so pip considered 2.9.x valid. The dev editable install (`pip install -e '.[dev]'`) used cached/pre-resolved packages and never hit the conflict.

**Fix:** Added `"pydantic>=2.13.0"` to `pyproject.toml` dependencies.

---

## Decision and tradeoff

**Decision:** Use `Base.metadata.create_all()` in the FastAPI lifespan instead of running `alembic upgrade head` as a separate init container.

**Alternative:** Run a dedicated migration container that executes alembic before the backend starts.

**Why chosen:** No alembic configuration exists in the project at this stage; `create_all` is idempotent and sufficient for the workshop. The tradeoff is that you lose migration history tracking — acceptable for a test stack, not acceptable for production data.

---

## Security, privacy, and operations

- `SECRET_KEY` in the acceptance stack uses an explicit test-only value — not the default dev string, not a real secret.
- No Docker socket mount, no privileged mode, no host networking in either stack.
- The acceptance database volume is destroyed after every run (`down -v`) — no test data leaks into the next run.
- `CORS_ORIGINS` is now configurable per environment; production should set it to the real domain only.
- Production backend image runs as non-root `app` user (established in Module 04 Dockerfile).
