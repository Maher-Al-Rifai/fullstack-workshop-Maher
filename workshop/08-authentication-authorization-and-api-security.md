# Module 08: Authentication, authorization, and API security

**Guided effort:** 12 hours  
**Required branch:** `learning/08-auth-security`  
**Phase:** Backend

## Objectives

- Hash and verify passwords safely, issue/validate typed access and refresh tokens, and implement current-user dependency.
- Enforce resource authorization for every private operation.
- Configure cookie and CORS behavior by environment and explain limitations.
- Perform a small threat/abuse-case review and add security-focused tests.

## Prerequisites

- Backend project/task workflows available.
- Basic understanding of hashing, cookies, and bearer headers from readings.

## Concepts and context

Passwords must be transformed with a password-hashing function designed to resist guessing; they are not encrypted for later recovery. JWTs are signed claims and are usually readable by the holder. Validate signature, expiry, token type, and subject. A valid token does not authorize every resource.

The reference uses short-lived bearer access tokens in frontend memory and an HTTP-only refresh cookie. This demonstrates boundaries but omits refresh rotation/revocation and several account-security controls. Security work includes recognizing limitations, not presenting a training flow as complete.

## Step-by-step lab

### 1. Implement password storage

Use Argon2 through the approved library. Registration normalizes email, checks uniqueness, hashes the password, and never returns/logs the hash. Login uses a constant-style generic error for unknown email or wrong password.

Inspect one stored row in the disposable database and prove plaintext is absent. Do not include the full hash in public evidence.

### 2. Implement token claims

Access token claims should include subject, issued/expiry times, and a token-type discriminator. Refresh token uses a distinct type and longer expiry. Use a sufficiently long environment-provided signing key and an explicitly allowed algorithm.

Decode functions must reject:

- invalid signature;
- expired token;
- wrong token type;
- missing/invalid subject.

### 3. Implement authentication endpoints

Required:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

Login returns access JSON and sets the refresh cookie. Configure `HttpOnly`, `Secure` in production, path scope, duration, SameSite, and optional domain. Explain which settings change for same-site versus cross-site custom domains.

### 4. Implement current-user dependency

Use FastAPI's OAuth2 bearer helper to extract the access token, decode it as access type, parse subject, load active user, and raise a consistent unauthorized response. Do not perform this manually in every route.

### 5. Audit authorization

Create an authorization matrix for two users across project/task operations. Test each write and at least representative reads. Confirm a user cannot exploit:

- guessed project ID;
- guessed task ID;
- task ID under a different project path;
- public slug to gain write access;
- frontend omission of a button.

### 6. Configure CORS deliberately

Local allowed origin is the exact frontend origin. Explain preflight, allowed methods/headers, credentials, and why CORS is not an API authorization layer. Send an `OPTIONS` request or inspect browser preflight for a non-simple request.

### 7. Add frontend-safe error behavior

Ensure auth errors reveal enough to recover but not user enumeration or stack detail. Check logs do not contain password, bearer token, refresh cookie, or signing key. Request IDs may be logged.

### 8. Security tests

Add tests for:

- password hash not equal to plaintext;
- duplicate registration;
- bad login generic failure;
- access token required;
- refresh token cannot act as access token;
- invalid/expired token;
- inactive/missing user;
- cross-user private project/task denial;
- cookie flags under production-like settings where testable.

### 9. Threat notes

Use `../docs/security.md` to write top abuse cases and mitigations/deferred controls. Include credential stuffing, XSS/token use, stolen refresh cookie, broken object authorization, malicious dependency, and log leakage.

## Validation checklist

- [ ] Passwords are Argon2 hashes and never returned/logged.
- [ ] Access and refresh tokens are type-distinguished and expiry-validated.
- [ ] Refresh cookie flags/path are environment-aware.
- [ ] Every private project/task operation is resource-authorized.
- [ ] Two-user tests prove isolation.
- [ ] CORS uses explicit origins and is not treated as authorization.
- [ ] Known training limitations and production follow-ups are documented.

## Independent challenge

Implement refresh-token rotation with a persisted hashed token identifier, reuse detection, and session revocation design. A design-only ADR is acceptable if implementation is outside cohort scope, but it must cover data model, concurrency, logout, expiry, compromise, and tests.

## Common failure modes

- Using reversible encryption or a fast general-purpose hash for passwords.
- Accepting any valid JWT without checking token type.
- Returning different login messages for unknown user versus wrong password.
- Assuming CORS prevents non-browser attackers.
- Checking project access for reads but not nested task updates/deletes.

## Evidence to submit

- Authentication sequence diagram.
- Cookie attribute evidence with values redacted.
- Two-user authorization matrix and test output.
- Threat/abuse-case table with mitigations and deferred controls.
- Proof plaintext password is absent without exposing the hash.

## Commit checkpoint

```text
feat(auth): secure authentication and resource authorization
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [security.md](../docs/security.md)
- [SECURITY.md](../SECURITY.md)
- [https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [rfc7519.html](https://www.rfc-editor.org/rfc/rfc7519.html)
- [Password_Storage_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [https://owasp.org/www-project-api-security/](https://owasp.org/www-project-api-security/)
- [Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)
- [Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
