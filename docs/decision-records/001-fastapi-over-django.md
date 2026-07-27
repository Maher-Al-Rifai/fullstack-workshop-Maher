# ADR 001: Use FastAPI for the backend API

- Status: Accepted
- Date: 2026-07-22

## Context

The workshop needs to expose HTTP contracts, validation, dependency injection, authentication, service/repository boundaries, OpenAPI, and API testing directly. Django provides an excellent integrated web platform, but its admin, forms, templating, ORM, sessions, and framework conventions would broaden the course and obscure some API-first boundaries.

## Decision

Use FastAPI with Pydantic, SQLAlchemy, Alembic, and PostgreSQL.

## Consequences

Positive:

- explicit typed request/response schemas;
- generated OpenAPI and interactive documentation;
- direct Pytest/TestClient path;
- small framework surface for tracing requests;
- async capability remains available without requiring it in the baseline.

Negative:

- authentication/admin/content workflows require more explicit implementation;
- architecture conventions must be taught rather than inherited from one integrated framework;
- learners may over-layer simple behavior unless reviewers enforce proportional design.

## Revisit when

A future workshop's primary objective is Django administration, server-rendered forms/content management, or an organization-specific Django codebase.
