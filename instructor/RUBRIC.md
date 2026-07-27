# Assessment rubric

Score each category from 0 to 4, multiply by its weight, and record specific evidence. A score of 3 represents independent work-ready performance for an intern under normal review.

```text
0 — absent, unsafe, or cannot demonstrate
1 — partial result requiring direct step-by-step intervention
2 — functional with notes/review support; explanation has material gaps
3 — independent, correct, testable, and explainable
4 — diagnoses failure, compares tradeoffs, improves maintainability, can teach it
```

| Category | Weight | Critical minimum |
|---|---:|---:|
| Git, collaboration, and change discipline | 8% | 2 |
| HTTP/API contract and backend architecture | 14% | 3 |
| Relational data and migrations | 10% | 3 |
| Authentication, authorization, and security judgment | 12% | 3 |
| Backend test quality | 10% | 3 |
| Frontend implementation and accessibility | 12% | 2 |
| Frontend and E2E test quality | 10% | 3 |
| Docker and local reproducibility | 8% | 3 |
| CI/CD and supply-chain discipline | 6% | 2 |
| Google Cloud deployment and IAM | 5% | 2 |
| Operations, observability, rollback, and cost | 3% | 2 |
| Documentation, explanation, and handover | 2% | 2 |

## Evidence anchors

### Git, collaboration, and change discipline

**3:** focused branches/commits, complete PR evidence, responds constructively to review, no secret material, can resolve a simple conflict.

### HTTP/API and backend architecture

**3:** correct methods/statuses/schemas; routes, services, repositories, and models have explainable responsibilities; domain errors map consistently; dependency injection is used appropriately.

### Relational data and migrations

**3:** keys/constraints/relationships support business invariants; migration builds an empty database and has a reasoned downgrade/forward strategy; learner understands transaction boundaries.

### Security judgment

**3:** passwords are hashed; token/cookie behavior is explainable; protected resources enforce ownership/membership; CORS and secrets are environment-specific; learner identifies missing production controls honestly.

### Test quality

**3:** tests fail for intended regressions, isolate the correct layer, avoid implementation trivia, and include important error/authorization behavior. Learner can explain what remains unproven.

### Frontend implementation

**3:** typed components/pages, resilient loading/error/empty states, keyboard/label/heading semantics, correct state boundary, public page is server-rendered with contextual metadata.

### Docker and reproducibility

**3:** clean clone starts from documented commands; health checks model readiness; production images are multi-stage/non-root; learner diagnoses DNS, port, environment, and volume issues.

### CI/CD and cloud

**3:** required checks run with least permissions, artifacts aid diagnosis, images use immutable SHA tags, deployment uses OIDC, runtime/deployer identities are distinct, migrations are controlled, rollback works.

### Operations and handover

**3:** logs can be correlated, one useful metric/alert is demonstrated, rollback and smoke checks are documented, cost sources and cleanup are understood, risks are explicit.

## Critical failure rules

The learner cannot pass the final gate while any of the following remains:

- a user can access another user's private project/task;
- plaintext or reversibly encrypted passwords are stored;
- real credentials or Terraform state are committed;
- schema changes rely only on automatic table creation without migrations;
- the system cannot start from the documented clean path;
- tests are disabled or weakened to obtain a green pipeline;
- deployment relies on a long-lived Google service-account key without an approved exception;
- the learner cannot identify or execute a rollback path;
- the final result is copied but cannot be explained.

## Suggested overall interpretation

- **85–100:** ready for scoped full-stack tasks with normal code review;
- **70–84:** ready with explicit mentorship in weaker categories;
- **55–69:** partial capability; assign narrower work and a remediation plan;
- **below 55:** workshop objectives not yet demonstrated.

The weighted score never overrides a critical minimum or critical failure.
