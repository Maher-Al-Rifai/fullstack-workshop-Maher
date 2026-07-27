# Workshop modules

The workshop is a gated, cumulative path from a clean workstation to a deployed and operated full-stack application. Complete modules in numerical order unless an instructor explicitly changes the sequence. Each module ends with evidence, a commit checkpoint, and an independent challenge; reading alone is not completion.

## How to use a module

1. Create the required branch from the latest approved base branch.
2. Read the objectives and prerequisites before changing code.
3. Complete the lab in small, reviewable commits.
4. Run every validation command and retain useful evidence.
5. Complete the independent challenge without copying the reference implementation.
6. Update the learning log and open a pull request using the repository template.
7. Do not continue past a formal gate until the reviewer records a pass or a documented conditional pass.

## Module index

| Module | Focus | Primary outcome |
|---:|---|---|
| [00](00-orientation-and-definition-of-done.md) | Orientation and definition of done | Evidence-based learning plan and shared delivery expectations |
| [01](01-workstation-and-repository-setup.md) | Workstation and repository setup | Reproducible local toolchain and verified clone |
| [02](02-git-github-and-pull-requests.md) | Git, GitHub, and pull requests | Safe branch, commit, review, and merge workflow |
| [03](03-http-rest-json-and-api-contracts.md) | HTTP, REST, JSON, and contracts | Written API contract with correct status and error semantics |
| [04](04-docker-and-container-fundamentals.md) | Docker fundamentals | Secure, understandable images and containers |
| [05](05-fastapi-application-foundation.md) | FastAPI foundation | Versioned API, configuration, health endpoints, and OpenAPI |
| [06](06-postgresql-sqlalchemy-and-alembic.md) | PostgreSQL and migrations | Relational model, SQLAlchemy mappings, and reproducible schema |
| [07](07-backend-domain-architecture-and-crud.md) | Backend architecture and CRUD | Route/service/repository flow with business rules |
| [08](08-authentication-authorization-and-api-security.md) | Authentication and authorization | Secure identity flow and object-level access control |
| [09](09-backend-testing-and-quality-gates.md) | Backend testing | Unit, repository, API, coverage, lint, and type gates |
| [10](10-nuxt-vue-and-typescript-foundation.md) | Nuxt, Vue, and TypeScript | Accessible component and routing foundation |
| [11](11-frontend-api-integration-and-state.md) | Frontend API integration | Typed service layer, auth session, and robust UI states |
| [12](12-ssr-seo-accessibility-and-performance.md) | SSR, SEO, accessibility, and performance | Crawlable public pages and measurable quality |
| [13](13-frontend-testing-with-vitest.md) | Frontend tests | Unit, component, and service-level confidence |
| [14](14-docker-compose-and-full-stack-integration.md) | Full-stack integration | One-command, health-aware local environment |
| [15](15-playwright-api-and-browser-testing.md) | System testing | Deterministic API and browser acceptance tests |
| [16](16-github-actions-ci-and-delivery-controls.md) | CI and delivery controls | Pull-request pipeline and protected delivery path |
| [17](17-google-cloud-foundation-and-deployment.md) | Google Cloud deployment | Artifact Registry, Cloud Run, Cloud SQL, secrets, and OIDC |
| [18](18-operations-observability-incidents-and-rollback.md) | Operations and rollback | Logs, signals, incident response, and safe traffic rollback |
| [19](19-final-capstone-and-production-readiness.md) | Final capstone | Clean-clone proof, production review, and technical defense |

## Course gates

The detailed gate criteria live in [the module gate guide](../instructor/MODULE_GATES.md). At minimum, reviewers should stop progression after the backend, frontend, integrated system, CI, and cloud-delivery milestones. The final capstone is a live demonstration, not a document-only submission.

## Supporting material

- [Course map](../COURSE_MAP.md)
- [Learner start guide](../learner/START_HERE.md)
- [Learning log](../learner/LEARNING_LOG.md)
- [Instructor guide](../instructor/INSTRUCTOR_GUIDE.md)
- [Architecture](../docs/architecture.md)
- [Testing strategy](../docs/testing-strategy.md)
- [Official references](../references/OFFICIAL_REFERENCES.md)
