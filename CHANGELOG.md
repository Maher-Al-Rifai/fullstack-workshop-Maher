# Changelog

## [Unreleased] — Modules 04–13 implementation

### Module 13 — Frontend testing with Vitest (2026-09-01)

- Added `vitest.config.ts` with happy-dom environment, `@vitejs/plugin-vue`, and `~` alias.
- Added `tests/setup.ts` stubbing all Nuxt auto-imports for isolated unit tests.
- Added `frontend/app/utils/api-client.ts`: `createApiFetch` factory with bearer-token injection, 401→refresh→retry logic, and `normalizeError`.
- Added `frontend/app/utils/labels.ts`: `STATUS_LABELS` and `PRIORITY_LABELS` maps.
- Added `frontend/app/utils/formatDate.ts`: null-safe ISO date formatter.
- Added 41 tests across `tests/unit/utils.test.ts`, `tests/unit/api-client.test.ts`, and `tests/components/TaskCard.test.ts`.
- Improved `normalizeError` to handle Pydantic 422 validation arrays and status-based fallback messages.
- Updated all pages to use `normalizeError` for consistent, human-readable inline error banners.
- Fixed `LoginRequest.username` → `LoginRequest.email` throughout types, auth store, and login page.
- Added `CORSMiddleware` to `backend/app/main.py` allowing `localhost:3000` (missing since Module 08).
- Fixed doubled `/api/v1` path prefix in `auth.ts` and `[slug].vue` (baseURL already includes prefix).

### Module 12 — SSR, SEO, accessibility, and performance

- Added `routeRules` in `nuxt.config.ts`: prerender `/`, SWR on `/public/projects/**`, `ssr: false` on auth/dashboard pages.
- Added public SSR project page at `pages/public/projects/[slug].vue` with Open Graph meta.
- Added `useSeoMeta` calls on all pages.
- Used `apiInternalBase` (server-side) vs `apiBase` (client-side) split in SSR fetch.

### Module 11 — Frontend API integration and state

- Added `useProjects` and `useTasks` composables via `useApi` / `createApiFetch`.
- Added Pinia `auth` store with login, register, logout, refresh, and `initialize` plugin.
- Added `middleware/auth.ts` redirect guard.
- Implemented dashboard, projects list, and project detail pages with full task lifecycle.

### Module 10 — Nuxt, Vue, and TypeScript foundation

- Scaffolded Nuxt 4 frontend: `nuxt.config.ts`, `tsconfig.json`, CSS variables, `AppHeader`, `AppFooter`.
- Added `app/types/index.ts` with all domain types and `TaskStatus`/`TaskPriority` enums.
- Added `UiErrorAlert`, `UiLoadingSpinner`, `StatusBadge`, `ProjectCard`, `TaskCard` components.
- Configured `@pinia/nuxt` and `@nuxt/eslint` modules.

### Modules 04–09 — Backend foundation

- Module 04: Dockerfile multi-stage build for backend and frontend.
- Module 05: FastAPI app with `/api/v1` router, versioned prefix, exception handlers.
- Module 06: PostgreSQL + SQLAlchemy 2.0 models, Alembic migrations (`users`, `projects`, `tasks`).
- Module 07: Projects and tasks CRUD services and repositories with ownership enforcement.
- Module 08: Argon2 password hashing, JWT access tokens, HTTP-only refresh-cookie rotation, auth routes.
- Module 09: Pytest suite with SQLite in-memory DB, coverage gate ≥ 80%, ruff + mypy gates.

## 1.0.0 — 2026-07-22

- Added complete FastAPI, SQLAlchemy, Alembic, PostgreSQL reference backend.
- Added Nuxt 4, Vue, TypeScript, Pinia reference frontend with a public SSR page.
- Added Pytest, Vitest, component, API-client, and Playwright test layers.
- Added development and isolated acceptance Docker Compose environments.
- Added pull-request CI and keyless Google Cloud deployment workflow.
- Added Terraform foundation for Artifact Registry, Cloud SQL, Secret Manager, IAM, and GitHub workload identity federation.
- Added twenty learner modules, instructor materials, assessment rubric, templates, official references, and starter snapshot.
- Added package manifest, GitHub publishing procedure, standalone starter validator, and release validation report.
- Added explicit browser-domain/session acceptance guidance and production cookie-attribute regression coverage.
