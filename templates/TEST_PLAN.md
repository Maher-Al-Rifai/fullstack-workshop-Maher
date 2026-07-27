# Test plan: change or feature

## Risk statement

What failures matter, to whom, and with what impact?

## Test matrix

| Risk/behavior | Layer | Setup | Assertion | Evidence |
|---|---|---|---|---|
| | Unit/API/component/E2E/manual | | | |

## Data and isolation

Describe deterministic fixtures, unique values, cleanup, database engine, and personal-data restrictions.

## Environments

- local component;
- Docker Compose integration;
- CI;
- deployed smoke/exploration.

## Negative and authorization cases

- invalid input;
- missing authentication;
- wrong user/resource;
- expired token;
- unavailable dependency;
- repeated/duplicate action.

## Non-functional checks

Accessibility, performance, logs, secrets, container user, migration duration, rollback, cost.

## Exit criteria

- [ ] Required automated tests pass.
- [ ] Intended mutation causes the expected failure.
- [ ] Manual risks are recorded.
- [ ] Evidence is attached without sensitive data.
