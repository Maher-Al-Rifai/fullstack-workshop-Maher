# Module 18 Demo Guide — Operations, Observability, Incidents, and Rollback

## 1. Review the production safety boundary

Show `backend/app/main.py` and `backend/app/core/config.py`:

- Development/test environments can create local tables for fast setup.
- Production does not call `create_all`.
- The deployment workflow runs `alembic upgrade head` as an explicit Cloud Run Job before deploying revisions.

This prevents application startup from silently changing a production schema.

## 2. Establish and record a baseline

Fill `evidence/module-18-baseline.md` using the live training project:

```bash
curl -sf "$BACKEND_URL/health/live"
curl -sf "$BACKEND_URL/health/ready"
curl -sf "$FRONTEND_URL/api/health"
gcloud run revisions list --service workboard-api --region "$GCP_REGION"
gcloud run jobs executions list --job workboard-migrate --region "$GCP_REGION"
```

Record the time window, revision, request/error rate, latency, Cloud SQL health, and migration status.

## 3. Inspect logs without leaking secrets

```bash
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="workboard-api"' --limit=50 --format=json
```

Check that Authorization headers, cookies, passwords, signing keys, and database URLs are absent. Correlate the request using timestamp, revision, and request ID where available.

## 4. Apply the dashboard and alert

From `infrastructure/gcp/terraform`:

```bash
terraform plan
terraform apply
```

In Cloud Monitoring, show:

- backend request count;
- backend p99 latency;
- the 5xx alert condition and five-minute window;
- the runbook link in alert documentation.

Explain that a budget alert is separate from an availability alert, and that an alert needs an owner and response action.

## 5. Deploy a controlled failure

Use a safe training-only change that makes a health or frontend route fail without touching data or secrets. Deploy it through the normal tagged workflow so the image SHA and Cloud Run revision are traceable.

Capture:

- failing revision name;
- failed health response;
- alert/log evidence;
- rollback decision threshold.

Do not deploy this change to a shared or production project.

## 6. Roll back traffic

```bash
gcloud run revisions list --service workboard-api --region "$GCP_REGION"
GCP_PROJECT_ID="$GCP_PROJECT_ID" GCP_REGION="$GCP_REGION" \
  ./infrastructure/gcp/scripts/rollback.sh workboard-api <known-good-revision>
```

For a frontend-only failure, use `workboard-web` as the service. Verify the recovery:

```bash
curl -sf "$BACKEND_URL/health/ready"
curl -sf "$FRONTEND_URL/api/health"
curl -sf "$FRONTEND_URL/"
```

Then perform the critical browser journey: login, protected request, project/task operation, public page, and logout.

## 7. Explain migration rollback risk

Answer these questions in the evidence:

- Did the failed revision run a migration?
- Can the known-good revision read and write the current schema?
- Would a downgrade lose data?
- Is a corrective forward migration safer?
- Which deployment gate prevents incompatible rollback?

## 8. Complete the incident review

Fill `evidence/module-18-incident-review.md` with the source SHA, revision names, timeline, detection, technical cause, mitigation, verification, and corrective actions. Do not include tokens, passwords, cookie values, or database URLs.

## 9. Clean up

After evidence is approved:

```bash
./infrastructure/gcp/scripts/destroy-training-project-resources.sh
gcloud run services list --region "$GCP_REGION"
gcloud sql instances list
gcloud secrets list
gcloud artifacts repositories list --location "$GCP_REGION"
```

Confirm that intended services, jobs, SQL, registry, and secrets are removed, then monitor the billing account.
