# Module 18: Operations, observability, incidents, and rollback

**Guided effort:** 8 hours  
**Required branch:** `learning/18-operations`  
**Phase:** Cloud

## Objectives

- Use health, logs, request/revision context, metrics, and alerts to detect and diagnose failure.
- Create a practical service dashboard/alert and understand signal limitations.
- Deploy a safe failing revision, mitigate by traffic rollback, and verify recovery.
- Write an incident review and distinguish application rollback from database rollback.

## Prerequisites

- Module 17 deployment is healthy.
- Permission to inspect logs/metrics and shift training traffic.

## Concepts and context

Observability is the ability to infer internal state from outputs such as logs, metrics, and traces. It is not the number of dashboards. Useful evidence answers: which users/requests are affected, which service/revision changed, what dependency is failing, and whether mitigation worked.

Rollback is a controlled operational action. Cloud Run can route traffic to a previous revision, but an incompatible migration can prevent old code from functioning. Design expand/contract migrations so application revisions remain reversible.

## Step-by-step lab

### 1. Establish a baseline

Record normal:

- backend/frontend health responses;
- request count/error rate;
- request latency;
- instance count/startup;
- Cloud SQL CPU/storage/connections;
- migration job status.

Use a short, known test window so later failure comparison is meaningful.

### 2. Query structured logs

Use Cloud console or CLI filters by service/revision/severity. Generate one request and correlate it using request ID or timestamp:

```bash
gcloud logging read   'resource.type="cloud_run_revision" AND resource.labels.service_name="workboard-api"'   --limit=50 --format=json
```

Check that logs do not contain Authorization, cookie, password, signing key, or database URL.

### 3. Create a dashboard and alert

Choose signals tied to user impact, such as backend 5xx rate and high latency. Define:

- metric/filter;
- threshold/window;
- why it indicates a problem;
- expected false positives/negatives;
- notification route;
- first-response runbook link.

A budget alert is separate from an availability alert.

### 4. Deploy a controlled failure

Create a safe change such as an intentionally failing backend health/readiness behavior or a frontend route error. Do not corrupt data or expose secrets. Deploy through the normal workflow so revision/source evidence exists.

Observe health, logs, metrics, and user impact. State the rollback decision threshold.

### 5. Roll back traffic

List revisions and choose the known-good one:

```bash
gcloud run revisions list --service workboard-api --region "$GCP_REGION"
GCP_PROJECT_ID="$GCP_PROJECT_ID" GCP_REGION="$GCP_REGION"   ./infrastructure/gcp/scripts/rollback.sh workboard-api <known-good-revision>
```

For a frontend failure, roll back `workboard-web` independently. Run health and product smoke checks after traffic shift.

### 6. Analyze database compatibility

Answer:

- Did the failed deployment run a migration?
- Can the old revision read/write the current schema?
- Would downgrade lose data?
- Is a forward corrective migration safer?
- Which step should prevent an incompatible rollback?

Perform migration downgrade only if the training revision is explicitly reversible and disposable.

### 7. Write an incident review

Use `../templates/INCIDENT_REVIEW.md`. Include detection, timeline, technical cause, contributing factors, mitigation, recovery verification, and corrective actions. Do not blame the learner; focus on controls and conditions.

### 8. Cleanup and cost verification

After the final assessment or instructor approval, destroy training resources with the guarded script. Verify services, jobs, SQL, registry, and secrets are removed as intended and monitor billing.

## Validation checklist

- [ ] Normal baseline and useful log query are recorded.
- [ ] Logs are checked for sensitive-data leakage.
- [ ] Dashboard/alert has a user-impact rationale and runbook.
- [ ] A safe failing revision was deployed through normal delivery.
- [ ] Traffic was rolled back to a named known-good revision.
- [ ] Health and critical product behavior were verified after recovery.
- [ ] Database compatibility implications are explained correctly.
- [ ] Incident review and cleanup/cost evidence are complete.

## Independent challenge

Add a lightweight request-duration or domain metric and alert/SLO proposal. Explain cardinality, privacy, cost, and why the metric improves a decision rather than merely adding data.

## Common failure modes

- Logging entire requests/tokens to make debugging easier.
- Creating alerts with no owner or response action.
- Rolling back application code without checking schema compatibility.
- Increasing resources before identifying the failure.
- Deleting failed revisions/evidence before writing the incident review.

## Evidence to submit

- Baseline signal table.
- Correlated log query with sensitive fields absent.
- Dashboard/alert configuration.
- Failing and recovered revision/traffic evidence.
- Incident review.
- Cleanup and post-destroy resource/billing verification.

## Commit checkpoint

```text
ops: add observability evidence and tested rollback runbook
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [operating-runbook.md](../docs/operating-runbook.md)
- [deployment.md](../docs/deployment.md)
- [INCIDENT_REVIEW.md](../templates/INCIDENT_REVIEW.md)
- [logging](https://cloud.google.com/run/docs/logging)
- [rollouts-rollbacks-traffic-migration](https://cloud.google.com/run/docs/rollouts-rollbacks-traffic-migration)
- [metrics_gcp#gcp-run](https://cloud.google.com/monitoring/api/metrics_gcp#gcp-run)
