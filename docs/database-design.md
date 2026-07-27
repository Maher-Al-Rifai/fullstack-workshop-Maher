# Database design

## Entity relationship overview

```mermaid
erDiagram
  USERS ||--o{ PROJECTS : owns
  USERS ||--o{ PROJECT_MEMBERS : joins
  PROJECTS ||--o{ PROJECT_MEMBERS : includes
  PROJECTS ||--o{ TASKS : contains
  USERS ||--o{ TASKS : assigned
  TASKS ||--o{ COMMENTS : has
  USERS ||--o{ COMMENTS : writes

  USERS {
    bigint id PK
    varchar email UK
    varchar full_name
    varchar password_hash
    boolean is_active
    timestamptz created_at
    timestamptz updated_at
  }
  PROJECTS {
    bigint id PK
    varchar name
    varchar slug UK
    text description
    boolean is_public
    bigint owner_id FK
    timestamptz created_at
    timestamptz updated_at
  }
  PROJECT_MEMBERS {
    bigint project_id PK_FK
    bigint user_id PK_FK
    varchar role
  }
  TASKS {
    bigint id PK
    bigint project_id FK
    varchar title
    text description
    varchar status
    varchar priority
    bigint assignee_id FK_NULL
    date due_date
    timestamptz created_at
    timestamptz updated_at
  }
  COMMENTS {
    bigint id PK
    bigint task_id FK
    bigint author_id FK
    text body
    timestamptz created_at
  }
```

The current UI/API exercises projects and tasks. Membership and comments are modeled to support extensions and relational discussion without forcing every feature into the core six-week scope.

## Design decisions

### Surrogate integer identifiers

Integer primary keys keep the training queries and relationships easy to inspect. A public production API may prefer opaque UUID/ULID identifiers to reduce enumeration and merge concerns. Authorization must never rely on identifiers being hard to guess.

### Unique normalized email

Email is unique. The service normalizes it before lookup/insert. PostgreSQL case-insensitive uniqueness could alternatively use `citext` or a functional unique index; the baseline keeps migrations portable and explicit.

### Unique project slug

Public URLs use a unique slug generated from the project name. Collisions receive a suffix. The slug is not an authorization mechanism; only `is_public` controls unauthenticated visibility.

### Project membership association

`project_members` uses a composite key (`project_id`, `user_id`) so the same user cannot be added twice. The role field can evolve from owner/member to more granular permissions.

### Enum-like values

The reference maps Python enum values to persisted string values. Migrations must be reviewed carefully when adding/removing statuses because historical rows and rolling revisions may use older values.

### Timestamps

Creation/update timestamps are stored with timezone semantics. Applications should display in user context while keeping storage and logs in UTC.

## Constraints and business rules

Place a rule at the strongest practical layer:

- **Pydantic:** shape, required fields, length, date/type parsing;
- **service:** task workflow transition, project access, owner-only destructive action;
- **database:** primary/foreign/unique constraints, non-null state, referential integrity;
- **frontend:** immediate user guidance, never the only enforcement.

A rule may be represented in multiple layers for different purposes. Frontend validation improves feedback; backend validation/security remains authoritative.

## Transaction boundaries

A service operation should commit a complete business change or roll it back. Project creation, for example, includes both the project and owner membership. Do not commit halfway and then attempt another related write in a separate uncoordinated transaction.

Repository methods may add/flush entities, while the service decides when the application operation commits. Keep this convention consistent.

## Migrations

The initial migration creates the complete reference schema. Learner modules should add a small field/index/change in a new revision rather than editing an already-applied migration.

Core commands:

```bash
cd backend
alembic current
alembic history
alembic revision --autogenerate -m "add task estimate"
alembic upgrade head
alembic downgrade -1
alembic check
```

Autogeneration proposes a migration; it does not understand business intent. Review types, nullability, defaults, index operations, foreign keys, data backfills, downgrade safety, and lock duration.

## Safe production change pattern

For a new required field:

1. add it nullable or with a safe server/database default;
2. deploy code that can read old and new rows;
3. backfill in controlled batches;
4. verify completeness and performance;
5. add the non-null constraint in a later migration;
6. remove compatibility code later.

Do not combine a destructive rename/drop with an application revision that immediately assumes the old shape is gone when old instances may still serve traffic.

## Indexing exercise

Candidate indexes should follow observed query patterns, not be added to every column. Examples:

- project membership lookup by user and project;
- task listing by project/status;
- public project lookup by slug (already unique/indexed);
- due-date queries for active tasks.

Use `EXPLAIN (ANALYZE, BUFFERS)` only with safe test data and understand that an index speeds some reads while increasing write/storage cost.

## Backup and restore

Cloud SQL automated backup and point-in-time recovery settings are enabled in the training Terraform. This is not proven recovery. A production readiness exercise must restore into a separate instance, verify schema/application behavior, measure recovery time, and document data-loss tolerance.
