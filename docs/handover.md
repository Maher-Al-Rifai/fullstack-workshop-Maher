# Workboard Engineer Handover

## Start here

1. Read `README.md` and `learner/SETUP_CHECKLIST.md`.
2. Run `make setup`, `make up`, and `make ps`.
3. Run `make verify` and `make e2e-test`.
4. Read `docs/architecture.md`, `docs/security.md`, and `docs/api-contract.md`.

## System map

```text
browser -> Nuxt frontend -> FastAPI API -> PostgreSQL
                 |               |
              SSR config      Alembic migrations
```

Backend routes handle HTTP concerns, services own business rules, repositories own queries, Pydantic schemas define external contracts, and SQLAlchemy models define persistence.

## Delivery and cloud

- CI: `.github/workflows/ci.yml`
- Deployment: `.github/workflows/deploy-gcp.yml`
- Terraform: `infrastructure/gcp/terraform/`
- Deployment guide: `docs/deployment.md`
- Cloud setup: `infrastructure/gcp/README.md`
- Operations: `docs/operating-runbook.md`
- Rollback: `infrastructure/gcp/scripts/rollback.sh`

Deployment uses GitHub OIDC and separate deployer/runtime service accounts. Images use the Git SHA. Migrations run as an explicit Cloud Run Job before service revisions.

## Configuration inventory

| Runtime | Configuration | Source |
|---|---|---|
| Backend | `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS` | `.env`/secret references |
| Frontend browser | `NUXT_PUBLIC_API_BASE` | Compose or Cloud Run environment |
| Frontend SSR | `NUXT_API_INTERNAL_BASE` | Compose or Cloud Run environment |
| Cloud deployment | `GCP_*` repository variables | Terraform outputs via `configure-github.sh` |

Never commit `.env`, Terraform variables/state, credentials, tokens, or database URLs.

## Verification and evidence

- Backend: `backend/tests/`, Ruff, mypy, pytest coverage.
- Frontend: `frontend/tests/`, ESLint, Nuxt typecheck, Vitest, build.
- System: `e2e/tests/` and `compose.test.yaml`.
- Operations: `evidence/module-18-baseline.md`, `evidence/module-18-incident-review.md`.
- Final review: `docs/production-readiness.md`, `evidence/module-19-risk-register.md`.

## Known limits and first follow-ups

This is a workshop system. Before real users, address identity hardening, domain/session validation, restore testing, privacy/retention, load testing, alert ownership, supply-chain policy, and Terraform remote state. See the prioritized risk register rather than treating this handover as a production approval.

## Incident response

Start an incident note, identify service/region/revision, check health/logs/latency/Cloud SQL, preserve evidence, and decide whether rollback is safer than a forward fix. Verify health and a critical product journey after mitigation. Check migration compatibility before sending traffic to an older revision.
