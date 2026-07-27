# Final demonstration script

The final demonstration is a controlled production-readiness review, not a slide presentation. Use a clean checkout or a clean machine whenever possible. The mentor may choose any item below and ask for an explanation or intentional failure.

## 1. Reproduce the local system

```bash
git clone <repository-url> workboard-final-demo
cd workboard-final-demo
make setup
make up
make ps
```

Demonstrate:

- healthy database, backend, and frontend;
- frontend home page and API documentation;
- deterministic seeded account and public project;
- where runtime configuration enters each container.

## 2. Demonstrate the product journey

1. Register a new user.
2. Sign in.
3. Create a private project.
4. Create a public project.
5. Add a task with priority and due date.
6. Move the task through allowed statuses.
7. attempt an invalid transition and explain the response;
8. open the public project page and inspect the delivered HTML metadata;
9. sign out and demonstrate protected-route behavior.

## 3. Trace one request

Choose task creation and trace:

```text
Nuxt page/component
→ frontend API client
→ HTTP request
→ FastAPI router and dependency
→ authentication/authorization
→ service rule
→ repository query
→ SQLAlchemy model/PostgreSQL transaction
→ response schema
→ rendered UI state
```

Explain where each concern belongs and why.

## 4. Defend the data model and migration path

- show the entity relationships and constraints;
- apply migrations to an empty database;
- show the current revision;
- downgrade and upgrade the latest safe training migration;
- explain how a destructive production migration would be staged.

## 5. Prove quality gates

Run:

```bash
make verify
```

Then choose one backend rule and one frontend state:

- break each intentionally;
- show the correct test failure;
- restore the implementation;
- show the checks pass.

Explain why each test belongs at its layer and what it does not prove.

## 6. Inspect production packaging

- show final image stages and non-root users;
- explain build-time versus runtime configuration;
- inspect image history and size;
- explain health checks, shutdown, volumes, and statelessness;
- identify what must never be baked into an image.

## 7. Demonstrate delivery controls

- open or show a pull request with required checks;
- explain concurrency and artifact retention;
- identify the immutable image tag;
- explain the GitHub OIDC trust condition and deployed service accounts;
- explain why a service-account key is not stored in GitHub.

## 8. Operate the cloud deployment

- show frontend and backend Cloud Run revisions;
- show Cloud SQL connection and Secret Manager references without revealing values;
- query logs using a request ID or revision;
- show one metric and alert policy;
- deploy a harmless change;
- run smoke checks;
- shift traffic to the previous revision;
- verify recovery.

## 9. Present production-readiness assessment

State clearly:

- what is ready;
- what is intentionally simplified for training;
- top five risks before real users;
- the next security, reliability, performance, privacy, and product steps;
- current cloud cost drivers and cleanup plan.

## Required handover artifacts

- architecture and API documentation;
- migration history;
- test strategy and recent evidence;
- environment/configuration inventory;
- deployment and rollback runbook;
- operations and incident notes;
- open risks and deferred decisions;
- learning log and self-assessment.
