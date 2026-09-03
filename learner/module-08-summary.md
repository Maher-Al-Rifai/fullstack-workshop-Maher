# Module 08 — Authentication, Authorization & API Security

## Objectives

- Hash and verify passwords safely with Argon2
- Issue and validate typed access and refresh tokens (JWT)
- Implement the `get_current_user` FastAPI dependency for all protected routes
- Enforce per-resource authorization for every private project and task operation
- Configure cookie attributes by environment
- Perform a threat/abuse-case review and add security-focused tests

---

## Files created / modified

| File | Change |
|---|---|
| `backend/pyproject.toml` | Added `argon2-cffi==23.1.0`, `PyJWT==2.10.1` |
| `app/core/security.py` | NEW — Argon2 password hasher |
| `app/core/tokens.py` | NEW — JWT create/decode with type discrimination |
| `app/repositories/user_repository.py` | NEW — get_by_email, get_by_id, add |
| `app/schemas/user.py` | Added `UserRegister`, `LoginRequest`, `TokenResponse` |
| `app/services/auth_service.py` | NEW — register, login, refresh_tokens |
| `app/api/routes/auth.py` | NEW — 5 auth endpoints |
| `app/api/deps.py` | REPLACED stub with real JWT Bearer verification |
| `app/api/router.py` | Registered auth router |
| `tests/conftest.py` | Added `auth_client` fixture (real JWT, no user override) |
| `tests/test_auth.py` | NEW — 15 security tests |
| `.env` | Added `SECRET_KEY` development value |

---

## Step 1 — Password storage (`app/core/security.py`)

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_ph = PasswordHasher()

def hash_password(plaintext: str) -> str:
    return _ph.hash(plaintext)

def verify_password(plaintext: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, plaintext)
    except VerifyMismatchError:
        return False
```

**Why Argon2?** It is the winner of the Password Hashing Competition and is designed to be expensive to brute-force — it costs time and memory. Fast general-purpose hashes (MD5, SHA-256) are unsuitable for passwords because they can be reversed with GPU-scale brute-force attacks.

**What is stored in the database?** The Argon2 string with embedded parameters, salt, and derived key:
```
$argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>
```
The plaintext password is never stored or logged.

---

## Step 2 — Token design (`app/core/tokens.py`)

```python
_ACCESS_TYPE = "access"
_REFRESH_TYPE = "refresh"

def create_access_token(user_id: int) -> str:
    payload = {"sub": str(user_id), "exp": expire, "type": _ACCESS_TYPE}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")
```

**Token type discriminator:** Every JWT includes `"type": "access"` or `"type": "refresh"`. The decode functions reject the wrong type — a refresh token cannot be used where an access token is expected and vice versa.

**Validation chain** in `_decode()`:
1. Signature valid (wrong key → rejected)
2. Not expired (`exp` claim)
3. Correct token type (`type` claim)
4. Subject present and parseable (`sub` claim)

**JWTs are not encrypted.** Any holder can base64-decode the payload and read the claims. Never put sensitive data (password hash, email, PII) in a JWT payload.

---

## Step 3 — Authentication endpoints (`app/api/routes/auth.py`)

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/v1/auth/register` | POST | None | Create account, return `UserRead` |
| `/api/v1/auth/login` | POST | None | Return access token + set refresh cookie |
| `/api/v1/auth/refresh` | POST | Cookie | Issue new access token from refresh cookie |
| `/api/v1/auth/logout` | POST | None | Delete refresh cookie |
| `/api/v1/auth/me` | GET | Bearer | Return current user profile |

**Refresh cookie attributes:**

```python
response.set_cookie(
    key="refresh_token",
    httponly=True,                                    # JS cannot read it
    secure=settings.environment == "production",      # HTTPS only in prod
    samesite="lax",
    max_age=settings.refresh_token_expire_days * 86400,
    path="/api/v1/auth",                              # not sent on every request
)
```

`path="/api/v1/auth"` scopes the cookie so it is only sent to auth endpoints, not every API call. `HttpOnly` prevents JavaScript from reading it even if XSS occurs.

---

## Step 4 — `get_current_user` dependency (`app/api/deps.py`)

```python
_bearer = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Bearer token required")
    user_id = decode_access_token(credentials.credentials)
    user = user_repository.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")
    return user
```

`HTTPBearer` extracts the token from the `Authorization: Bearer <token>` header. Every protected route declares `Depends(get_current_user)` — auth logic is defined once, not repeated in every route. In tests, `app.dependency_overrides[get_current_user] = lambda: owner` completely bypasses the JWT check.

---

## Step 5 — Auth service (`app/services/auth_service.py`)

**User enumeration prevention:**
```python
def login(db, email, password):
    user = user_repository.get_by_email(db, email.lower().strip())
    # Same message whether email does not exist or password is wrong
    if not user or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid credentials")
```

Returning different messages for "unknown email" vs "wrong password" lets an attacker enumerate which emails are registered. The identical response prevents this.

---

## Step 6 — Authorization matrix

| Operation | Owner | Member | Other | Unauthenticated |
|---|---|---|---|---|
| `GET /projects/public/{slug}` | ✅ | ✅ | ✅ | ✅ |
| `GET /projects` | ✅ (own+member) | ✅ (own+member) | ❌ (empty) | 401 |
| `POST /projects` | ✅ | ✅ | ✅ | 401 |
| `GET /projects/{id}` (private) | ✅ | ✅ | 404 | 401 |
| `PATCH /projects/{id}` | ✅ | 403 | 404 | 401 |
| `DELETE /projects/{id}` | ✅ | 403 | 404 | 401 |
| `GET/POST /projects/{id}/tasks` | ✅ | ✅ | 404 | 401 |
| `PATCH/DELETE .../tasks/{id}` | ✅ | ✅ | 404 | 401 |

**Why 404 instead of 403 for private projects?** A 403 response confirms the resource exists. A non-member receives 404 so private project existence is never revealed.

---

## Step 7 — CORS (already configured in Module 05)

CORS is configured in `main.py` with `allow_origins=settings.cors_origins`. Key points:
- **CORS is not an authorization layer.** It only controls which browser origins can make requests. Non-browser clients (curl, Postman, attackers) are not restricted by CORS at all.
- `allow_credentials=True` requires an explicit origin list — `allow_origins=["*"]` is disallowed with credentials.
- The `Secure` cookie flag and HTTPS enforce transport-layer security. CORS does not.

---

## Threat notes

| Abuse case | Mitigation in this implementation | Deferred / limitation |
|---|---|---|
| Credential stuffing (bulk guessing) | Generic error, Argon2 cost | Rate limiting, CAPTCHA, lockout not implemented |
| XSS token theft | Access token in memory only; refresh cookie is `HttpOnly` | CSP headers not set |
| Stolen refresh cookie | Scoped to `/api/v1/auth` path, `HttpOnly` | No rotation or revocation |
| Broken object authorization | Every service checks project visibility before acting | — |
| Token replay after logout | Logout deletes the cookie | Access token remains valid until expiry (no revocation list) |
| Log leakage | Generic error messages surfaced to callers | Ensure no request logger captures `Authorization` headers |
| Malicious dependency | Lock exact versions in `pyproject.toml` | No SBOM or automated CVE scanning |

**Known training limitations:** No refresh-token rotation, no server-side revocation, no email verification, no MFA, no lockout, no breach-password check. Do not claim this session design is production-complete.

---

## Test results

```
46 passed in 4.28s — ruff check: All checks passed — ruff format: clean
```

| Test file | Count | What it covers |
|---|---|---|
| `test_auth.py` | 15 | Registration, hash proof, duplicate 409, login, user enumeration prevention, bearer required, valid token, expired token, wrong token type, refresh, cross-user isolation |
| `test_projects.py` | 8 | Project CRUD + visibility + 403 ownership |
| `test_tasks.py` | 11 | Transition rules + task CRUD |
| Others | 12 | Exceptions, health, status, service |

---

## Key concepts

| Concept | Detail |
|---|---|
| **Password hashing** | Argon2id — slow by design, salted, parameterized. Never encrypt, never store plaintext. |
| **JWT type discriminator** | `"type": "access"` / `"type": "refresh"` prevents token confusion attacks |
| **User enumeration** | Identical error and response time for unknown email vs wrong password |
| **HTTP-only cookie** | Refresh token in `HttpOnly` cookie — readable by the server, not by JavaScript |
| **Cookie path scoping** | `path="/api/v1/auth"` — cookie is only sent to auth routes, not leaked on every request |
| **CORS ≠ authorization** | CORS restricts browser origins; it does not protect server-side resources |
| **Dependency override in tests** | `app.dependency_overrides[get_current_user]` bypasses JWT for unit/integration tests; `auth_client` fixture uses the real implementation |
