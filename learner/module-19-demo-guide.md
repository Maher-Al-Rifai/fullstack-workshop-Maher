# Module 19 Demo Guide — Final Capstone

## 1. Start from a clean checkout

```bash
git clone <repository-url> workboard-final-demo
cd workboard-final-demo
make setup
make up
make ps
python scripts/validate-starter.py
make verify
```

Show that no `.env`, database volume, `node_modules`, Python cache, or build output was copied from the development checkout.

## 2. Demonstrate the product

Register, sign in, create private and public projects, create a task, move it through valid statuses, attempt an invalid transition, open the public SSR page, and sign out. Explain which route/service/repository/model handles one task-creation request.

## 3. Defend delivery and data decisions

Show the Alembic migration history and explain why migrations run as a Cloud Run Job before revisions. Show CI job dependencies, immutable SHA image tags, artifact retention, OIDC trust, and distinct deployer/runtime roles.

## 4. Demonstrate operations

Use the Module 18 baseline and incident evidence. Query logs without sensitive fields, show the dashboard/alert, identify a revision, run health checks, and explain the rollback command. Before rollback, state the migration compatibility decision.

## 5. Present readiness honestly

Use `docs/production-readiness.md` and `evidence/module-19-risk-register.md` to explain:

- what is ready for workshop-scoped work;
- what remains simplified;
- the top five risks before real users;
- the three highest-value 30-day follow-ups;
- cost drivers and cleanup ownership.

## 6. Final evidence package

Submit the clean-checkout transcript, `make verify` output, CI link, cloud revision/image evidence, operations evidence, completed incident review, risk register, self-assessment, and reviewer questions. Do not claim live-cloud checks that were not executed.
