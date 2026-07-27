# Google Cloud cost control

Cloud exercises can incur charges. A training project must have a named billing owner and cleanup deadline.

## Primary cost sources

- Cloud SQL instance runtime, storage, backups, and network;
- Cloud Run CPU/memory/request execution and optional minimum instances;
- Artifact Registry storage and data transfer;
- Logging/Monitoring ingestion and retention;
- outbound network traffic;
- retained snapshots, static IPs, or additional resources introduced by learners.

Cloud SQL is usually the dominant always-on training cost because the instance runs even when no requests arrive.

## Before deployment

- use a dedicated project, never a shared production project;
- create a budget and alert thresholds; budgets notify but do not automatically cap usage;
- use one region unless a learning objective requires otherwise;
- keep Cloud Run minimum instances at zero;
- use the smallest acceptable disposable Cloud SQL tier;
- set `deletion_protection = false` only for explicitly disposable training projects;
- record who will destroy resources and on what date.

## During training

- label resources with application/environment/owner where supported;
- do not enable high-volume debug logging indefinitely;
- limit Cloud Run maximum instances;
- inspect billing reports after initial deployment;
- delete failed/unused experimental resources;
- avoid copying large container images repeatedly across regions.

## After training

Run the Terraform destroy workflow, then verify manually:

```bash
gcloud run services list --region "$GCP_REGION"
gcloud run jobs list --region "$GCP_REGION"
gcloud sql instances list
gcloud artifacts repositories list --location "$GCP_REGION"
gcloud secrets list
```

Review billing for delayed charges. Disabling APIs or deleting source code does not necessarily delete billable resources.
