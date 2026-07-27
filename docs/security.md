# Security model and training threat notes

## Assets

- user credentials and password hashes;
- access and refresh tokens;
- private project/task content;
- database credentials and signing key;
- cloud deployment identity;
- source, CI artifacts, logs, backups, and Terraform state.

## Trust boundaries

```text
Untrusted browser input
  → public Nuxt service
  → public FastAPI service
  → authenticated/authorized application operation
  → database and managed secrets

GitHub workflow token
  → Google workload identity provider restricted to repository
  → deployer service-account impersonation
  → Cloud Run/Artifact Registry control plane
```

Every boundary must validate identity, input, authorization, and data exposure appropriate to that layer.

## Authentication design

- Passwords are hashed with Argon2 through `argon2-cffi`.
- Login returns a short-lived JWT access token.
- The frontend stores the access token in memory, reducing persistent browser exposure.
- The refresh token is an HTTP-only cookie scoped to the auth path.
- Production sets `Secure`; SameSite and domain must be reviewed with the chosen frontend/backend domains. Separate default Cloud Run URLs may be treated as cross-site, and browser privacy policy can block refresh cookies despite correct CORS.

### Known training limitations

- refresh tokens are not rotated;
- there is no server-side revocation list or device/session inventory;
- logout cannot revoke an existing access token before expiry;
- there is no email verification, password reset, breach-password check, MFA, lockout, or anti-automation layer.

Do not claim the reference session design is sufficient for every production risk.

## Authorization

Authentication answers “who is calling?” Authorization answers “may this identity act on this resource?”

Every project/task operation scopes access to ownership or membership. The service must check the actual parent project; trusting a frontend-hidden button or an identifier in a token is insufficient.

Tests should include two users and demonstrate that one cannot read, update, or delete the other's private resource.

## Input and output

- Pydantic validates types, lengths, enums, email, and optional fields.
- SQLAlchemy uses parameterized statements; do not interpolate raw input into SQL.
- Vue escapes text interpolation by default; avoid untrusted `v-html`.
- Error responses should not expose stack traces, SQL, keys, or existence of private resources.
- Logs should include request/revision context but not passwords, bearer tokens, cookies, or full sensitive bodies.

## Browser controls

- Configure explicit production CORS origins; credentials plus wildcard origins are unsafe/incompatible.
- Use HTTPS and secure cookies.
- Add reviewed security headers at the service/proxy layer: HSTS, content-type options, frame policy, referrer policy, permissions policy, and a tested Content Security Policy.
- Protect state-changing cookie-authenticated endpoints against CSRF if the design evolves beyond the current bearer-access-token pattern.
- Review XSS impact because any script executing in the origin can use in-memory access tokens and call APIs as the user.

## Secrets

- Local demonstration values live in untracked `.env`.
- Production database URL and signing key live in Secret Manager.
- Runtime service account receives accessor permission only for required secrets.
- Deployment uses GitHub OIDC federation and short-lived impersonation.
- Terraform-generated secret values are present in Terraform state; use encrypted, access-controlled remote state for non-disposable environments.

Run `./scripts/check-secrets.sh` as a basic local guard and add a dedicated scanner such as GitHub secret scanning or an approved organizational tool.

## Containers and supply chain

- production stages run as non-root;
- build dependencies are not copied into final frontend image;
- dependencies and base images should be locked/reviewed before a cohort;
- CI builds production images before merge;
- deploys use Git SHA tags;
- a mature pipeline should pin actions to reviewed commit SHAs, generate SBOM/provenance, scan images, sign artifacts, and enforce deployment policy.

## Cloud IAM

Identities:

- **GitHub OIDC principal:** admitted only for the configured `owner/repository` claim;
- **deployer service account:** writes images, administers Cloud Run, and may act as runtime account;
- **runtime service account:** connects to Cloud SQL, reads two secrets, writes logs/metrics;
- **human learner/operator:** should use named accounts and least-privilege roles, not shared owner credentials.

Production organizations should further restrict branch/environment claims, use GitHub protected environments, approval rules, organization policies, and audit-log review.

## Abuse cases to discuss

- credential stuffing against login;
- automated account creation;
- ID enumeration and broken object-level authorization;
- malicious project/task text rendered publicly;
- stolen refresh cookie;
- compromised dependency or GitHub Action;
- malicious pull request attempting OIDC deployment;
- database connection exhaustion through autoscaling;
- log injection or sensitive data in error output;
- migration that deletes data before application rollback.

## Security acceptance evidence

The learner should demonstrate:

- password hash differs from plaintext;
- unauthenticated and cross-user resource requests fail;
- invalid/expired token path;
- production containers are non-root;
- secrets are absent from Git and image history;
- OIDC provider condition and service-account role mapping;
- one documented limitation and production mitigation.
