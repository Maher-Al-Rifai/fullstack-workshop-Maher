# Module 14 — Demo Guide: Docker Compose and Full-Stack Integration

**Audience:** Instructor / reviewer  
**Stack required:** `docker compose up --build -d` running

---

## Demo 1 — One-command startup from scratch (2 min)

Show that the full product starts from a single command:

```bash
docker compose down -v
docker compose up --build -d
docker compose ps
```

Point out the health chain in the output:
1. `db` becomes healthy (pg_isready)
2. `backend` starts only after db is healthy, then becomes healthy (`/health/ready`)
3. `frontend` starts only after backend is healthy

Open <http://localhost:3000> — the app is serving.

---

## Demo 2 — Docker DNS: why `localhost` breaks inside a container (3 min)

Open two browser tabs side by side:
- `http://localhost:3000` → the Nuxt frontend (published port)
- `http://localhost:8000/docs` → FastAPI OpenAPI (published port)

Now explain: inside the Docker network these containers cannot reach each other via `localhost`. Demonstrate:

```bash
# ✅ frontend resolves 'backend' via Docker DNS
docker compose exec frontend getent hosts backend

# ✅ backend resolves 'db' via Docker DNS
docker compose exec backend getent hosts db

# Show what the SSR base URL actually is
docker compose exec frontend env | grep NUXT_API_INTERNAL
# → NUXT_API_INTERNAL_BASE=http://backend:8000/api/v1
```

Explain: `NUXT_PUBLIC_API_BASE` is `localhost:8000` — for the browser on the host. `NUXT_API_INTERNAL_BASE` is `backend:8000` — for Nuxt server-side rendering inside Docker. If you used `localhost` for SSR, every server-rendered page would fail.

---

## Demo 3 — Volume persistence (2 min)

1. Register a new account and create a project.
2. Force-recreate the containers without touching the volume:

```bash
docker compose up -d --force-recreate backend frontend
```

3. Refresh the browser — the project is still there. The data lives in `starter-postgres-data` volume, not in the container.
4. Destroy the volume:

```bash
docker compose down -v
docker compose up --build -d
```

5. Refresh — project is gone. The volume deletion is the only thing that wipes data.

---

## Demo 4 — CORS: what happens without it (2 min)

Open the browser DevTools Network tab. Register or log in. Show the `POST /api/v1/auth/register` request includes `Access-Control-Allow-Origin: http://localhost:3000` in the response headers.

Then explain what would happen without it:

```bash
# Simulate preflight
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/register" `
  -Method OPTIONS `
  -Headers @{ "Origin"="http://localhost:3000"; "Access-Control-Request-Method"="POST" }
# → 200 + Access-Control-Allow-Origin header
```

Without `CORSMiddleware`, the browser blocks the response before JavaScript sees it. The error in the browser would be "Failed to fetch" with no status code — the same error we debugged.

---

## Demo 5 — Acceptance stack: isolated, production images, disposable (3 min)

```bash
docker compose -f compose.test.yaml build
docker compose -f compose.test.yaml run --rm playwright
```

Narrate as it runs:
- `db-test` spins up — completely separate from the dev database
- `backend-test` starts with production image (no `--reload`, no source mount)
- `frontend-test` starts with pre-built Nuxt output (Nitro server)
- `playwright` service runs, reports healthy stack, exits 0
- All volumes are destroyed (`down -v` in the `e2e-test` make target)

Point out key differences from dev:
- No published host ports — nothing on `localhost:8000` or `localhost:3000`
- `SECRET_KEY` is a test-specific value
- `CORS_ORIGINS` allows `frontend-test:3000` — the browser origin inside Docker

---

## Demo 6 — Failure drill: wrong internal API base (2 min)

Show what happens when `NUXT_API_INTERNAL_BASE` is wrong. Temporarily set it to `localhost`:

```bash
# In a separate terminal — override just for this run
NUXT_API_INTERNAL_BASE=http://localhost:8000/api/v1 docker compose up -d frontend
docker compose logs frontend
```

Navigate to a server-rendered page like `/` (prerendered — not affected) then try a page that does SSR fetch. The request from the Nuxt server would go to `localhost:8000` inside the container — which is the frontend container itself, not the backend. You'd see a connection refused error in logs.

Restore: `docker compose up -d frontend` (without the override) to return to correct config.

---

## Key talking points

- **"depends_on without health"** — orders start, not readiness. Sleep-based waits are fragile. Health conditions are observable state.
- **"Sharing the dev database with E2E"** — a classic mistake. Acceptance tests must use their own database so test data doesn't contaminate development data and vice versa.
- **"Source mounts in production-like containers"** — mounts hide image build problems. The acceptance stack builds real production images so you find problems before deployment, not during it.
- **"pydantic resolver bug"** — pip's default resolver tries the oldest satisfying version. Always add explicit lower bounds for packages that have known good versions.
