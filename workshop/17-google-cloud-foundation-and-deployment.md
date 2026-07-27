# Module 17: Google Cloud foundation and deployment

**Guided effort:** 14 hours  
**Required branch:** `learning/17-gcp-deployment`  
**Phase:** Cloud

## Objectives

- Provision Artifact Registry, Cloud SQL, Secret Manager, service accounts, and GitHub workload identity federation with Terraform.
- Build and push immutable images, run migrations as a Cloud Run Job, and deploy separate backend/frontend services.
- Explain deployer versus runtime identity, secret access, Cloud SQL connection, and CORS/runtime configuration.
- Run production smoke checks and record revision/image evidence.

## Prerequisites

- Delivery gate passed and exact commit is green.
- Billing-enabled disposable GCP project and named billing owner.
- gcloud, Terraform, and GitHub environment access.

## Concepts and context

Cloud deployment is an identity and configuration exercise as much as a container exercise. GitHub receives a short-lived OIDC token; Google admits only the configured repository claim; a deployer service account is impersonated; Cloud Run services execute as a separate runtime service account with only Cloud SQL/secret/log permissions.

Images are tagged with Git SHA so a revision can be traced to source. Migrations run as an explicit job before new service revisions. Cloud Run rollback is independent per service, but database compatibility determines whether an old revision remains usable.

## Step-by-step lab

### 1. Establish a safe training project

Confirm project ID, billing account/owner, region, cleanup date, and budget alerts. Never use a production/shared project. Read `../docs/cost-control.md`.

Authenticate human tooling:

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project <project-id>
```

Understand that human ADC is for Terraform/bootstrap, not the GitHub deployment identity.

### 2. Review Terraform before apply

Copy variables:

```bash
cd infrastructure/gcp/terraform
cp terraform.tfvars.example terraform.tfvars
```

Set exact `project_id` and `github_repository`. Review every resource and IAM role. Note that generated secret values are stored in Terraform state; use protected remote state outside disposable training.

### 3. Plan and apply foundation

```bash
../scripts/bootstrap.sh
terraform show workboard.tfplan
terraform apply workboard.tfplan
terraform output
```

Inspect created resources in CLI/console. Confirm Cloud SQL version/region/tier, backups, Artifact Registry, secret names, runtime/deployer accounts, workload pool/provider condition, and IAM bindings.

### 4. Configure GitHub

Create a protected `production` environment. Populate variables from Terraform:

```bash
../scripts/configure-github.sh
```

Verify no service-account key JSON or secret value is stored in GitHub. Inspect OIDC provider attribute condition restricted to the exact repository. A stronger production setup can also restrict branch/environment claims.

### 5. Read the deployment workflow

Trace `.github/workflows/deploy-gcp.yml`:

1. checkout;
2. OIDC auth and service-account impersonation;
3. registry authentication;
4. backend/frontend image build and push using Git SHA;
5. migration job deploy/execute/wait;
6. backend deploy and URL discovery;
7. frontend deploy with runtime API URLs;
8. backend CORS restriction to frontend URL;
9. smoke checks and summary.

Explain every permission and environment variable.

### 6. Trigger deployment

Use manual dispatch first. Watch authentication, build, migration, service deploy, and smoke steps. If IAM propagation causes a transient failure immediately after creation, inspect and retry after confirming configuration rather than adding a key.

### 7. Inspect deployed resources

Record:

```bash
gcloud artifacts docker images list "${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/workboard"
gcloud run services describe workboard-api --region "$GCP_REGION"
gcloud run services describe workboard-web --region "$GCP_REGION"
gcloud run jobs executions list --job workboard-migrate --region "$GCP_REGION"
gcloud sql instances describe workboard-postgres
```

Confirm image tag/source SHA, service account, Cloud SQL attachment, secret references, ports, min/max instances, URLs, and revision names.

### 8. Run smoke and product checks

Use health URLs and a dedicated cloud training account. Create project/task, open public page, and inspect logs. Do not seed known demo passwords into a real shared environment without an explicit training decision.

### 9. Validate browser session and domain topology

The default workflow deploys separate Cloud Run URLs and uses a secure `SameSite=None` refresh cookie. Test whether the target browsers accept refresh behavior on those URLs. CORS success alone is insufficient. For a production-oriented result, design sibling custom domains, a same-origin proxy/gateway, or another approved session architecture. Record cookie domain/path/SameSite/Secure, CORS, CSRF assumptions, TLS/canonical URLs, and privacy-mode test results in an ADR.

### 10. Validate security and cost

- runtime account can read only required secrets;
- deployer does not need secret values;
- service-account keys list is empty/unneeded;
- Cloud Run min instances are zero;
- maximum instances are bounded;
- Cloud SQL tier/backup cost is understood;
- cleanup date is recorded.

## Validation checklist

- [ ] Disposable project, budget owner, alert, and cleanup date are recorded.
- [ ] Terraform plan was reviewed before apply.
- [ ] OIDC provider is restricted to the exact repository and no key JSON is used.
- [ ] Deployer and runtime service accounts have distinct responsibilities.
- [ ] Images are traceable to immutable Git SHA tags.
- [ ] Migration job completes before new service revisions.
- [ ] Backend/frontend run as separate Cloud Run services with secret/Cloud SQL configuration.
- [ ] Browser refresh-cookie behavior is tested on the actual domains or explicitly documented as an incomplete production control.
- [ ] Production smoke/product checks pass and cost sources are known.

## Independent challenge

Harden the Terraform/GitHub trust to restrict deployment to the protected production environment or an exact main/tag claim. Document the GitHub OIDC claims used, CEL condition, failure test, and operational recovery path.

## Common failure modes

- Creating/download a service-account key as the default solution.
- Applying Terraform without reading resource/IAM/cost impact.
- Deploying `latest` with no source traceability.
- Running migrations in every backend instance startup.
- Using wildcard CORS or putting the database URL in Nuxt public config.
- Assuming default Cloud Run URL reachability proves cross-site refresh-cookie compatibility.

## Evidence to submit

- Terraform plan summary and outputs with sensitive values absent.
- OIDC/IAM identity map.
- Successful deployment workflow link.
- Image tag, job execution, and service revision evidence.
- Smoke-test results, domain/session ADR, and cost/cleanup record.

## Commit checkpoint

```text
feat(gcp): provision and deploy immutable full-stack services
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [README.md](../infrastructure/gcp/README.md)
- [deployment.md](../docs/deployment.md)
- [cost-control.md](../docs/cost-control.md)
- [deploying](https://cloud.google.com/run/docs/deploying)
- [mapping-custom-domains](https://cloud.google.com/run/docs/mapping-custom-domains)
- [connect-run](https://cloud.google.com/sql/docs/postgres/connect-run)
- [workload-identity-federation-with-deployment-pipelines](https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines)
- [auth](https://github.com/google-github-actions/auth)
- [Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)
- [Third-party cookies](https://developer.mozilla.org/en-US/docs/Web/Privacy/Guides/Third-party_cookies)
