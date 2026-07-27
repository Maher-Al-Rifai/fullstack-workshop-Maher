# Module 03: HTTP, REST, JSON, and API contracts

**Guided effort:** 5 hours  
**Required branch:** `learning/03-api-contracts`  
**Phase:** Foundation

## Objectives

- Decompose HTTP requests and responses into method, target, headers, body, status, and representation.
- Choose methods and status codes based on semantics rather than habit.
- Read and exercise OpenAPI documentation with curl or an HTTP client.
- Write explicit success, validation, authentication, authorization, conflict, and not-found behavior.

## Prerequisites

- Modules 00–02 complete.
- Reference/starter services available or ability to inspect OpenAPI.

## Concepts and context

HTTP is the contract between frontend and backend. REST is an architectural style, not a requirement to use every method or eliminate all actions. Correct contracts make behavior predictable: methods carry semantics, status codes describe outcomes, headers carry metadata/authentication, and representations carry data.

A `200` with an error string is not equivalent to a `4xx`. `401` means authentication is required or invalid; `403` means identity is known but forbidden; a resource-scoped `404` can avoid disclosing private existence. `422` is used by FastAPI for request validation. `409` fits a state conflict such as an invalid task transition or duplicate unique value.

## Step-by-step lab

### 1. Inspect the documented contract

Read `../docs/api-contract.md` and open `http://localhost:8000/docs`. Locate schemas, security requirements, and every project/task path. Export or inspect `/openapi.json`:

```bash
curl --fail http://localhost:8000/openapi.json > /tmp/workboard-openapi.json
python -m json.tool /tmp/workboard-openapi.json | sed -n '1,120p'
```

### 2. Trace a request on the wire

Use `curl -v` for status and headers:

```bash
curl -v http://localhost:8000/api/v1/status
```

Identify DNS/connection target, request line, headers, response status, content type, and body. Explain which details are transport versus application behavior.

### 3. Exercise authentication manually

Use `../examples/http/workboard.http` or curl:

```bash
curl -i -X POST http://localhost:8000/api/v1/auth/register   -H 'Content-Type: application/json'   -d '{"email":"api-learner@example.com","full_name":"API Learner","password":"StrongPassword123!"}'

curl -i -X POST http://localhost:8000/api/v1/auth/login   -H 'Content-Type: application/x-www-form-urlencoded'   --data-urlencode 'username=api-learner@example.com'   --data-urlencode 'password=StrongPassword123!'
```

Store the token only in an uncommitted shell variable. Do not paste it into the committed HTTP file.

### 4. Build a status/error matrix

For project creation and task transition, record expected:

- valid request;
- missing required field;
- malformed type/enum;
- no token;
- invalid token;
- inaccessible project;
- missing project/task;
- duplicate/conflict;
- invalid status transition.

For each, choose status, response shape, and client behavior. Compare with the actual API and file a curriculum/implementation issue for genuine mismatch.

### 5. Inspect idempotency and retry implications

Compare:

- `GET /projects` repeated;
- `POST /projects` repeated;
- `PATCH /tasks/{id}` repeated with the same body;
- `DELETE` repeated after the resource is gone.

Explain which operations are semantically idempotent and why a network retry can still require an idempotency key for some production creates/payments.

### 6. Propose a contract change

Design, but do not necessarily implement, task filtering:

```text
GET /api/v1/projects/{project_id}/tasks?status=in_progress&priority=high
```

Specify parameter validation, combination behavior, empty result, pagination future, index implications, OpenAPI docs, frontend type, and tests. Keep it backward compatible.

### 7. Update documentation evidence

Add the matrix and proposal to the learning log or module issue. Do not edit `docs/api-contract.md` unless actual repository behavior changes.

## Validation checklist

- [ ] I can identify every part of a real request/response transcript.
- [ ] My error matrix distinguishes 401, 403/resource-scoped 404, 404, 409, and 422.
- [ ] I exercised a protected endpoint without committing a token.
- [ ] I can explain method safety/idempotency and practical retry risk.
- [ ] The proposed filtering contract covers validation, empty results, compatibility, data, frontend, and tests.

## Independent challenge

Create two users and prove through direct API calls that a private project cannot be read by the second user. Record status/body without exposing full tokens.

## Common failure modes

- Choosing status codes based only on what the frontend currently expects.
- Equating hidden UI controls with authorization.
- Committing bearer tokens in examples.
- Using POST for every operation without considering semantics.

## Evidence to submit

- Annotated request/response transcript.
- Status/error matrix.
- Cross-user authorization request evidence.
- Backward-compatible filter contract proposal.

## Commit checkpoint

```text
docs(api): record HTTP contract and error analysis
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [api-contract.md](../docs/api-contract.md)
- [workboard.http](../examples/http/workboard.http)
- [rfc9110.html](https://www.rfc-editor.org/rfc/rfc9110.html)
- [latest.html](https://spec.openapis.org/oas/latest.html)
