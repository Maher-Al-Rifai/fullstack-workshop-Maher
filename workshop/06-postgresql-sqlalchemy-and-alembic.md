# Module 06: PostgreSQL, SQLAlchemy, and Alembic

**Guided effort:** 10 hours  
**Required branch:** `learning/06-data-and-migrations`  
**Phase:** Backend

## Objectives

- Model users, projects, memberships, tasks, and comments with intentional keys, constraints, relationships, and nullability.
- Configure SQLAlchemy 2 sessions and repository-friendly models.
- Create, review, apply, downgrade, and validate Alembic migrations.
- Explain transaction boundaries and differences between Pydantic schemas and persistence models.

## Prerequisites

- Module 05 complete.
- Basic relational concepts or completion of the reading in this module.

## Concepts and context

A relational model encodes durable invariants. Primary keys identify rows, foreign keys preserve relationships, unique constraints prevent duplicates, and transactions make multi-write operations atomic. The ORM is a mapping/query tool; it does not remove the need to understand SQL and database behavior.

Alembic migrations are versioned production changes. Autogeneration compares metadata to a database and proposes operations; a human must review intent, existing data, locks, compatibility, and rollback.

## Step-by-step lab

### 1. Design before coding

Read `../docs/database-design.md`. Draw the five entities, cardinality, ownership, optional fields, and delete behavior. For each rule, state whether it belongs in Pydantic, service code, PostgreSQL, or multiple layers.

Required baseline:

- unique user email;
- unique public project slug;
- project owner foreign key;
- unique project membership pair;
- task belongs to project;
- optional assignee and due date;
- controlled status/priority values;
- timestamps.

### 2. Configure engine and sessions

Create an engine from typed settings and a request-scoped session dependency. Understand `autoflush`, `expire_on_commit`, commit, rollback, close, and why one global session is unsafe.

Use PostgreSQL in development. Tests may override the dependency with an isolated engine, but PostgreSQL-specific behavior needs PostgreSQL tests.

### 3. Implement SQLAlchemy models

Use SQLAlchemy 2 typed mappings (`Mapped`, `mapped_column`, relationships). Avoid importing Pydantic schemas into model files. Add explicit cascade behavior and verify database/ORM effects match.

Import every model into the metadata used by Alembic.

### 4. Initialize Alembic

Configure `alembic.ini`, `migrations/env.py`, and target metadata. The database URL should come from settings/environment rather than a committed credential.

Generate the initial revision:

```bash
cd backend
alembic revision --autogenerate -m "initial workboard schema"
```

Review every operation against the design. Check constraint names, enum/string types, nullability, foreign keys, indexes, timestamps, and downgrade order.

### 5. Exercise migration lifecycle on PostgreSQL

```bash
alembic upgrade head
alembic current
alembic history --verbose
alembic downgrade base
alembic upgrade head
alembic check
```

Run this only against the disposable training database. Verify tables with `psql` or SQLAlchemy inspection.

### 6. Add one incremental migration

Do not edit the applied initial migration. Add a small new field or index—such as a task estimate or `(project_id, status)` index—in model metadata, create a new revision, review it, apply/downgrade/reapply it, and document why it exists.

If adding a required column, use a safe staged approach rather than adding `NOT NULL` with no strategy for existing rows.

### 7. Demonstrate a transaction

Implement a small service/repository operation that creates a project and owner membership atomically. Deliberately raise an exception after the first add but before commit; prove neither row persists after rollback. Restore the valid behavior and add a test.

### 8. Inspect generated SQL

Enable SQL echo temporarily or use PostgreSQL logging/SQLAlchemy compilation in a safe environment. Identify select, insert, transaction begin/commit, and potential N+1 relationship access. Disable noisy logging before committing.

## Validation checklist

- [ ] The ER model and implemented relationships agree.
- [ ] An empty PostgreSQL database reaches head using migrations only.
- [ ] The latest incremental revision can be downgraded/reapplied safely in training.
- [ ] `alembic check` reports no model drift.
- [ ] Project plus owner membership is atomic under an injected failure.
- [ ] I can explain schema/model/repository/service responsibilities.
- [ ] No database credential appears in migration files or Git.

## Independent challenge

Add and justify an index for a real list/filter query. Capture `EXPLAIN` output before/after using enough test rows to make the exercise meaningful, and discuss write/storage cost.

## Common failure modes

- Calling `Base.metadata.create_all` as the deployment migration strategy.
- Editing a migration already applied to shared environments.
- Allowing autogenerate output without reviewing data/lock/rollback impact.
- Committing inside every repository method and breaking multi-step atomicity.
- Assuming SQLite proves PostgreSQL behavior.

## Evidence to submit

- ER diagram and rule-placement table.
- Migration review notes and lifecycle transcript.
- Atomic rollback test/result.
- Schema inspection showing constraints.
- Index challenge evidence if completed.

## Commit checkpoint

```text
feat(db): model workboard data and add reviewed migrations
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [database-design.md](../docs/database-design.md)
- [quickstart.html](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [session_transaction.html](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)
- [tutorial.html](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [ddl-constraints.html](https://www.postgresql.org/docs/current/ddl-constraints.html)
