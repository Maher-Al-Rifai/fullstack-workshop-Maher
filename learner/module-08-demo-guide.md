# Module 08 — Authentication Demo Guide
## What to open and show the lead

---

## 1. Open the new file structure

Navigate to `backend/app/` and point out what was added:

```
app/
├── core/
│   ├── security.py    ← NEW — Argon2 password hasher
│   └── tokens.py      ← NEW — JWT create/decode with type discrimination
├── repositories/
│   └── user_repository.py  ← NEW
├── schemas/
│   └── user.py        ← EXTENDED — added UserRegister, LoginRequest, TokenResponse
├── services/
│   └── auth_service.py  ← NEW — register, login, refresh_tokens
└── api/
    ├── deps.py        ← REPLACED stub with real HTTPBearer verification
    └── routes/
        └── auth.py    ← NEW — 5 endpoints
```

---

## 2. Open `backend/app/core/security.py`

**What to point out:**

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

**What to say:**
- "Argon2 is the winner of the Password Hashing Competition. It is slow and memory-intensive by design — brute-forcing a 10,000-entry list takes much longer than with SHA-256."
- "The hash looks like: `$argon2id$v=19$m=65536,t=3,p=4$<salt>$<key>` — the salt and algorithm parameters are embedded in the string. We never need to store the salt separately."
- "We never encrypt passwords. Encryption is reversible. Hashing is one-way — if the database is breached, attackers cannot recover the plaintext password."

---

## 3. Open `backend/app/core/tokens.py`

**What to point out — the type discriminator:**

```python
_ACCESS_TYPE = "access"
_REFRESH_TYPE = "refresh"

def create_access_token(user_id: int) -> str:
    payload = {"sub": str(user_id), "exp": expire, "type": _ACCESS_TYPE}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")
```

**What to say:**
- "Every JWT includes `'type': 'access'` or `'type': 'refresh'`. The decode function rejects the wrong type — a refresh token cannot be used as an access token."
- "JWT payloads are NOT encrypted — they are base64 encoded. Anyone who holds the token can read the claims. Never put sensitive data in the payload — only the user ID as `sub`."

**Point to the decode validation chain:**
```python
def _decode(token, expected_type):
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    # 1. Signature check — wrong key raises InvalidTokenError
    # 2. Expiry check — expired raises ExpiredSignatureError
    if payload.get("type") != expected_type:    # 3. Type check
        raise UnauthorizedError("Wrong token type")
    if not payload.get("sub"):                  # 4. Subject check
        raise UnauthorizedError("Invalid token subject")
```

---

## 4. Open `backend/app/services/auth_service.py`

**Point to the user enumeration prevention in `login`:**

```python
def login(db, email, password):
    user = user_repository.get_by_email(db, email.lower().strip())
    # Generic error regardless of whether email exists — prevents user enumeration
    if not user or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid credentials")
```

**What to say:**
- "If we returned `'Email not found'` for unknown emails and `'Wrong password'` for bad passwords, an attacker could build a list of registered emails. The identical response prevents this."
- "Email is normalised to lowercase before storage and lookup — `User@Example.COM` and `user@example.com` are the same account."

---

## 5. Open `backend/app/api/routes/auth.py`

**Point to the refresh cookie setup:**

```python
def _set_refresh_cookie(response, token):
    response.set_cookie(
        key="refresh_token",
        httponly=True,                                      # JS cannot read it
        secure=settings.environment == "production",        # HTTPS only in prod
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/v1/auth",                                # scoped — not sent on every request
    )
```

**What to say:**
- "`HttpOnly`: even if an XSS attack runs JavaScript in the user's browser, it cannot read this cookie — the browser only sends it to the server."
- "`path='/api/v1/auth'`: the cookie is only attached to requests to auth endpoints. A request to `/api/v1/projects` will not include the refresh token."
- "`secure=True` in production: the browser will only send the cookie over HTTPS. In dev we use HTTP so we set it to False."

**Point to the login endpoint — shows access+cookie pattern:**
```python
@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)):
    access, refresh = auth_service.login(db, body.email, body.password)
    _set_refresh_cookie(response, refresh)
    return TokenResponse(access_token=access)
```
"The access token is returned in the JSON response body — the frontend stores it in memory. The refresh token is set as an HTTP-only cookie — the frontend never touches it directly."

---

## 6. Open `backend/app/api/deps.py`

**Show the before and after:**

Before (Module 07 stub):
```python
async def get_current_user(db: Session = Depends(get_db)) -> User:
    raise UnauthorizedError("Authentication not implemented — override in tests")
```

After (real implementation):
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

**What to say:**
- "`HTTPBearer` extracts the token from `Authorization: Bearer <token>` header. It is one dependency used by every protected route."
- "In tests, `app.dependency_overrides[get_current_user] = lambda: owner` replaces the entire function — JWT is never called in unit/integration tests, only in the auth tests that use `auth_client`."

---

## 7. Run the tests live — show the two client fixture patterns

```powershell
docker compose run --rm backend pytest tests/test_auth.py -v
```

**Expected output — point out the auth-specific tests:**
```
test_register_returns_201_without_password_fields PASSED
test_password_is_stored_as_argon2_hash PASSED
test_duplicate_registration_returns_409 PASSED
test_email_is_normalised_to_lowercase PASSED
test_login_returns_access_token_and_sets_httponly_cookie PASSED
test_wrong_password_returns_generic_401 PASSED
test_unknown_email_returns_same_error_as_wrong_password PASSED
test_me_without_token_returns_401 PASSED
test_me_with_valid_token_returns_user PASSED
test_invalid_token_returns_401 PASSED
test_expired_token_returns_401 PASSED
test_refresh_token_cannot_act_as_access_token PASSED
test_refresh_issues_new_access_token PASSED
test_other_user_cannot_read_private_project PASSED
test_other_user_cannot_update_private_project PASSED

15 passed
```

**Point out `test_password_is_stored_as_argon2_hash`:**
```python
def test_password_is_stored_as_argon2_hash(auth_client, db_session):
    _register(auth_client, "hashcheck@example.com", password="plaintext123")
    user = user_repository.get_by_email(db_session, "hashcheck@example.com")
    assert user.password_hash != "plaintext123"
    assert user.password_hash.startswith("$argon2")
```
"This test queries the database directly after registration and proves the stored value is not the plaintext password — it starts with `$argon2`."

**Point out `test_unknown_email_returns_same_error_as_wrong_password`:**
"Same status code (401), same message ('Invalid credentials') whether the email exists or not. Callers cannot use the response to enumerate registered users."

Then run all 46:
```powershell
docker compose run --rm backend pytest -v
```

---

## 8. Show the OpenAPI docs in the browser

Open `http://localhost:8000/docs`

**What to show:**
- The **auth** section with 5 endpoints
- Click the lock icon (🔒) on any protected endpoint — shows Bearer token field
- `POST /api/v1/auth/register` — show `UserRegister` schema (has `password` field)
- `POST /api/v1/auth/login` — show `TokenResponse` in response schema
- `GET /api/v1/auth/me` — show that `password_hash` is absent from `UserRead`

---

## 9. Live end-to-end demo (requires stack running)

Start the stack:
```powershell
docker compose up -d
```

Register a user:
```powershell
curl.exe -s -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{"email":"demo@example.com","full_name":"Demo","password":"demopass123"}'
```

Login and capture the token:
```powershell
curl.exe -s -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"demo@example.com","password":"demopass123"}'
```

Use the returned `access_token` to call `/me`:
```powershell
curl.exe -s http://localhost:8000/api/v1/auth/me `
  -H "Authorization: Bearer <paste_access_token_here>"
```

**Expected output:** User object without `password_hash`.

---

## 10. Show threat notes from `docs/security.md`

Open [docs/security.md](../docs/security.md) and point to:
- "Passwords are hashed with Argon2 through `argon2-cffi`" — matches implementation
- "Known training limitations" section — no rotation, no revocation, no MFA
- "Do not claim the reference session design is sufficient for every production risk"

**What to say:** "Security work includes recognising limitations, not just implementing what works. A valid token does not authorize every resource — authorization is checked separately on every project and task operation."

---

## Questions the lead may ask

**Q: Why Argon2 and not bcrypt?**
A: Both are acceptable. Argon2id is the current OWASP recommendation because it adds memory hardness (memory-cost `m` parameter) which defeats GPU-scale attacks more effectively than bcrypt's time-only cost.

**Q: Why not use OAuth2PasswordBearer instead of HTTPBearer?**
A: `OAuth2PasswordBearer` expects the login endpoint to accept `application/x-www-form-urlencoded` (form data) to show the Authorize button in the OpenAPI UI. Our login uses JSON, so `HTTPBearer` is the correct helper — it just reads `Authorization: Bearer <token>` without the OAuth2 form machinery.

**Q: Why does the access token expire in 30 minutes if we can refresh it?**
A: The access token is in memory — if it is somehow stolen (XSS, logging leak), limiting its lifetime limits the damage window. The refresh token is in a secure cookie with a longer life (7 days). Refreshing issues a new short-lived access token without the user re-entering their password.

**Q: What prevents someone from just calling `/api/v1/auth/refresh` with their own cookie?**
A: They would need the `refresh_token` cookie value, which is `HttpOnly` — JavaScript cannot read it. If they have physical access to the cookie (e.g., stolen device, MITM), that is a separate threat. `Secure=True` in production prevents MITM interception by enforcing HTTPS.

**Q: What happens if a user changes their password?**
A: Nothing — existing tokens remain valid until they expire. Full production systems maintain a token revocation list or include a `password_version` claim in the token. This is documented as a known training limitation.
