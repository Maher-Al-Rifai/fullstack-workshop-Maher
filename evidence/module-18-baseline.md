# Module 18 Baseline Evidence

- Date/time and timezone:
- Project:
- Region:
- Commit/image revision:

## Baseline signals

| Signal | Observation | Window | Source/query |
|---|---|---|---|
| Backend `/health/ready` | | | |
| Frontend `/api/health` | | | |
| Backend 5xx rate | | | |
| Backend p99 latency | | | |
| Cloud Run instances/startup | | | |
| Cloud SQL CPU/storage/connections | | | |
| Migration job status | | | |

## Correlated log query

```bash
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="workboard-api"' --limit=50 --format=json
```

Sensitive fields checked and absent: Authorization, cookies, passwords, signing keys, database URLs.

## Alert decision

- Signal and threshold:
- Observation window:
- User-impact rationale:
- Expected false positives/negatives:
- Notification route and owner:
- First-response runbook: `docs/operating-runbook.md`