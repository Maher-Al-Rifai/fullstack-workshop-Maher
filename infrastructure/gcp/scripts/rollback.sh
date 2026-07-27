#!/usr/bin/env bash
set -euo pipefail

SERVICE="${1:-}"
REVISION="${2:-}"
REGION="${GCP_REGION:-us-central1}"
PROJECT="${GCP_PROJECT_ID:-}"

[[ -n "$SERVICE" && -n "$REVISION" && -n "$PROJECT" ]] || {
  echo "Usage: GCP_PROJECT_ID=... GCP_REGION=... $0 <service> <revision>" >&2
  exit 1
}

gcloud run services update-traffic "$SERVICE" \
  --project "$PROJECT" \
  --region "$REGION" \
  --to-revisions "$REVISION=100"

echo "Traffic for $SERVICE now points to $REVISION. Run smoke tests immediately."
