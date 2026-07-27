# Deployment and rollback runbook

This runbook summarizes the production-style training path. The detailed lab is Module 17 and the infrastructure guide is [../infrastructure/gcp/README.md](../infrastructure/gcp/README.md).

## Preconditions

- disposable billing-enabled Google Cloud project;
- budget alert and named cleanup owner;
- Terraform foundation applied;
- GitHub `production` environment created and optionally protected by approval;
- required repository variables populated from Terraform outputs;
- CI is green on the exact commit/tag;
- migration reviewed for backward/forward compatibility;
- no real user data in the training database.

## Deployment flow

```text
Git tag or manual workflow
→ GitHub OIDC token
→ Google workload identity provider
→ deployer service-account impersonation
→ build backend/frontend images tagged with Git SHA
→ push to Artifact Registry
→ deploy migration image as Cloud Run Job
→ execute migration and wait
→ deploy backend revision
→ discover backend URL
→ deploy frontend revision with runtime API URL
→ restrict backend CORS to frontend origin
→ smoke checks
```

## Why migration precedes service revisions

The migration job is explicit and observable. Application instances do not race to modify the schema at startup. A failed migration prevents new revisions from being deployed.

This order is safe only when the migration remains compatible with currently serving application revisions. Use expand/migrate/contract patterns for destructive changes.

## GitHub variables

```text
GCP_PROJECT_ID
GCP_REGION
GCP_ARTIFACT_REPOSITORY
GCP_CLOUD_SQL_CONNECTION_NAME
GCP_RUNTIME_SERVICE_ACCOUNT
GCP_DEPLOY_SERVICE_ACCOUNT
GCP_WORKLOAD_IDENTITY_PROVIDER
```

The workflow references Secret Manager secret names directly; it does not read their values into GitHub.

## Verification

After deployment:

```bash
curl --fail "$BACKEND_URL/health/live"
curl --fail "$BACKEND_URL/health/ready"
curl --fail "$FRONTEND_URL/api/health"
curl --fail "$FRONTEND_URL/"
```

Then test registration/login/project/task/public page using dedicated training data. Inspect Cloud Run revision logs and confirm no secret values appear.

## Browser session and domain verification

The sample workflow deploys the frontend and backend to independent Cloud Run services. It sets the production refresh cookie to `Secure` and `SameSite=None` and restricts CORS after the frontend URL is known. This does not override browser privacy controls: default service URLs can be treated as cross-site, and some browsers or user policies may block the refresh cookie.

Before production acceptance:

1. choose sibling custom domains, a same-origin gateway/proxy, or a different approved session architecture;
2. record the choice in an ADR;
3. review cookie domain/path/SameSite/Secure flags, CORS, credentials mode, and CSRF assumptions;
4. test login, token refresh after access-token expiry, logout, expired/invalid refresh behavior, and privacy/incognito modes on the actual domains;
5. verify TLS, canonical URLs, and redirect behavior.

Endpoint smoke checks against default Cloud Run URLs prove reachability, not complete browser-session compatibility.

## Rollback decision

Rollback when a new revision causes elevated errors, failed critical journeys, severe latency, security regression, or corrupted behavior and a rapid forward fix is not safer.

### Frontend or backend revision rollback

List revisions:

```bash
gcloud run revisions list \
  --service workboard-api \
  --region "$GCP_REGION" \
  --project "$GCP_PROJECT_ID"
```

Shift traffic:

```bash
GCP_PROJECT_ID=... GCP_REGION=... \
  ./infrastructure/gcp/scripts/rollback.sh workboard-api <known-good-revision>
```

Repeat for `workboard-web` when needed, then run smoke checks.

### Database warning

Application traffic rollback does not automatically reverse a migration. A destructive or incompatible migration may make the previous revision unusable. Prefer forward-compatible migrations and a corrective forward migration. Downgrade only when explicitly tested and data-safe.

## Post-deployment evidence

Record:

- source commit and image tags/digests;
- migration execution name/status;
- backend/frontend revision names;
- service URLs/custom domains;
- smoke-test results;
- error/latency observations;
- operator and timestamp;
- rollback target and decision threshold.

## Cleanup

At the end of a disposable cohort:

1. export only approved learning evidence;
2. remove Cloud Run services/jobs and Artifact Registry images if not Terraform-managed;
3. run the guarded Terraform destroy script;
4. verify Cloud SQL and retained backups are gone as intended;
5. remove GitHub variables/environment access if the repository is archived;
6. review billing until charges stop.
