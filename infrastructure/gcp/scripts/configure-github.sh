#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="$(cd "$SCRIPT_DIR/../terraform" && pwd)"

command -v gh >/dev/null 2>&1 || { echo "GitHub CLI (gh) is required." >&2; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "Terraform is required." >&2; exit 1; }

gh auth status >/dev/null
cd "$TF_DIR"

gh variable set GCP_PROJECT_ID --body "$(terraform output -raw project_id)"
gh variable set GCP_REGION --body "$(terraform output -raw region)"
gh variable set GCP_ARTIFACT_REPOSITORY --body "$(terraform output -raw artifact_repository)"
gh variable set GCP_CLOUD_SQL_CONNECTION_NAME --body "$(terraform output -raw cloud_sql_connection_name)"
gh variable set GCP_RUNTIME_SERVICE_ACCOUNT --body "$(terraform output -raw runtime_service_account)"
gh variable set GCP_DEPLOY_SERVICE_ACCOUNT --body "$(terraform output -raw deploy_service_account)"
gh variable set GCP_WORKLOAD_IDENTITY_PROVIDER --body "$(terraform output -raw workload_identity_provider)"

echo "GitHub Actions variables configured. Create a protected 'production' environment before deployment."
