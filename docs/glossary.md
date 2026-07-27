# Glossary

**API contract** — agreed request, response, status, authentication, and error behavior between systems.

**Artifact Registry** — Google Cloud registry storing container images and other artifacts.

**Authentication** — establishing the identity of a caller.

**Authorization** — deciding whether that identity may perform an action on a resource.

**Build context** — files made available to a Docker build.

**Cloud Run revision** — immutable deployment snapshot of service code and configuration.

**CORS** — browser mechanism controlling cross-origin requests; not a replacement for authorization.

**Database migration** — versioned operation changing schema or data state reproducibly.

**Dependency injection** — supplying a dependency such as database session/current user through a declared boundary.

**Docker Compose** — declarative orchestration for a multi-container local/test application.

**Hydration** — Vue attaching interactive behavior to server-rendered HTML.

**Idempotent** — repeating an operation produces the same intended state without unintended duplicate effects.

**Image** — immutable container filesystem/configuration template.

**JWT** — signed token carrying claims; not encrypted by default.

**Liveness** — whether a process should be restarted.

**OIDC workload identity federation** — exchange of a GitHub-issued identity token for short-lived Google Cloud credentials without a stored service-account key.

**ORM** — object-relational mapping between application objects and relational records.

**Prerendering** — generating HTML during build rather than per request.

**Readiness** — whether an instance should receive traffic, including required dependency checks.

**Repository pattern** — boundary encapsulating persistence/query mechanics.

**Rollback** — returning traffic/configuration to a known-good application revision; not automatically a database rollback.

**SSR** — server-side rendering of HTML for a request.

**Service layer** — application boundary coordinating business rules, authorization, repositories, and transactions.

**Smoke test** — small post-build/deployment check of critical reachability/behavior.

**Terraform state** — sensitive record mapping configuration to real resources; may contain generated secret values.

**Test pyramid** — strategy using many fast focused tests and fewer broad expensive tests.

**Volume** — Docker-managed persistent data independent of a specific container lifecycle.
