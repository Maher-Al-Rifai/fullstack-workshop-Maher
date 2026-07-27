# Operating runbook

## Service inventory

| Service | Purpose | Health | Dependency |
|---|---|---|---|
| `workboard-web` | Nuxt SSR/UI | `/api/health` | backend for data pages |
| `workboard-api` | FastAPI/API | `/health/live`, `/health/ready` | Cloud SQL, secrets |
| `workboard-migrate` | Alembic execution | job status | Cloud SQL, secrets |
| Cloud SQL | durable PostgreSQL | managed metrics | storage/network |

## First response to an alert

1. Confirm user impact and start an incident note.
2. Identify service, region, revision, and change window.
3. Check readiness, error rate, latency, instance count, and database health.
4. Correlate logs with revision and request ID.
5. Decide whether to mitigate by rollback, traffic shift, scaling limit, or disabling a feature.
6. Run smoke checks after mitigation.
7. Preserve evidence without exposing secrets/personal data.
8. Communicate status and next update according to organization policy.

## Useful local commands

```bash
make ps
make logs
docker compose exec backend alembic current
docker compose exec db psql -U workboard -d workboard
```

## Useful cloud commands

```bash
gcloud run services list --region "$GCP_REGION"
gcloud run revisions list --service workboard-api --region "$GCP_REGION"
gcloud run jobs executions list --job workboard-migrate --region "$GCP_REGION"
gcloud sql instances describe workboard-postgres
gcloud logging read 'resource.type="cloud_run_revision"' --limit=100
```

## Baseline signals

- backend 5xx response count/rate;
- backend request latency percentiles;
- container startup failures;
- instance count and concurrency;
- readiness failures;
- Cloud SQL CPU, memory, disk, connection count, and storage;
- migration job failures;
- frontend SSR 5xx and latency;
- authentication failure rate, interpreted carefully to avoid alerting on normal invalid input.

## Rollback

Follow [deployment.md](deployment.md). Verify database compatibility before directing old application code to the current schema.

## Incident review

Use [../templates/INCIDENT_REVIEW.md](../templates/INCIDENT_REVIEW.md). Focus on system conditions and detection/response improvements rather than blame.
