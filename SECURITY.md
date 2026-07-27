# Security policy

## Reporting

Do not open a public issue for a suspected credential exposure, authentication bypass, injection path, dependency exploit, or private-data leak. Report it through the organization's private security channel or GitHub private vulnerability reporting after the repository owner enables it.

Include the affected revision, reproduction conditions, impact, and the minimum evidence required to investigate. Do not include real user data or active credentials.

## Training application scope

Workboard is an educational reference. It demonstrates baseline controls but has not undergone an external penetration test, privacy assessment, compliance certification, performance test, or disaster-recovery certification.

Before using the code for a real service:

- conduct a threat model and abuse-case review;
- choose a production session and token revocation design;
- add rate limiting and account-abuse controls;
- define email verification, password reset, and account recovery;
- define privacy classification, retention, deletion, and audit requirements;
- review CORS, cookie domain, SameSite, custom domains, and TLS termination;
- run dependency, image, secret, and infrastructure scans;
- test backup restoration and migration rollback;
- use least-privilege service-specific IAM and organization policies;
- establish incident ownership and patch response targets.

## Credential rules

- Never commit `.env`, Terraform state, generated `gha-creds-*.json`, Google service-account keys, access tokens, database exports, or browser storage snapshots.
- Use `.env.example` only for non-secret names and local demonstration values.
- Use short-lived GitHub OIDC credentials for deployment.
- Inject production secrets from Secret Manager.
- Rotate a secret immediately when exposure is suspected; deleting it from Git history is not sufficient.

## Supported versions

This workshop is maintained as a whole. Security fixes are applied to the current default branch and the active cohort branch. See [VERSION_MATRIX.md](VERSION_MATRIX.md) for the review date and dependency policy.
