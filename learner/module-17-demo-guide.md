# Module 17 Demo Guide — Google Cloud Foundation and Deployment

## Prerequisites

- GCP project with billing enabled (disposable training project only).
- `gcloud` CLI authenticated: `gcloud auth login && gcloud auth application-default login`.
- `terraform >= 1.10` installed.
- `gh` (GitHub CLI) authenticated.
- CI passing on `main`.

---

## Step 1: Configure Terraform

```bash
cd infrastructure/gcp/terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:
```hcl
project_id        = "your-project-id"
github_repository = "Maher-Al-Rifai/fullstack-workshop-Maher"
region            = "us-central1"
```

---

## Step 2: Plan and review

```bash
cd infrastructure/gcp
./scripts/bootstrap.sh
```

This runs `terraform init`, `fmt -check`, `validate`, and `plan`. Review the plan:

- **Artifact Registry** — `workboard` Docker repository
- **Cloud SQL** — `workboard-postgres` (POSTGRES_17, db-f1-micro)
- **Secret Manager** — `workboard-database-url`, `workboard-secret-key`
- **Service accounts** — `workboard-runtime`, `workboard-deployer`
- **Workload Identity** — pool `workboard-github`, provider `github-repository`
- **IAM bindings** — confirm no overly broad roles

Then apply:

```bash
cd terraform
terraform apply workboard.tfplan
terraform output
```

---

## Step 3: Configure GitHub environment and variables

```bash
cd infrastructure/gcp
./scripts/configure-github.sh
```

This uses `gh variable set` to push all 7 `GCP_*` variables from Terraform output into the repository.

Then on GitHub → Settings → Environments → New environment:
- Name: `production`
- Check: "Required reviewers" (optional for training)
- Confirm the environment exists before triggering deploy

**Verify no secrets were stored** — the GitHub CLI sets variables (not secrets). The Workload Identity token is ephemeral and never stored.

---

## Step 4: Trigger first deployment

Option A — manual dispatch:

```bash
gh workflow run deploy-gcp.yml
```

Option B — version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Watch the deploy workflow on GitHub Actions:

1. CI gate (reuses `ci.yml`) — must pass first
2. OIDC auth → no key stored, short-lived token
3. Image build + push with `$GITHUB_SHA` tag
4. Migration job: `alembic upgrade head`
5. Backend deploy → URL captured
6. Frontend deploy with runtime `NUXT_PUBLIC_API_BASE`
7. CORS update on backend
8. Smoke checks pass
9. Step summary shows live URLs

---

## Step 5: Inspect deployed resources

```bash
export PROJECT_ID=$(terraform -chdir=infrastructure/gcp/terraform output -raw project_id)
export REGION=$(terraform -chdir=infrastructure/gcp/terraform output -raw region)

# Images
gcloud artifacts docker images list "${REGION}-docker.pkg.dev/${PROJECT_ID}/workboard"

# Services
gcloud run services describe workboard-api --region "$REGION"
gcloud run services describe workboard-web --region "$REGION"

# Migration job executions
gcloud run jobs executions list --job workboard-migrate --region "$REGION"

# Database
gcloud sql instances describe workboard-postgres --project "$PROJECT_ID"

# Service account keys (should be empty)
gcloud iam service-accounts keys list \
  --iam-account "workboard-deployer@${PROJECT_ID}.iam.gserviceaccount.com"
```

Confirm for each service: image tag matches `$GITHUB_SHA`, correct service account, Cloud SQL instance attached, secrets mounted by reference (not values).

---

## Step 6: Smoke checks

```bash
BACKEND_URL=$(gcloud run services describe workboard-api --region "$REGION" --format='value(status.url)')
FRONTEND_URL=$(gcloud run services describe workboard-web --region "$REGION" --format='value(status.url)')

curl -sf "${BACKEND_URL}/health/ready" | python -m json.tool
curl -sf "${FRONTEND_URL}/api/health"
curl -sI "${FRONTEND_URL}/" | head -5
```

Open `$FRONTEND_URL` in a browser. Register a new account, create a project, add a task, open the public project page.

---

## Step 7: Validate identity boundaries

Show that:

1. The deployer SA cannot read Secret Manager values:
   ```bash
   # This fails — deployer has no secretmanager.secretAccessor
   gcloud secrets versions access latest \
     --secret workboard-database-url \
     --impersonate-service-account "workboard-deployer@${PROJECT_ID}.iam.gserviceaccount.com"
   ```

2. No service account key files exist:
   ```bash
   gcloud iam service-accounts keys list \
     --iam-account "workboard-runtime@${PROJECT_ID}.iam.gserviceaccount.com"
   # Output: only the auto-managed system key
   ```

---

## Step 8: Rollback demo (if needed)

```bash
# List recent backend revisions
gcloud run revisions list --service workboard-api --region "$REGION"

# Route 100% traffic to a previous revision
gcloud run services update-traffic workboard-api \
  --region "$REGION" \
  --to-revisions workboard-api-00001-xxx=100

# Or use the rollback script
infrastructure/gcp/scripts/rollback.sh
```

---

## Step 9: Cleanup (end of training)

**Run before billing accrues further:**

```bash
infrastructure/gcp/scripts/destroy-training-project-resources.sh
```

Or delete the entire GCP project:

```bash
gcloud projects delete "$PROJECT_ID"
```

---

## Validation checklist

- [ ] `terraform apply` succeeded with no errors
- [ ] All 7 GitHub variables set; no service account key in secrets
- [ ] Deploy workflow ran to completion; step summary shows live URLs
- [ ] `alembic upgrade head` migration job executed successfully
- [ ] Image tags in Artifact Registry match `$GITHUB_SHA`
- [ ] Deployer SA confirmed unable to read secrets
- [ ] Service account keys list is empty
- [ ] Browser session works end-to-end (register → project → task → public page)
- [ ] Training project cleanup scheduled or executed
