# Full-stack intern workshop — Workboard

Modules 00–13 complete. The full application stack is running: authenticated CRUD for projects and tasks, server-side rendered public pages, and a Vitest unit/component test suite.

## Start here

```bash
cp .env.example .env
docker compose up --build
```

Open:

- frontend: <http://localhost:3000>
- backend live health: <http://localhost:8000/health/live>
- backend ready health: <http://localhost:8000/health/ready>
- backend OpenAPI: <http://localhost:8000/docs>

Run all quality gates:

```bash
make backend-test       # pytest + ruff + mypy
make frontend-test      # vitest run
make frontend-lint      # eslint
make frontend-typecheck # vue-tsc
```

Stop and delete the disposable database volume:

```bash
make clean
```

## What is implemented

- FastAPI with versioned `/api/v1` router, Pydantic schemas, SQLAlchemy models, Alembic migrations.
- Argon2 password hashing, JWT access tokens, HTTP-only refresh-cookie rotation.
- CORS configured for `localhost:3000` (development).
- Projects and tasks CRUD with ownership enforcement.
- Nuxt 4 frontend: login, register, dashboard, projects list, project detail with task management.
- SSR public project page with prerendering and Open Graph meta.
- Pinia auth store with token refresh and unauthenticated redirect.
- Vitest suite: pure utils, API client, TaskCard component (41 tests).
- Professional inline error messages via `normalizeError` on all pages.

## Remaining modules

Modules 14–19 cover Docker Compose full-stack integration, Playwright E2E, GitHub Actions CI, Google Cloud deployment, and production operations.

## Architecture

```text
browser -> Nuxt :3000
              |
              v  (client-side: localhost:8000 | server-side: backend:8000)
          FastAPI :8000 -> PostgreSQL :5432
```

Follow [the workshop index](workshop/README.md) and keep a personal copy of [the learning log](learner/LEARNING_LOG.md).
