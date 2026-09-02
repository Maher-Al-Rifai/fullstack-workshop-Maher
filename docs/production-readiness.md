# Production Readiness Review

This training application is a reproducible full-stack reference system, not a claim of commercial production readiness. The status below separates verified repository controls from evidence that requires a live deployment or organizational decision.

## Readiness summary

| Area | Status | Evidence or next gate |
|---|---|---|
| Local reproducibility | Implemented | `README.md`, `Makefile`, Compose health checks |
| API/data architecture | Implemented | `docs/architecture.md`, API schemas, repositories, services |
| Authentication/authorization | Implemented with known gaps | `docs/security.md`; add MFA, recovery, and rate limiting before real users |
| Automated tests | Implemented | Backend tests, Vitest, Playwright, CI workflow |
| Production packaging | Implemented | Multi-stage non-root Docker images |
| CI delivery controls | Implemented | `.github/workflows/ci.yml`, OIDC deploy workflow |
| Cloud foundation | Defined, live evidence pending | Terraform under `infrastructure/gcp/terraform` |
| Operations/rollback | Defined, live evidence pending | `docs/operating-runbook.md`, Module 18 evidence |
| Privacy/compliance | Not assessed | Data classification, retention, residency, and audit review required |

## Release-candidate gate

Before tagging a release candidate, attach evidence for:

- clean working tree and exact source SHA;
- `python scripts/validate-starter.py`;
- `make verify` and `make e2e-test` results;
- clean checkout setup transcript;
- CI workflow link with all required jobs green;
- image SHA/tag and migration execution;
- smoke checks, logs, dashboard, alert, and rollback result;
- completed risk register and self-assessment.

## Known training simplifications

- Default Cloud SQL sizing is cost-oriented and not a production capacity decision.
- Cloud Run default URLs are used for training; browser cookie behavior needs validation with the final domain topology.
- Access tokens are held in frontend memory and refresh uses an HTTP-only cookie; this is not a complete identity platform.
- The CI workflow uses `npm install` until lockfiles are committed.
- Alert policy configuration is a starter signal, not a complete SLO or paging policy.

## Go/no-go decision

**Decision:** pending live cloud evidence and reviewer approval.

A green test suite alone is insufficient. Do not represent this repository as production-ready until the operational, privacy, cost, and identity items above have owners and evidence.
