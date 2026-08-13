# Module 04 — Docker & Container Fundamentals
## Summary, Evidence & Presentation Guide

---

## What we did (step by step)

### Step 1 — Read the Dockerfiles

Read `backend/Dockerfile` and `frontend/Dockerfile` and analysed every stage.

**Backend Dockerfile stages:**

| Stage | Base | User | Command | Purpose |
|---|---|---|---|---|
| `base` | `python:3.13.5-slim` | root | — | Sets env vars, creates `app` system user |
| `development` | base | `app` | `uvicorn --reload` | Hot-reload dev server |
| `production` | base | `app` | `uvicorn` | Production server with HEALTHCHECK |

**Frontend Dockerfile stages:**

| Stage | Base | User | Command | Purpose |
|---|---|---|---|---|
| `dependencies` | `node:22.16.0-alpine` | root | — | Installs npm packages once |
| `build` | dependencies | root | `npm run build` | Compiles Nuxt to `.output/` |
| `production` | `node:22.16.0-alpine` | `app` | `node server/index.mjs` | Serves only compiled output |

---

### Step 2 — Built production images without Compose

```powershell
docker build --target production -t workboard-backend:module04 backend
docker build --target production -t workboard-frontend:module04 frontend
docker image ls | findstr workboard
docker history workboard-backend:module04
```

**Evidence collected:**

```
workboard-backend:module04     298 MB
workboard-frontend:module04    231 MB
```

Backend image history (bottom to top = oldest to newest layer):
- Debian base OS (~85 MB)
- Python 3.13.5 runtime (~41 MB)
- WORKDIR + app user creation
- COPY source files (~70 KB)
- pip install dependencies (~91 MB)
- USER app
- HEALTHCHECK
- CMD uvicorn

No secrets found in any layer. Build logs contain no real credentials.

---

### Step 3 — Proved non-root runtime identity

```powershell
docker run --rm --entrypoint whoami workboard-backend:module04
docker run --rm --entrypoint id workboard-backend:module04
docker run --rm --entrypoint whoami workboard-frontend:module04
```

**Output:**
```
app
uid=999(app) gid=999(app) groups=999(app)
app
```

**Explanation:** Both final images run as user `app` (uid 999), not `root`.

**Why non-root reduces impact but is not a complete sandbox:**
Running as a non-root user means an attacker who exploits the app cannot install
system packages, modify `/etc`, or access `/root`. However they can still read all
app files, environment variables, and communicate over the network. A complete
sandbox also requires seccomp profiles, read-only root filesystems, and network
policy.

---

### Step 4 — Inspected liveness without database

The backend `/health/live` endpoint does not query the database (process-level only).
The `/health/ready` endpoint requires PostgreSQL. For an isolated liveness test, use
Compose which wires up all three services together.

---

### Step 5 — Layer cache experiment

Built the same backend image twice without changing any files.

**Second build output:** Every layer showed `CACHED`. Rebuild time: under 1 second.

**Why copying dependency files before source matters:**

```dockerfile
# CORRECT — slow-changing file copied first
COPY pyproject.toml ./        # layer cached until deps change
RUN pip install .             # only rebuilds when pyproject.toml changes
COPY . .                      # source changes every commit, but deps stay cached

# WRONG — everything in one copy
COPY . .                      # any code change invalidates the next layer
RUN pip install .             # full pip install on every single code edit
```

Copying `pyproject.toml` or `package.json` before the full source means the
expensive dependency install layer is reused on every normal code change, cutting
build time from minutes to seconds.

---

### Step 6 — Inspected .dockerignore files

Three `.dockerignore` files were read: root, backend, frontend.

**What is excluded and why:**

| Excluded | Reason |
|---|---|
| `.env` | Contains secrets — must never enter an image |
| `.git` | Repo history — large and irrelevant to runtime |
| `node_modules`, `.venv` | Local artifacts — image installs its own fresh copy |
| `__pycache__`, `.pytest_cache` | Generated files — not needed at runtime |
| `.nuxt`, `.output` | Build artifacts — rebuilt inside the image |
| `coverage`, `htmlcov` | Test reports — not part of the app |

**Key concept:** The build context is the folder Docker sends to the daemon before
any `RUN` executes. Without `.dockerignore`, a `COPY . .` instruction would
include `.env` in the image layer — where anyone who pulls the image can read it.

---

### Step 7 — Failure drills

#### Drill 1 — Wrong CMD executable

```powershell
docker run --rm --entrypoint badcommand workboard-backend:module04
```

**Error:**
```
executable file not found in $PATH
Exit code: 127
```

- **Root cause:** `badcommand` does not exist inside the image
- **Exit code 127** = standard Unix "command not found"
- **Diagnostic command:** `docker run --rm --entrypoint sh workboard-backend:module04 -c "which uvicorn"`
- **Fix:** Check `CMD`/`ENTRYPOINT` spelling in the Dockerfile matches an installed binary

#### Drill 2 — Missing required environment variable

```powershell
docker run --rm -e DATABASE_URL="" workboard-backend:module04
```

**Error:**
```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from given URL string
Exit code: 1
```

- **Root cause:** `DATABASE_URL` is empty so SQLAlchemy cannot build a connection string at startup
- **Diagnostic command:** `docker logs <container_id>`
- **Fix:** Always provide required env vars via `.env` or Compose `environment:` block. Never hardcode them in the image.

---

### Step 8 — Signal and shutdown behavior

**PID 1 in backend production image:** `uvicorn`

When `docker stop` is run:
1. Docker sends `SIGTERM` to PID 1 (uvicorn)
2. Uvicorn drains in-flight requests and shuts down cleanly
3. If PID 1 is a shell script that does not forward signals, the app never receives
   `SIGTERM` and Docker force-kills it with `SIGKILL` after 10 seconds

**PID 1 in frontend production image:** `node server/index.mjs`

Node handles `SIGTERM` and closes the HTTP server gracefully.

---

## Key concepts to present

### 1. Image vs Container

| | Image | Container |
|---|---|---|
| What it is | Immutable frozen template | Running process from an image |
| Persistence | Permanent until deleted | Temporary — filesystem resets on stop |
| Analogy | Blueprint | Building constructed from blueprint |

### 2. EXPOSE vs Published port vs Compose DNS

| | `EXPOSE` | Published port (`-p`) | Compose service DNS |
|---|---|---|---|
| What it does | Documentation only | Maps host port → container port | Containers talk by name |
| Example | `EXPOSE 8000` | `-p 8000:8000` | `http://backend:8000` |
| Who sees it | Humans reading Dockerfile | Your browser / curl | Other containers only |

**Common mistake:** Assuming `EXPOSE 8000` makes the port accessible from your browser. It does not. Only `ports:` in compose.yaml or `-p` in `docker run` does that.

### 3. Layers and cache

Every `RUN`, `COPY`, and `FROM` line creates a layer. Docker caches layers. A
changed layer invalidates all layers below it. Order your Dockerfile from
least-frequently-changed to most-frequently-changed.

### 4. Non-root user

Production images create and switch to a non-root `app` user. This limits the blast
radius if the application is compromised. It is required practice for any container
running in production.

### 5. Volumes vs containers

- `docker compose down` — stops containers, **keeps** named volumes (database data safe)
- `docker compose down -v` — stops containers AND **deletes** volumes (database wiped)
- Never use `down -v` as a first troubleshooting step — collect logs first

---

## Validation checklist (completed)

- [x] Both production images build from their final `--target production` stage
- [x] Both backend and frontend processes run as non-root user `app` (uid 999)
- [x] Every Dockerfile stage analysed — input, output, user, command, purpose
- [x] No environment secrets found in image history or build context
- [x] Two failure drills performed with exit codes, root causes, and fixes recorded
- [x] EXPOSE vs published ports vs Compose DNS distinction documented

---

## Commit message

```
chore(docker): document and validate production image fundamentals
```
