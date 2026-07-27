# Course map

This map defines the canonical order, estimated learner effort, observable output, and gate relationship for the Full-Stack Intern Workshop. Estimates assume an intern who has written small programs but has not independently delivered a full product.

| Module | Topic | Guided hours | Primary artifact | Gate |
|---:|---|---:|---|---|
| 00 | Orientation and definition of done | 2 | Baseline self-assessment and learning log | Foundation |
| 01 | Workstation and repository setup | 3 | Reproducible environment evidence | Foundation |
| 02 | Git, GitHub, branches, and pull requests | 5 | Reviewed practice PR | Foundation |
| 03 | HTTP, REST, JSON, and API contracts | 5 | API contract and manual requests | Foundation |
| 04 | Docker and container fundamentals | 7 | Non-root health-checked image | Foundation |
| 05 | FastAPI application foundation | 8 | Versioned health/status API | Backend |
| 06 | PostgreSQL, SQLAlchemy, and Alembic | 10 | Relational model and reversible migration | Backend |
| 07 | Backend domain architecture and CRUD | 12 | Project/task service workflows | Backend |
| 08 | Authentication, authorization, and API security | 12 | Protected routes and threat notes | Backend |
| 09 | Backend tests and quality gates | 10 | Unit/API/migration evidence | Backend |
| 10 | Nuxt, Vue, and TypeScript foundation | 10 | Routed, accessible UI shell | Frontend |
| 11 | Frontend API integration and state | 12 | Authenticated project/task workflows | Frontend |
| 12 | SSR, SEO, accessibility, and performance | 8 | Server-rendered public project page | Frontend |
| 13 | Frontend unit, component, and API-client tests | 10 | Layered frontend test suite | Frontend |
| 14 | Docker Compose and full-stack integration | 8 | One-command local system | Integration |
| 15 | Playwright API and browser end-to-end tests | 10 | Critical journey evidence | Integration |
| 16 | GitHub Actions CI and delivery controls | 10 | Required passing PR checks | Delivery |
| 17 | Google Cloud foundation and deployment | 14 | Cloud Run services and Cloud SQL | Cloud |
| 18 | Operations, observability, incidents, and rollback | 8 | Dashboard, alert, rollback exercise | Cloud |
| 19 | Final capstone and production readiness | 10 | Demonstration, defense, and handover | Final |

**Expected guided effort:** approximately 174 hours, including implementation, investigation, review corrections, and evidence preparation. A six-week placement usually allocates 25–30 focused hours per week plus mentor review.

## Gate rules

A gate is not passed merely because code exists. The learner must demonstrate repeatability, reasoning, tests, and documentation.

### Foundation gate — modules 00–04

The learner can clone, branch, make a focused commit, open a pull request, explain an HTTP request, build a container, inspect logs, and distinguish image, container, volume, and network.

### Backend gate — modules 05–09

The learner can trace an authenticated request from router through service and repository to PostgreSQL; create and roll back a migration; explain a domain rule; and show unit and API tests that fail for the expected reason when behavior is broken.

### Frontend gate — modules 10–13

The learner can explain SSR and hydration, build accessible components, integrate a typed API client, preserve loading/error/empty states, and choose the correct frontend test layer.

### Integration and delivery gate — modules 14–16

A clean machine can start the stack from documented commands. A pull request cannot merge when quality, build, or acceptance checks fail. Logs and test artifacts are retained for diagnosis.

### Cloud gate — modules 17–18

The learner can deploy by immutable image tag, explain every runtime identity, find logs, observe a failing revision, direct traffic to a previous revision, and identify ongoing cost sources.

### Final gate — module 19

The learner performs the full demonstration without hidden manual corrections and answers architecture, security, testing, failure, and tradeoff questions using evidence.

## Module workflow

For every numbered module:

1. read objectives and prerequisites;
2. create the required branch;
3. complete the lab without copying the reference implementation first;
4. run the specified validations;
5. complete the independent challenge;
6. update `learner/LEARNING_LOG.md` or the learner's own copy;
7. commit using the suggested checkpoint;
8. open a pull request and attach evidence;
9. address review feedback;
10. receive the mentor gate decision.

The detailed six-week calendar is in [instructor/SIX_WEEK_SCHEDULE.md](instructor/SIX_WEEK_SCHEDULE.md).
