# Module 19: Final capstone and production readiness

**Guided effort:** 10 hours  
**Required branch:** `learning/19-final-readiness`  
**Phase:** Final

## Objectives

- Reproduce, demonstrate, trace, test, deploy, observe, and roll back the product independently.
- Defend architecture, security, testing, data, delivery, and operations decisions with evidence.
- Identify simplifications and risks honestly and propose prioritized production follow-ups.
- Deliver a complete handover suitable for another engineer to operate and extend.

## Prerequisites

- All previous module work complete or formally waived.
- Clean local verification and healthy cloud deployment.
- Learning log, runbooks, and evidence organized.

## Concepts and context

The final assessment evaluates integrated judgment. You are not expected to claim the training application is a finished commercial platform. You are expected to know exactly what it proves, what it does not prove, how it fails, and how another engineer can reproduce and operate it.

Production readiness is context-specific. A passing capstone has reproducible delivery, protected data/access boundaries, meaningful tests, observable runtime behavior, controlled migration/deployment, and explicit remaining risks.

## Step-by-step lab

### 1. Freeze the candidate revision

Create a release candidate from a green reviewed commit. Record source SHA and ensure no uncommitted local correction is required:

```bash
git status
git rev-parse HEAD
python scripts/validate-starter.py
./scripts/check-secrets.sh
make verify
```

Tag/release only through the instructor's policy.

### 2. Rehearse from a clean checkout

Use a new directory or machine and perform the exact setup path. Do not copy `.env`, database volume, node modules, Python cache, or build artifacts from the development checkout.

Record hidden prerequisites and fix documentation before the assessment.

### 3. Complete the formal demonstration

Follow `../learner/FINAL_DEMO.md`. The reviewer may change the order, ask you to break a rule, choose a different request to trace, or request a rollback without step-by-step prompting.

### 4. Prepare architecture defense

Be ready to explain:

- FastAPI instead of Django for this objective;
- Nuxt instead of a client-only Vue SPA;
- monorepo but separate deployables;
- PostgreSQL and migrations;
- service/repository boundaries;
- memory access token and refresh cookie limitations;
- Cloud Run instead of Kubernetes;
- Cloud Run Job for migrations;
- OIDC/deployer/runtime identities.

For each, name an alternative and condition that would change the decision.

### 5. Prepare risk register

Rank at least ten follow-ups by impact and urgency across:

- account recovery/MFA/refresh rotation/rate limiting;
- privacy/retention/audit;
- database HA, restore test, connection capacity;
- performance/load testing;
- security headers/CSP/scanning/SBOM/signing;
- tracing/alerts/SLO/on-call;
- custom domains/TLS/cookie policy;
- frontend runtime validation/generated client;
- product roles/invitations/comments;
- infrastructure state/organization policy.

State owner, next evidence, and whether it blocks real users.

### 6. Assemble handover

The repository must point clearly to:

- quick start and commands;
- architecture/ADRs;
- API and database design;
- tests and current evidence;
- environment/configuration inventory;
- migration/deploy/rollback runbooks;
- security model and known limitations;
- cloud cost/cleanup;
- incident review;
- open risk register.

Another engineer should not require private verbal steps.

### 7. Self-assess and compare

Complete `../learner/SELF_ASSESSMENT.md` before seeing the final rubric score. Compare Module 00 baseline with current evidence. Identify one area ready for independent work and one that still needs supervision.

### 8. Retrospective and cleanup

Discuss which module created the most transferable capability, which instruction was unclear, and which reference should be improved. Complete cloud cleanup according to the instructor schedule and confirm billing ownership.

## Validation checklist

- [ ] Release candidate is a clean reviewed SHA and `make verify` passes.
- [ ] A new checkout reproduces the product without hidden artifacts.
- [ ] I complete the full demo and request trace independently.
- [ ] I can defend major decisions and state alternatives/revisit conditions.
- [ ] Risk register contains prioritized owners/evidence, not a generic wishlist.
- [ ] Handover contains complete local, CI, cloud, security, and rollback paths.
- [ ] Self-assessment is evidence-based and identifies remaining supervision needs.
- [ ] Cloud cleanup and cost ownership are confirmed.

## Independent challenge

Propose a 30-day post-workshop improvement roadmap limited to three deliverables. Each deliverable must state user/risk outcome, architecture impact, acceptance evidence, rollout/rollback, and why it outranks other follow-ups.

## Common failure modes

- Claiming production readiness because automated tests are green.
- Hiding unexecuted checks or unresolved risks.
- Demonstrating from a dirty checkout with cached state.
- Listing dozens of follow-ups with no priority/owner/evidence.
- Treating final slides as a substitute for operating the real system.

## Evidence to submit

- Clean-checkout transcript and final `make verify` result.
- Final demo recording/notes and reviewer questions.
- Architecture decision defense summary.
- Prioritized production risk register.
- Complete handover index.
- Self-assessment and 30-day roadmap.

## Commit checkpoint

```text
docs(release): complete capstone handover and readiness review
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [FINAL_DEMO.md](../learner/FINAL_DEMO.md)
- [SELF_ASSESSMENT.md](../learner/SELF_ASSESSMENT.md)
- [RUBRIC.md](../instructor/RUBRIC.md)
- [architecture.md](../docs/architecture.md)
- [security.md](../docs/security.md)
- [framework](https://cloud.google.com/architecture/framework)
- [ssdf](https://csrc.nist.gov/Projects/ssdf)
