# Contributing

## Branch and pull-request model

Create focused branches from the current base:

```text
feature/<short-outcome>
fix/<short-problem>
docs/<short-topic>
chore/<maintenance-topic>
```

Keep pull requests small enough for a reviewer to understand the behavior, risks, and evidence in one session. Do not mix framework upgrades, broad formatting, and product behavior in the same change.

## Commit style

Use an imperative conventional prefix:

```text
feat(api): create project endpoint
fix(web): preserve return route after refresh
 test(api): reject invalid task transition
docs(course): clarify migration rollback exercise
chore(ci): update supported action major
```

A commit should describe one coherent change. Never include `.env`, credentials, service-account keys, local database files, test videos containing personal data, or generated cloud state.

## Definition of done

Before requesting review:

```bash
python scripts/validate-repository.py
./scripts/check-secrets.sh
make verify
```

When Docker is unavailable, run the host-specific component checks and state clearly which container and integration checks remain unexecuted.

Every behavioral change needs:

- an explanation of the user or engineering outcome;
- tests at the lowest useful layer;
- updated API, architecture, operating, or learner documentation where applicable;
- migration and rollback notes for schema changes;
- security and privacy consideration;
- evidence in the pull-request template.

## Review expectations

Reviewers evaluate correctness, clarity, contracts, failure behavior, authorization, migration safety, test meaning, operations, and course impact—not only style.

Resolve feedback with new commits while review is active. Squash only according to the repository's merge policy. Do not dismiss a failed check by weakening the quality gate without a documented decision.
