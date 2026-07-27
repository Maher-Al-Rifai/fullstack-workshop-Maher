# Google Cloud deployment kit

This directory provisions the shared cloud foundation for the Workboard workshop and connects GitHub Actions to Google Cloud with short-lived OpenID Connect credentials. The application remains two independently deployable containers: a FastAPI backend and a Nuxt frontend. PostgreSQL runs in Cloud SQL.

> **Cost warning:** Cloud SQL is normally the largest continuously billed resource in this training design. Use a dedicated training project, assign a billing owner, set a budget alert, choose a cleanup date, and destroy resources after assessment. Review [cost-control.md](../../docs/cost-control.md) before applying Terraform.

## What Terraform creates

- required Google Cloud APIs;
- one regional Artifact Registry Docker repository;
- one PostgreSQL 17 Cloud SQL instance, database, and application user;
- Secret Manager secrets for `DATABASE_URL` and `SECRET_KEY`;
- a least-privilege Cloud Run runtime service account;
- a GitHub deployment service account;
- a Workload Identity Pool and provider restricted to the configured GitHub repository;
- IAM bindings needed by the runtime and deployment identities.

Cloud Run services and the migration job are created or updated by `.github/workflows/deploy-gcp.yml`, because their image tags are produced by the delivery pipeline.

## Prerequisites

Install and authenticate:

```bash
gcloud --version
terraform version
gh --version

gcloud auth login
gcloud auth application-default login
gh auth login
```

You also need:

- a Google Cloud project with billing enabled;
- permission to enable services, create IAM resources, Cloud SQL, secrets, and Artifact Registry;
- a GitHub repository in exact `owner/name` form;
- a protected GitHub environment named `production` before the first deployment.

## 1. Select a dedicated project

```bash
export GCP_PROJECT_ID="your-training-project"
gcloud config set project "$GCP_PROJECT_ID"
gcloud billing projects describe "$GCP_PROJECT_ID"
```

Confirm that the displayed project is disposable training infrastructure rather than an unrelated shared or production project.

## 2. Configure Terraform variables

```bash
cd infrastructure/gcp/terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
project_id        = "your-training-project"
region            = "us-central1"
github_repository = "your-github-owner/fullstack-intern-workshop"

# Low-cost training defaults; perform a separate production sizing exercise.
database_tier       = "db-f1-micro"
deletion_protection = false
```

Do not commit `terraform.tfvars`, state files, or plan files. Terraform state contains sensitive values even when output is marked sensitive elsewhere. For team use, configure an approved encrypted remote backend before applying.

## 3. Initialize, validate, and review the plan

From the repository root:

```bash
./infrastructure/gcp/scripts/bootstrap.sh
```

The script verifies credentials, initializes providers, formats and validates configuration, and writes `workboard.tfplan`. Inspect the complete plan before applying:

```bash
cd infrastructure/gcp/terraform
terraform show workboard.tfplan
terraform apply workboard.tfplan
```

Cloud SQL creation can take several minutes. A successful apply is not proof that the application is deployed; it only creates the foundation and identity path.

## 4. Configure GitHub Actions variables

From the repository root:

```bash
./infrastructure/gcp/scripts/configure-github.sh
```

The script writes these repository variables from Terraform outputs:

- `GCP_PROJECT_ID`
- `GCP_REGION`
- `GCP_ARTIFACT_REPOSITORY`
- `GCP_CLOUD_SQL_CONNECTION_NAME`
- `GCP_RUNTIME_SERVICE_ACCOUNT`
- `GCP_DEPLOY_SERVICE_ACCOUNT`
- `GCP_WORKLOAD_IDENTITY_PROVIDER`

No long-lived Google Cloud service-account key is required or expected.

Create a GitHub environment called `production` and add the appropriate required reviewers. Protect `main`, require the CI workflow, disallow force pushes, and require pull requests. The workflow has explicit `id-token: write` permission only in the deployment job.

## 5. Prepare the application repository

Before enabling deployment:

```bash
cp .env.example .env
make verify
```

Also complete these repository hygiene tasks:

- generate and commit `frontend/package-lock.json` and `e2e/package-lock.json` with the approved Node/npm version;
- verify production image builds use the same dependency lock;
- update ownership, support, and security contacts;
- review regional data, backup, retention, IAM, and network requirements;
- replace training-cost defaults when the environment is not disposable.

## 6. Run the first deployment

Use **Actions → Deploy to Google Cloud → Run workflow**, or create an approved version tag such as `v1.0.0`. The deployment workflow first reuses the complete CI workflow, so the tagged commit must pass backend, frontend, container, and Playwright gates before cloud credentials are requested.

The workflow performs the following sequence:

1. executes the complete CI workflow;
2. exchanges the GitHub OIDC token for short-lived Google Cloud credentials;
3. builds backend and frontend images tagged with the immutable Git commit SHA;
4. pushes both images to Artifact Registry;
5. creates or updates a Cloud Run migration job and executes `alembic upgrade head`;
6. deploys the backend service with Cloud SQL and Secret Manager bindings;
7. deploys the frontend service with the backend URL;
8. updates backend CORS to the resulting frontend origin;
9. runs smoke checks against live and ready health endpoints and the rendered homepage.

Review the workflow summary and retain the deployed revision names.


### Browser session and domain topology

The example workflow initially uses two default Cloud Run URLs and configures the refresh cookie as `Secure` with `SameSite=None`. This is useful for deployment exercises and endpoint smoke checks, but browsers may restrict a refresh cookie when the frontend and backend are treated as different sites. CORS success does not guarantee that cross-site cookies will be accepted.

Before calling the deployment production-ready, choose and test a domain/session topology:

- sibling custom domains under one reviewed registrable domain, such as `app.example.com` and `api.example.com`;
- a same-origin gateway or Nuxt server proxy for browser API calls; or
- an approved external identity/session design.

Record cookie domain/path/SameSite/Secure settings, CORS origins, CSRF assumptions, TLS ownership, logout/refresh tests, and browser privacy-mode results in an ADR. See [PUBLISH_TO_GITHUB.md](../../PUBLISH_TO_GITHUB.md).

## 7. Verify production behavior

```bash
gcloud run services list --region "$GCP_REGION" --project "$GCP_PROJECT_ID"
gcloud run revisions list --service workboard-api --region "$GCP_REGION" --project "$GCP_PROJECT_ID"
gcloud run revisions list --service workboard-web --region "$GCP_REGION" --project "$GCP_PROJECT_ID"
```

Then validate:

- backend `/health/live` returns success;
- backend `/health/ready` reaches Cloud SQL;
- frontend `/` renders;
- a public project page contains its title in initial HTML;
- registration, login, a protected API request, and logout work;
- an unauthorized cross-user request is denied;
- logs contain request IDs but not tokens, passwords, or database credentials.

Record results in the deployment evidence template described in Module 17.

## 8. Roll back safely

List revisions and select a known-good revision:

```bash
export GCP_PROJECT_ID="your-training-project"
export GCP_REGION="us-central1"
gcloud run revisions list \
  --service workboard-backend \
  --project "$GCP_PROJECT_ID" \
  --region "$GCP_REGION"
```

Shift traffic:

```bash
./infrastructure/gcp/scripts/rollback.sh workboard-api workboard-api-00001-abc
```

Repeat for the frontend when required, then run smoke tests immediately. A container rollback does **not** reverse a destructive database migration. Production migrations must be backward-compatible or have a separately rehearsed data recovery plan.

## 9. Destroy disposable training resources

Export required evidence first. Then:

```bash
./infrastructure/gcp/scripts/destroy-training-project-resources.sh
```

After Terraform destruction, confirm that no manually created services, images, secrets, logs sinks, DNS records, or billing resources remain. Deleting the dedicated project is the clearest cleanup for an isolated training environment, subject to organizational policy.

## Production-hardening exercises

The supplied configuration is deliberately understandable rather than a universal production baseline. Before representing it as production-ready, assess and implement as applicable:

- remote encrypted Terraform state with locking and restricted access;
- branch or GitHub-environment claims in the Workload Identity Provider condition;
- private service networking and controlled egress;
- Cloud Armor, a load balancer, custom domains, and certificate strategy;
- Cloud SQL regional availability, production sizing, backups, PITR, and restore drills;
- separate projects for development, staging, and production;
- image vulnerability policy, provenance, signing, and retention;
- alert policies, service-level objectives, audit-log retention, and incident ownership;
- data classification, residency, privacy, and disaster-recovery requirements.

## Authoritative reading

Use [the official-reference catalog](../../references/OFFICIAL_REFERENCES.md), especially the sections for Cloud Run containers and jobs, Cloud SQL connections, Secret Manager, Artifact Registry, Workload Identity Federation, GitHub OIDC, and Terraform provider resources.
