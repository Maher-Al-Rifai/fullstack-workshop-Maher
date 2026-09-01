# Module 17 Summary — Google Cloud Foundation and Deployment

## What was built

The full cloud infrastructure definition (Terraform) and deployment automation (GitHub Actions) for running Workboard on Google Cloud Run backed by Cloud SQL PostgreSQL. Alembic was also scaffolded to enable controlled production database migrations.

## Alembic setup (new — required by migration job)

| File | Purpose |
|---|---|
| `backend/alembic.ini` | Alembic config; `script_location = migrations` |
| `backend/migrations/env.py` | Connects Alembic to `get_settings().database_url` and all ORM models |
| `backend/migrations/script.py.mako` | Template for generated migration files |
| `backend/migrations/versions/0001_initial_schema.py` | Creates `users`, `projects`, `tasks` tables + enum types |

The deploy workflow's migration job runs `alembic upgrade head` inside the backend production image. This is idempotent and safe to repeat.

## Infrastructure: `infrastructure/gcp/terraform/`

| File | What it provisions |
|---|---|
| `main.tf` | Enables required GCP APIs, creates Artifact Registry |
| `database.tf` | Cloud SQL PostgreSQL 17, DB user with random password |
| `secrets.tf` | Secret Manager secrets: `DATABASE_URL`, `SECRET_KEY` |
| `iam.tf` | Two service accounts + IAM bindings |
| `github-oidc.tf` | Workload Identity Federation pool/provider |
| `outputs.tf` | All values needed for GitHub variables |
| `variables.tf` | `project_id`, `region`, `github_repository` (required) |
| `versions.tf` | Terraform >= 1.10, google provider ~> 7.x |

## Identity model

```
GitHub Actions token (OIDC)
  │  attribute_condition: assertion.repository == '<owner>/<repo>'
  ▼
Workload Identity Pool
  │  roles/iam.workloadIdentityUser
  ▼
deployer service account   (roles: artifactregistry.writer, run.admin)
  │  roles/iam.serviceAccountUser
  ▼
runtime service account    (roles: cloudsql.client, secretmanager.secretAccessor, logging/monitoring)
```

**Deployer** builds and pushes images, runs migrations, deploys services — never reads secrets.  
**Runtime** is the Cloud Run execution identity — reads secrets, connects to Cloud SQL, writes logs.  
No service account key JSON is stored anywhere.

## Deployment workflow: `.github/workflows/deploy-gcp.yml`

Triggered on `push` to version tags (`v*`) or `workflow_dispatch`. Job sequence:

1. CI gate via `workflow_call` (reuses `ci.yml`)
2. OIDC auth → short-lived token → impersonate deployer SA
3. `docker build --target production` + `docker push` (tagged with `$GITHUB_SHA`)
4. `gcloud run jobs deploy/execute workboard-migrate` — runs `alembic upgrade head`
5. Deploy backend → capture URL
6. Deploy frontend with `NUXT_PUBLIC_API_BASE=$BACKEND_URL/api/v1`
7. Update backend `CORS_ORIGINS` to exact frontend URL
8. Smoke checks: `/health/ready`, `/api/health`, `/`
9. Step summary with URLs and image SHA

## Cloud Run configuration

| Setting | Backend | Frontend |
|---|---|---|
| Port | 8000 | 3000 |
| CPU/Memory | 1 / 512Mi | 1 / 512Mi |
| Min instances | 0 (scale-to-zero) | 0 |
| Max instances | 5 | 5 |
| Auth | `--allow-unauthenticated` | `--allow-unauthenticated` |
| Cloud SQL | via `--set-cloudsql-instances` | — |
| Secrets | DATABASE_URL, SECRET_KEY | — |

## Provisioning steps (requires GCP project + billing)

```bash
# 1. Authenticate
gcloud auth login
gcloud auth application-default login

# 2. Configure Terraform
cd infrastructure/gcp/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit: set project_id and github_repository

# 3. Plan and review
../scripts/bootstrap.sh
terraform show workboard.tfplan   # read every resource and IAM binding

# 4. Apply
terraform apply workboard.tfplan
terraform output

# 5. Configure GitHub
../scripts/configure-github.sh    # sets 7 GCP_* repository variables via gh CLI
# Also: create protected 'production' environment in GitHub Settings

# 6. Trigger deployment
gh workflow run deploy-gcp.yml
# or push a version tag: git tag v0.1.0 && git push origin v0.1.0
```

## Security checklist

- [ ] `terraform.tfvars` is git-ignored — never committed
- [ ] No service account key JSON in GitHub secrets
- [ ] OIDC condition restricted to exact `github_repository` value
- [ ] Runtime SA cannot deploy; deployer SA cannot read secrets
- [ ] `deletion_protection = false` only for disposable training project
- [ ] Budget alert configured in GCP Billing console
- [ ] Training project cleaned up after course with `destroy-training-project-resources.sh`

## Files changed

| File | Change |
|---|---|
| `backend/pyproject.toml` | Added `alembic>=1.13.0` dependency |
| `backend/alembic.ini` | New — Alembic configuration |
| `backend/migrations/env.py` | New — connects Alembic to ORM settings |
| `backend/migrations/script.py.mako` | New — migration file template |
| `backend/migrations/versions/0001_initial_schema.py` | New — initial migration |
| `.github/workflows/ci.yml` | Schema step now uses `alembic upgrade head` |

All Terraform and deploy workflow files were already complete (pre-scaffolded).
