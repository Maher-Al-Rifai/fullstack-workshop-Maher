# Publish and operationalize the workshop on GitHub

This guide turns the release archives into maintained repositories. The recommended topology is a private instructor/reference repository plus a separate learner repository.

## 1. Verify the release

Keep the ZIP files and `SHA256SUMS.txt` together. From the download directory:

```bash
sha256sum -c SHA256SUMS.txt
unzip -t fullstack-intern-workshop-complete.zip
unzip -t fullstack-intern-workshop-starter.zip
```

On macOS, `shasum -a 256 -c SHA256SUMS.txt` may be used instead. Do not publish an archive that fails either integrity check.

## 2. Create the instructor/reference repository

```bash
mkdir workshop-reference
unzip fullstack-intern-workshop-complete.zip -d workshop-reference
cd workshop-reference/fullstack-intern-workshop

git init
git add .
git commit -m "chore: publish full-stack workshop reference"
git branch -M main
git remote add origin <private-reference-repository-url>
git push -u origin main
```

Restrict this repository to instructors and maintainers. The completed implementation is an answer key and debugging reference, not the learner's default starting point.

## 3. Create the learner repository

```bash
mkdir workshop-learner
unzip fullstack-intern-workshop-starter.zip -d workshop-learner
cd workshop-learner/fullstack-intern-workshop-starter

git init
git add .
git commit -m "chore: initialize full-stack intern workshop"
git branch -M main
git remote add origin <learner-repository-url>
git push -u origin main
```

Set the learner repository as a template when multiple interns need isolated copies. Do not use a public repository when exercises, names, logs, screenshots, or cloud evidence may contain internal information.

## 4. Replace organization-specific placeholders

Before enrollment, review and update:

- repository name and owner;
- `CODE_OF_CONDUCT.md`, `SECURITY.md`, support and escalation contacts;
- license and copyright policy;
- expected working hours, review service level, and completion dates;
- approved Google Cloud organization/project/region and billing owner;
- data handling, screenshot, logging, and evidence-retention rules;
- assessment accommodations and local workstation constraints.

The reference application name `Workboard` may remain, or it can be rebranded consistently across source, Compose, cloud services, documentation, and tests.

## 5. Generate reproducibility locks on a connected machine

The assembly environment could not resolve external npm or Terraform registries, so lockfiles are intentionally not fabricated. Use the versions in `VERSION_MATRIX.md`, review the resulting dependency graph, and commit the generated files.

```bash
cd frontend
npm install
npm test
npm run typecheck
npm run lint
npm run build

cd ../e2e
npm install
npx playwright install --with-deps
npm test

cd ../infrastructure/gcp/terraform
terraform init
terraform fmt -check -recursive
terraform validate
```

Commit:

```text
frontend/package-lock.json
e2e/package-lock.json
infrastructure/gcp/terraform/.terraform.lock.hcl
```

Then change maintained Dockerfiles and workflows from `npm install` to `npm ci`. Keep the Playwright package version and Playwright container image version identical. Review all generated advisories and transitive changes rather than accepting them mechanically.

The learner starter initially has no Playwright package because that is created during the system-testing modules. Generate its lockfile when the package is introduced.

## 6. Run clean-machine acceptance

Use a workstation with Docker Compose v2:

```bash
cp .env.example .env
make setup
make up
make verify
make clean
```

Repeat from a fresh clone with no existing volumes. Confirm:

- the frontend, API documentation, readiness endpoint, and public SSR page open;
- database migration and deterministic seed complete;
- backend lint/type/tests, frontend lint/type/tests, production image builds, and Playwright pass;
- production images run as non-root;
- no manual database or container correction is required;
- cleanup removes the disposable database and generated test artifacts.

## 7. Configure GitHub repository controls

For `main` in the learner repository:

- require pull requests;
- require at least one reviewer where staffing permits;
- require conversation resolution;
- require the CI status checks appropriate to the current module;
- block force pushes and deletion;
- enable secret scanning/push protection when available;
- enable dependency alerts and review Dependabot configuration;
- limit Actions permissions to read by default;
- require approval for workflows originating from untrusted forks.

At the beginning of the course, starter CI protects only the baseline. Module 16 expands it to the complete backend, frontend, container, and Playwright gates. Do not make a future gate required before the corresponding workflow job exists.

Create labels and milestones from `instructor/PUBLISHING_MODEL.md`. Copy each module's observable acceptance criteria into a GitHub issue and link the learner's pull request and evidence.

## 8. Configure the production environment and keyless cloud identity

Create a protected GitHub environment named `production` with required reviewers. Apply the Terraform foundation only in a disposable billing-enabled project, then run:

```bash
./infrastructure/gcp/scripts/configure-github.sh
```

This creates repository variables for project, region, registry, Cloud SQL connection, runtime/deployer service accounts, and workload identity provider. Do not upload a Google service-account key JSON.

Review the workload identity condition. The baseline restricts admission to the exact repository. A production organization should also evaluate protected environment, branch/tag, organization, and reusable-workflow claims.

## 9. Decide browser and domain topology before representing deployment as production-ready

The sample workflow can deploy frontend and backend to separate default Cloud Run URLs. That is sufficient for infrastructure and API smoke checks, but the refresh token is a secure HTTP-only cookie. Cross-site cookie behavior on unrelated default service URLs can be restricted by browser privacy policy even when `SameSite=None`, `Secure`, and CORS are configured correctly.

Choose and test one production topology:

1. **Shared registrable domain:** for example `app.example.com` and `api.example.com`, with an explicitly reviewed cookie domain, CORS, CSRF, and TLS policy.
2. **Same-origin gateway/proxy:** the browser reaches one origin and a trusted proxy or Nuxt server route forwards API traffic.
3. **External identity/session redesign:** use an approved identity provider and token/session architecture suitable for the organization.

Record the decision as an ADR. Test login, access-token refresh, logout, browser privacy modes, CSRF assumptions, and failure recovery on the actual domains. Default Cloud Run URL success is not a substitute for that test.

## 10. Prove deployment and rollback

Before learner use of cloud modules:

1. run Terraform plan/apply in a disposable project;
2. trigger the deployment workflow from a known commit;
3. record image digests, migration execution, and service revisions;
4. test health, authentication, authorization, public SSR output, and logs;
5. deploy a controlled failing revision;
6. shift traffic to the known-good backend/frontend revisions;
7. verify database compatibility during rollback;
8. destroy the project/resources and confirm billing stops.

## 11. Release acceptance checklist

A cohort release is ready only when all of the following are true:

- [ ] Both archive checksums and ZIP integrity pass.
- [ ] Reference and starter repositories have the intended visibility.
- [ ] Contacts, policy, schedule, and ownership are current.
- [ ] Dependency/provider lockfiles are generated, reviewed, and committed.
- [ ] Clean-clone `make verify` passes on a connected Docker workstation.
- [ ] GitHub branch rules and current-module checks are enforced.
- [ ] A disposable GCP plan, deployment, smoke test, rollback, and cleanup were rehearsed.
- [ ] Domain/cookie/session behavior is tested or explicitly classified as an incomplete production exercise.
- [ ] Budget alert, billing owner, cleanup date, and incident contact are recorded.
- [ ] Instructors have calibrated the rubric against one sample module pull request.
