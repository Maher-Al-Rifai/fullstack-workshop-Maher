# Module 16: GitHub Actions CI and delivery controls

**Guided effort:** 10 hours  
**Required branch:** `learning/16-github-actions`  
**Phase:** Delivery

## Objectives

- Build a least-privilege pull-request pipeline for backend, frontend, production images, and E2E acceptance.
- Use service containers, caching/build artifacts, concurrency, and failure evidence appropriately.
- Configure required checks and demonstrate a blocked pull request.
- Explain action versioning, untrusted pull-request risk, secrets boundaries, and deployment separation.

## Prerequisites

- Modules 09, 13, 15 complete.
- Ability to push a branch and view workflow logs.

## Concepts and context

CI converts the definition of done into enforced, repeatable checks. Jobs should fail close to the defect and retain enough evidence to diagnose. Parallel backend/frontend jobs improve feedback; production builds and E2E validate integration after focused checks.

Workflow code is privileged automation. Use minimum permissions, avoid exposing secrets to untrusted code, review third-party actions, and prefer immutable action commit pins where organizational policy requires. `pull_request_target` is especially dangerous when combined with checkout/execution of untrusted PR code.

## Step-by-step lab

### 1. Read the workflow as code

Inspect `.github/workflows/ci.yml`. For each job list:

- trigger and concurrency group;
- permissions;
- runner/tool versions;
- dependency installation;
- checks;
- service containers;
- artifacts;
- dependency relationships.

Draw the job DAG.

### 2. Implement backend job

Use PostgreSQL service health, Python 3.13, dependency install, Alembic upgrade, Ruff, Mypy, and Pytest. Keep test secret/local values in workflow environment, not repository production secrets.

Explain why migration against PostgreSQL is separate from fast SQLite-backed TestClient tests.

### 3. Implement frontend job

Use Node 22, install dependencies, lint, typecheck, Vitest, and production Nuxt build. After maintainers commit lockfiles, switch to `npm ci` and cache by lockfile.

### 4. Build production containers

Use Buildx to build backend and frontend production targets. No push is needed on PRs. Use scoped cache where appropriate and ensure the build context excludes credentials/artifacts.

### 5. Run E2E and upload failure evidence

Run `compose.test.yaml`, preserve exit code, collect Compose logs and Playwright artifacts even on failure, then tear down volumes/orphans. Limit artifact retention and review whether traces can contain sensitive data.

### 6. Demonstrate required-check enforcement

Create a deliberate failing test on the module branch, push, and show the PR cannot satisfy merge policy. Inspect logs, restore behavior, push, and show all required checks pass.

With administrator help, configure branch protection/ruleset for:

- PR required;
- required checks;
- review requirement;
- conversation resolution;
- restricted force pushes/deletion;
- optional linear history/signed commits according to policy.

### 7. Review workflow security

Confirm default `contents: read`. Identify where `id-token: write` appears only in deployment. Discuss:

- action major versus commit-SHA pinning;
- Dependabot action updates;
- fork PR secrets;
- untrusted code and cache/artifact poisoning;
- why deploy does not run on every PR;
- GitHub protected production environment.

### 8. Improve failure ergonomics

Add clear job names, step summaries, or test artifacts that make failure ownership obvious. Avoid one giant script with an unreadable log if separate commands provide better diagnosis.

### 9. Compare local and CI definitions

Ensure `make verify` and CI cover the same core gates. Document unavoidable differences (runner architecture, artifact upload, branch policy, cloud identity). A CI-only secret fix should not be required to run ordinary local tests.

## Validation checklist

- [ ] Workflow DAG and job responsibilities are understood.
- [ ] Backend, frontend, image-build, and E2E jobs run with minimum permissions.
- [ ] PostgreSQL migration is validated in CI.
- [ ] E2E failure artifacts are retained and volumes cleaned.
- [ ] A deliberate failure blocks the PR and the corrected commit passes.
- [ ] Branch protection/ruleset is documented or configured.
- [ ] Deployment identity permission is absent from PR CI.
- [ ] Local and CI definitions of done are aligned.

## Independent challenge

Add path-aware change detection without allowing a documentation-only change to bypass repository-structure validation. Explain how required check names remain stable when jobs are skipped.

## Common failure modes

- Giving the workflow write-all permissions.
- Running deployment secrets against untrusted PR code.
- Using `pull_request_target` without understanding its privilege model.
- Hiding all checks in one opaque shell command.
- Making local and CI behavior materially different.

## Evidence to submit

- Workflow DAG.
- Failed and passing workflow links.
- Artifact/trace used to diagnose the failure.
- Branch protection screenshot/config note.
- Security review of permissions and action pinning.

## Commit checkpoint

```text
ci: enforce full-stack pull-request quality gates
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [ci.yml](../.github/workflows/ci.yml)
- [actions](https://docs.github.com/en/actions)
- [about-service-containers](https://docs.github.com/en/actions/using-containerized-services/about-service-containers)
- [security-hardening-for-github-actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
