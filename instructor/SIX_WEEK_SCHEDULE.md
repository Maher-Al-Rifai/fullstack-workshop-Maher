# Six-week delivery schedule

This schedule assumes approximately 30 workshop hours per week, including review corrections. Adjust scope rather than compressing every gate when the learner needs more time.

## Week 1 — Foundations and reproducibility

**Modules:** 00–04

| Day | Primary work | Mentor focus |
|---|---|---|
| 1 | Orientation, baseline, setup | Establish evidence and escalation habits |
| 2 | Git branches, commits, PR exercise | Commit quality and review response |
| 3 | HTTP, REST, OpenAPI, manual requests | Status codes, contracts, failure semantics |
| 4 | Docker image lab | Layers, process model, non-root user |
| 5 | Compose/network/volume investigation and gate | Learner explanation under failure |

**Week exit:** clean clone works; learner opens a focused PR and diagnoses one container failure.

## Week 2 — API and persistence

**Modules:** 05–06, start 07

| Day | Primary work | Mentor focus |
|---|---|---|
| 6 | FastAPI app, routers, settings, health | Boundaries and dependency injection |
| 7 | Request/response schemas and errors | External contract discipline |
| 8 | Relational model and PostgreSQL | Keys, constraints, transactions |
| 9 | SQLAlchemy repositories and Alembic | Migration repeatability and rollback |
| 10 | Backend gate review | Trace request and rebuild empty DB |

**Week exit:** versioned API starts against PostgreSQL and migrations reproduce schema.

## Week 3 — Domain, security, and backend quality

**Modules:** finish 07, 08–09

| Day | Primary work | Mentor focus |
|---|---|---|
| 11 | Project/task services and repositories | Business rules versus transport/query concerns |
| 12 | Error model and task transition rule | Transaction and domain invariant |
| 13 | Registration/login/token flow | Password storage and token lifecycle |
| 14 | Resource authorization and abuse cases | Ownership checks, CORS, cookie behavior |
| 15 | Pytest layers and backend gate | Meaningful failure, not coverage theater |

**Week exit:** protected project/task API with unit and HTTP tests; learner can distinguish authentication and authorization.

## Week 4 — Frontend and universal rendering

**Modules:** 10–13

| Day | Primary work | Mentor focus |
|---|---|---|
| 16 | Nuxt structure, Vue components, TypeScript | Component contracts and accessible HTML |
| 17 | API client, auth state, middleware | Token refresh, failures, shared state boundary |
| 18 | Projects/tasks UI states | Loading, empty, validation, unauthorized states |
| 19 | SSR public page and metadata | Initial HTML, hydration, crawlability |
| 20 | Vitest and frontend gate | Correct layer and user-observable assertions |

**Week exit:** authenticated UI and public SSR page with meaningful component/API-client tests.

## Week 5 — Integration, acceptance, and CI

**Modules:** 14–16

| Day | Primary work | Mentor focus |
|---|---|---|
| 21 | Compose development stack | DNS, health, volume, environment boundaries |
| 22 | Production image and isolated test stack | Build/run separation and deterministic seed |
| 23 | Playwright API setup and browser journeys | Stable locators and readiness over sleeps |
| 24 | GitHub Actions jobs and artifacts | Required checks, least permissions, diagnosis |
| 25 | Failure drill and delivery gate | Break rule/build/E2E, use evidence to repair |

**Week exit:** `make verify` passes on a clean machine and pull requests are protected by required checks.

## Week 6 — Cloud, operations, and final defense

**Modules:** 17–19

| Day | Primary work | Mentor focus |
|---|---|---|
| 26 | GCP project, budget, IAM, Terraform plan | Identity, cost, destructive actions |
| 27 | Registry, Cloud SQL, secrets, migration job | Runtime/service/deployer boundaries |
| 28 | Cloud Run deployments and smoke tests | Immutable revisions and configuration |
| 29 | Logs, metrics, alert, rollback exercise | Detection, mitigation, verification |
| 30 | Final demonstration and retrospective | Independent explanation and risk judgment |

**Week exit:** deployed, observable solution; rollback demonstrated; handover and rubric completed.

## Scope adjustment rules

When schedule pressure appears, preserve the following:

- authentication **and** authorization;
- migrations and database constraints;
- backend unit/API tests;
- frontend component/API-client tests;
- one complete Playwright journey;
- production image builds;
- CI required checks;
- keyless cloud identity;
- migration job and rollback demonstration.

Reduce optional UI polish, comments, advanced task features, or custom domains before removing engineering gates.
