# Module 04 — Docker Demo Guide
## What to open and show the lead

---

## 1. Open the two Dockerfiles side by side

**Files to open:**
- `backend/Dockerfile`
- `frontend/Dockerfile`

**What to point out in `backend/Dockerfile`:**

| Line | What to say |
|---|---|
| `FROM python:3.13.5-slim AS base` | "We use a slim base — no extra OS packages, smaller attack surface" |
| `RUN groupadd ... useradd ...` | "We create a non-root system user called `app` at build time" |
| `FROM base AS development` / `AS production` | "Multi-stage: dev stage has hot-reload, prod stage has `HEALTHCHECK`" |
| `USER app` (in production stage) | "The final image runs as uid 999, not root" |
| `HEALTHCHECK` | "Docker itself pings `/health/live` every 30s to detect a hung process" |

**What to point out in `frontend/Dockerfile`:**

| Line | What to say |
|---|---|
| `FROM node:22.16.0-alpine AS dependencies` | "Alpine base — much smaller than standard node image" |
| `COPY package.json ./` then `RUN npm install` | "We copy only package.json first so npm install is cached — code changes don't re-run it" |
| `FROM dependencies AS build` → `npm run build` | "Build stage compiles Nuxt to `.output/`" |
| `FROM node:22.16.0-alpine AS production` | "Production stage copies only `.output/` — no source code, no node_modules" |
| `COPY --from=build --chown=app:app /workspace/.output ./` | "We copy only the compiled output, not the full source" |
| `USER app` | "Non-root here too" |

---

## 2. Open the `.dockerignore` files

**Files to open:**
- `backend/.dockerignore`

**What to point out:**
- `.env` is excluded → "Secrets never enter a layer. Anyone who pulls the image cannot read them."
- `.git` is excluded → "Repo history is large and irrelevant at runtime"
- `.venv` / `__pycache__` → "The image installs its own fresh copy — local artifacts pollute the build context"

---

## 3. Run live in the terminal — prove non-root

Run these commands one at a time and show the output:

```powershell
docker run --rm --entrypoint whoami workboard-backend:module04
```
Expected output: `app`

```powershell
docker run --rm --entrypoint id workboard-backend:module04
```
Expected output: `uid=999(app) gid=999(app) groups=999(app)`

**What to say:** "The process inside the container cannot install packages, write to `/etc`, or access `/root` even if the app is exploited."

---

## 4. Show the stack running with Docker Compose

```powershell
docker compose up -d
docker compose ps
```

**What to show:**
- Three services running: `db`, `backend`, `frontend`
- All show `healthy` or `running`

Then open a browser to:
- `http://localhost:8000/health/live` → `{"status": "ok"}`
- `http://localhost:8000/health/ready` → shows DB connection result
- `http://localhost:3000` → Nuxt frontend

---

## 5. Show layer cache — rebuild without changes

```powershell
docker build --target production -t workboard-backend:module04 backend
```

**What to show:** Every layer prints `CACHED`. Rebuild time is under 1 second.

**What to say:** "Because `pyproject.toml` is copied before the full source, the expensive `pip install` layer is reused on every code change. If we did `COPY . .` first, pip would re-run every single time."

---

## 6. Show volumes vs down -v (concept — do NOT run `down -v`)

```powershell
docker compose down
docker volume ls
```

**What to show:** The named volume `starter-postgres-data` still exists after `down`.

**What to say:** "`docker compose down` stops containers but keeps volumes. Running `down -v` would delete the database. Never do that as a first troubleshooting step — collect logs first."

---

## Questions the lead may ask

**Q: What is the difference between `EXPOSE` and `ports:` in compose.yaml?**
A: `EXPOSE` is documentation only — it does nothing to your network. `ports:` in compose actually maps a host port to the container port so your browser can reach it.

**Q: Why multi-stage builds?**
A: The `build` stage has compilers, build tools, and dev dependencies. The `production` stage starts fresh and copies only the final artifact. The result is a smaller, cleaner image with no build tools that an attacker could abuse.

**Q: What happens when `docker stop` is called?**
A: Docker sends `SIGTERM` to PID 1 (uvicorn / node). The process drains in-flight requests and exits cleanly. If PID 1 were a shell script that doesn't forward signals, the app would never receive `SIGTERM` and Docker would force-kill it after 10 seconds.
