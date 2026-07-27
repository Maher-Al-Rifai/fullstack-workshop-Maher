# ADR 003: Use one repository with two production deployables

- Status: Accepted
- Date: 2026-07-22

## Context

The course should be simple to clone and review while teaching independent frontend/backend build and deployment boundaries.

## Decision

Use a monorepo containing backend, frontend, E2E, infrastructure, and course materials. Build separate backend and frontend production containers and deploy them as separate Cloud Run services.

## Consequences

Positive:

- one pull request can update API contract, client, tests, and documentation atomically;
- one Compose project creates the local product;
- course navigation and CI are easier for an intern;
- frontend/backend can scale and roll back independently in production.

Negative:

- CI needs path-awareness if repository size grows;
- repository permissions cannot easily hide only the reference branch;
- coordinated releases may encourage unnecessary coupling unless contracts remain explicit.

## Rejected alternative

One combined production container was rejected because it hides service boundaries and couples process lifecycle, scaling, configuration, and rollback.
