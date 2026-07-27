#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="$(cd "$SCRIPT_DIR/../terraform" && pwd)"

for command_name in gcloud terraform; do
  command -v "$command_name" >/dev/null 2>&1 || { echo "$command_name is required" >&2; exit 1; }
done

[[ -f "$TF_DIR/terraform.tfvars" ]] || {
  echo "Copy terraform.tfvars.example to terraform.tfvars and fill the required values." >&2
  exit 1
}

cd "$TF_DIR"
PROJECT_ID="$(terraform console <<< 'var.project_id' 2>/dev/null | tr -d '"' || true)"

if [[ -n "$PROJECT_ID" ]]; then
  gcloud config set project "$PROJECT_ID" >/dev/null
fi

gcloud auth application-default print-access-token >/dev/null 2>&1 || {
  echo "Application Default Credentials are missing. Run: gcloud auth application-default login" >&2
  exit 1
}

terraform init
terraform fmt -check -recursive
terraform validate
terraform plan -out=workboard.tfplan

echo
echo "Review the plan above. Apply with:"
echo "  cd $TF_DIR && terraform apply workboard.tfplan"
