# Module 18 Summary — Operations, Observability, Incidents, and Rollback

## What was completed

- Added an `environment` setting and limited `Base.metadata.create_all` to non-production environments.
- Production remains migration-controlled through the Cloud Run migration job (`alembic upgrade head`).
- Added a Terraform Cloud Monitoring dashboard for backend request count and p99 latency.
- Added a Terraform alert policy for elevated backend 5xx responses with an operating-runbook link.
- Added baseline evidence and incident-review templates under `evidence/`.
- Confirmed the existing rollback script shifts 100% of traffic to a named Cloud Run revision.
- Existing runbooks document sensitive-log checks, database compatibility, cleanup, and cost verification.

## Operational model

```text
health + logs + metrics + revision context
                  |
                  v
          detect and diagnose
                  |
                  v
       mitigate: traffic rollback
                  |
                  v
     health + product smoke verification
```

## Monitoring resources

`infrastructure/gcp/terraform/monitoring.tf` defines:

- **Dashboard:** request rate and p99 latency for `workboard-api` Cloud Run revisions.
- **Alert:** backend 5xx request rate above zero for five minutes.
- **Alert documentation:** directs the operator to inspect revision, readiness, logs, latency, and Cloud SQL before rollback.

The alert is intentionally simple for training. A production policy should add notification channels, an owner, an SLO-based threshold, and a tested paging route.

## Rollback procedure

```bash
gcloud run revisions list --service workboard-api --region "$GCP_REGION"
GCP_PROJECT_ID="$GCP_PROJECT_ID" GCP_REGION="$GCP_REGION" \
  ./infrastructure/gcp/scripts/rollback.sh workboard-api <known-good-revision>
```

Repeat independently for `workboard-web` when the frontend is the affected service. Verify `/health/ready`, `/api/health`, the homepage, login, and a protected product journey after the traffic shift.

## Database compatibility rule

Traffic rollback changes application code, not the database schema. The deployment runs migrations before new revisions, so migrations must use expand/contract compatibility. A destructive migration can make an old revision unusable; prefer a corrective forward migration and use `downgrade` only when explicitly tested and data-safe.

## Evidence

- `evidence/module-18-baseline.md` records normal health, error, latency, instance, database, and migration signals.
- `evidence/module-18-incident-review.md` records detection, timeline, cause, mitigation, recovery, and corrective actions.
- `docs/operating-runbook.md` remains the first-response runbook.
- `docs/deployment.md` contains the deployment and rollback decision procedure.

## Live-cloud items

The dashboard/alert Terraform plan, safe failing revision, traffic rollback, production smoke checks, and cleanup verification require the deployed GCP training project from Module 17. They should be recorded in the evidence templates after execution, not simulated locally.
