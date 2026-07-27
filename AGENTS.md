# Instructions for coding agents

## Purpose

This repository is both executable software and a curriculum. A change can be technically correct while damaging a learner objective, command sequence, assessment gate, or instructor workflow.

## Required behavior

Before editing:

1. read the relevant workshop module and architecture decision records;
2. identify whether the change affects the reference solution, starter snapshot, course text, CI, or cloud runbooks;
3. preserve frontend/backend deployment separation and API versioning;
4. do not introduce secrets or generated cloud state;
5. prefer explicit, teachable code over abstraction that exists only to reduce line count.

After editing:

- update tests and affected documentation;
- run `python scripts/validate-repository.py`;
- run the narrow component tests, then `make verify` where Docker is available;
- record any validation that could not be executed;
- do not silently weaken lint, type, coverage, migration, or deployment gates.

## Architectural constraints

- FastAPI routes handle HTTP concerns; services own business rules; repositories own query mechanics.
- Pydantic schemas define external contracts; SQLAlchemy models are persistence structures.
- Database changes require Alembic migrations.
- Nuxt pages compose features; reusable API behavior belongs in services/composables; shared authenticated state belongs in Pinia only when necessary.
- Public SEO pages must remain server-renderable without authenticated browser state.
- Production images run as non-root users.
- CI/CD uses workload identity federation, not stored Google Cloud key JSON.
