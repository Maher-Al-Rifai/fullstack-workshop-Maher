#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="$(cd "$SCRIPT_DIR/../terraform" && pwd)"
cd "$TF_DIR"

read -r -p "Type DESTROY-TRAINING to remove Terraform-managed resources: " answer
[[ "$answer" == "DESTROY-TRAINING" ]] || { echo "Cancelled."; exit 1; }

terraform destroy
