# ADR 005: Use memory-held access token and HTTP-only refresh cookie

- Status: Accepted for training reference
- Date: 2026-07-22

## Context

The workshop needs to teach password hashing, bearer authorization, browser cookie security, token expiry, refresh behavior, and frontend state without introducing an external identity provider.

## Decision

Issue a short-lived JWT access token in the login response and keep it in frontend memory. Issue a longer-lived JWT refresh token as an HTTP-only cookie scoped to auth routes. Refresh once after an access-token `401`.

## Consequences

Positive:

- access token is not persisted in local storage;
- learner sees both header and cookie security boundaries;
- API tests and frontend client tests can cover expiry/refresh behavior;
- implementation remains small enough to trace.

Negative:

- refresh tokens lack rotation, revocation, reuse detection, and session inventory;
- logout cannot invalidate an already issued access token;
- XSS can still act as the user while executing in the origin;
- cross-domain cookie/SameSite configuration requires careful production design.

## Production direction

Evaluate managed identity, opaque server sessions, or a complete rotating refresh-token design based on the real threat model and platform. Do not deploy the training flow unchanged merely because it demonstrates the concepts.
