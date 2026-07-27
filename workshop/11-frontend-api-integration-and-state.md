# Module 11: Frontend API integration and state

**Guided effort:** 12 hours  
**Required branch:** `learning/11-frontend-api`  
**Phase:** Frontend

## Objectives

- Create one typed API client that handles base URLs, bearer access, one refresh/retry, and normalized errors.
- Implement shared authentication state and protected-route middleware without redirect loops.
- Connect project/task pages to real backend behavior with resilient UI states.
- Distinguish local component state, route data, server data, and global client state.

## Prerequisites

- Module 10 complete.
- Backend authentication/project/task API available.

## Concepts and context

Network calls fail in ordinary ways: validation, authentication expiry, authorization, conflict, timeout, offline state, and server failure. A frontend integration is complete only when those outcomes have explicit behavior.

The API client owns transport mechanics. The auth store owns shared identity/access-token state. Pages own project/task data in the reference because it is not yet a cross-route cache. Nuxt server rendering cannot use browser-only memory or cookie APIs in the same way as client code; public unauthenticated SSR uses the internal base URL separately.

## Step-by-step lab

### 1. Design the API client contract

Create a client factory that receives a fetcher and callbacks for access token, refresh, and authentication failure. This makes behavior testable without a real network.

For every request:

- prepend the correct runtime base URL;
- attach bearer token when available;
- preserve caller method/body/query/options;
- on the first `401`, attempt refresh once and retry once;
- prevent recursive/infinite refresh;
- surface a normalized error for UI use.

Do not persist the access token in local storage in the baseline.

### 2. Implement the auth store

State should include:

- current user;
- in-memory access token;
- loading/initialized state;
- login/register/refresh/load-me/logout actions.

Registration may create a user and then login, or return to login; keep contract/documentation consistent. Logout clears local state even if the network call fails, while preserving useful error reporting.

### 3. Initialize auth safely

Use a client plugin to attempt refresh/load current user once. Distinguish:

- initialization still running;
- authenticated;
- unauthenticated.

Do not redirect before initialization finishes. Avoid server/client hydration mismatch by keeping private pages client-authenticated in the baseline.

### 4. Protect routes

Create auth middleware for dashboard/projects. Preserve intended return navigation when practical. Login/register should not loop. Test direct URL navigation and browser refresh, not only NuxtLink navigation.

### 5. Connect login/register

Implement labeled forms, submitting/disabled state, field constraints, server error display, and redirect on success. Do not display the raw backend exception object.

Inspect network requests:

- form content type for login;
- refresh cookie presence/flags;
- Authorization header on `/auth/me`;
- absence of password/token in frontend logs.

### 6. Connect project list/create

On the projects page:

- load projects after auth;
- show loading/error/empty states;
- create a project and update the visible list;
- avoid duplicate submission while saving;
- support public/private selection.

Use an API service/composable; do not duplicate refresh logic in the page.

### 7. Connect project detail/tasks

Load project and task list; create tasks; move allowed statuses; delete tasks. Keep UI synchronized with returned server representation rather than assuming the request succeeded exactly as sent.

Display conflict errors for invalid transition and authorization errors without silently removing data.

### 8. Failure drills

Exercise:

- stop backend while page is open;
- expire/corrupt the access token and confirm one refresh attempt;
- remove refresh cookie and confirm sign-in recovery;
- submit invalid data;
- attempt double click during create;
- use a second user on an inaccessible URL.

Record user-visible behavior and console/network evidence.

### 9. Type and build

```bash
npm run lint
npm run typecheck
npm test
npm run build
```

## Validation checklist

- [ ] One API client owns base URL, bearer, refresh, retry, and error behavior.
- [ ] Refresh is attempted at most once per failed request.
- [ ] Auth initialization does not cause redirect or hydration loops.
- [ ] Access token is held in memory rather than committed/persisted local storage.
- [ ] Project/task pages handle loading, empty, error, saving, and success.
- [ ] UI uses returned server data and prevents obvious duplicate submissions.
- [ ] Failure drills produce recoverable user feedback and no secret logging.

## Independent challenge

Add cancellation for route data requests using `AbortController` so a stale response cannot overwrite a newer route state. Demonstrate with an artificial delay and write a focused test or reproducible trace.

## Common failure modes

- Retrying `401` forever.
- Persisting access tokens in local storage without threat analysis.
- Redirecting before auth initialization completes.
- Treating every server response as a global store concern.
- Catching errors and showing nothing to the user.

## Evidence to submit

- Auth and refresh sequence diagram.
- Network evidence with tokens redacted.
- Screenshots of loading/empty/error/conflict states.
- Failure-drill table.
- Lint/typecheck/test/build output.

## Commit checkpoint

```text
feat(web): integrate authenticated API and client state
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [api-contract.md](../docs/api-contract.md)
- [security.md](../docs/security.md)
- [data-fetching](https://nuxt.com/docs/getting-started/data-fetching)
- [https://pinia.vuejs.org/](https://pinia.vuejs.org/)
- [AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)
