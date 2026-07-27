# Module 07: Backend domain architecture and CRUD

**Guided effort:** 12 hours  
**Required branch:** `learning/07-backend-domain`  
**Phase:** Backend

## Objectives

- Implement project and task workflows through route, schema, service, repository, and model boundaries.
- Enforce business rules and transaction ownership in services.
- Return consistent not-found/conflict responses without leaking private resource existence.
- Build list, create, read, update, and delete behavior with focused tests.

## Prerequisites

- Modules 05–06 complete.
- Database migrations at head.

## Concepts and context

CRUD is not merely four database calls. Each operation has a contract, validation, access scope, business invariant, transaction, response, failure behavior, and operational consequence. Layering is useful when each layer has a distinct reason to change; it is harmful when a trivial operation is wrapped in empty pass-through classes.

The reference rule `backlog → in_progress → done` provides a testable domain invariant. The service should own that rule; the route maps HTTP, and the repository persists the approved change.

## Step-by-step lab

### 1. Define external schemas

Create `ProjectCreate`, `ProjectUpdate`, `ProjectRead`, `TaskCreate`, `TaskUpdate`, and `TaskRead`. Use explicit length/enum/date validation. For updates, distinguish “field omitted” from “set to null” where business behavior requires it.

Do not return password hashes, membership internals, or unrestricted model attributes.

### 2. Implement repositories

Add focused query operations:

- user/project lookup;
- project list visible to a user;
- public project by slug;
- task list scoped to a project;
- task by both project and task ID;
- add/delete/flush operations.

Avoid a generic repository abstraction that hides SQLAlchemy without adding domain value. Use eager loading deliberately when serialization would otherwise cause N+1 queries.

### 3. Implement project service

Required behavior:

- create project with unique slug and owner membership in one transaction;
- list visible projects;
- load a project only when visible;
- update allowed fields with ownership policy;
- delete according to owner policy;
- return public summary only when `is_public` is true.

Test slug collisions and private-public boundary.

### 4. Implement task transition rule

Create a pure function for allowed transitions and unit-test it before wiring persistence. Baseline:

```text
backlog → in_progress
in_progress → done
same-state update may be accepted or treated as no-op consistently
backlog → done is rejected
```

Document whether backward transitions are out of scope or supported.

### 5. Implement task service

For every operation:

1. verify caller can access the parent project;
2. verify task belongs to the path project;
3. apply field/business validation;
4. persist and commit once;
5. return the updated entity or mapped domain error.

Never accept a task ID and update it without parent/resource authorization.

### 6. Add versioned routes

Implement paths documented in `../docs/api-contract.md`. Declare response models and status codes. Keep route functions small enough to read as the HTTP contract.

### 7. Manual contract walkthrough

Use the HTTP example to create/list/update/delete projects and tasks. Exercise invalid transition, unknown ID, and cross-project task ID. Confirm status/body match documentation.

### 8. Add backend tests

At minimum:

- project creation and list;
- unique slug behavior;
- inaccessible project;
- task creation;
- valid two-step transition;
- invalid direct transition;
- task/project mismatch;
- delete behavior.

Mutate the transition function and prove the correct tests fail.

### 9. Review query and transaction behavior

Inspect SQL/logs for one list and one update. Confirm commit happens at service operation boundary and that serialization does not issue unexpected repeated queries.

## Validation checklist

- [ ] Routes match the documented paths, methods, statuses, and schemas.
- [ ] Services contain real business/access/transaction decisions.
- [ ] Repositories contain query mechanics without deciding unrelated policy.
- [ ] Invalid direct task transition returns a stable conflict.
- [ ] A task cannot be addressed through the wrong project path.
- [ ] Slug collision and public/private behavior are tested.
- [ ] One deliberate rule mutation causes targeted tests to fail.

## Independent challenge

Add task filtering by status and priority using the Module 03 proposal. Include validated query parameters, repository query composition, index consideration, frontend-compatible response, tests, and docs.

## Common failure modes

- Putting access checks only in list routes but not update/delete routes.
- Loading task by ID without verifying its parent project.
- Committing in multiple repositories during one operation.
- Creating generic abstractions before repeated behavior exists.
- Returning every model field through automatic serialization.

## Evidence to submit

- Request trace from route to SQL and back.
- Test output including invalid transition and scoped-resource cases.
- SQL/query observation.
- One architecture tradeoff: code kept simple versus extracted.

## Commit checkpoint

```text
feat(api): implement project and task domain workflows
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [api-contract.md](../docs/api-contract.md)
- [architecture.md](../docs/architecture.md)
- [database-design.md](../docs/database-design.md)
- [https://fastapi.tiangolo.com/tutorial/response-model/](https://fastapi.tiangolo.com/tutorial/response-model/)
- [https://docs.sqlalchemy.org/en/20/orm/queryguide/](https://docs.sqlalchemy.org/en/20/orm/queryguide/)
