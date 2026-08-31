# Module 11 — Frontend API Integration and State

## What this module covers

Module 11 connects the Nuxt frontend to the real FastAPI backend: one typed API client with bearer injection and 401/refresh/retry, a Pinia auth store with in-memory token storage, a client plugin for initialization, route middleware, and full CRUD pages for auth, projects, and tasks.

---

## Architecture added

```
frontend/app/
├── stores/
│   └── auth.ts              # Pinia setup store — user, token, login/logout/refresh
├── composables/
│   ├── useApi.ts             # Typed fetch wrapper — bearer, 401 retry, error normalization
│   ├── useProjects.ts        # Project CRUD over useApi
│   └── useTasks.ts           # Task CRUD over useApi
├── plugins/
│   └── auth.client.ts        # Client-only: initialize auth from refresh cookie on load
└── middleware/
    └── auth.ts               # Protect /dashboard and /projects/* — client-only
```

---

## API client design

`app/composables/useApi.ts` owns ALL transport mechanics:

```typescript
async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { _retried, ...fetchOptions } = options
  try {
    return await $fetch(path, {
      baseURL,
      headers: { Authorization: `Bearer ${auth.accessToken}`, ...fetchOptions.headers },
      credentials: 'include',
      ...fetchOptions,
    })
  } catch (err) {
    if (err.status === 401 && !_retried) {
      const ok = await auth.refresh()
      if (ok) return apiFetch(path, { ...options, _retried: true })
      // Refresh failed → clear session, redirect to /login
    }
    throw normalizeError(err)
  }
}
```

Key properties:
- **One refresh attempt** — `_retried` flag prevents infinite loops
- **Normalized errors** — every failure becomes `{ message, status, code }` matching the API contract
- **No localStorage** — access token lives only in Pinia memory (cleared on page reload, recovered via refresh cookie)
- **`credentials: 'include'`** — ensures the HTTP-only refresh cookie is sent on every request

---

## Auth store

`app/stores/auth.ts` (Pinia setup store):

| State | Type | Purpose |
|---|---|---|
| `user` | `User \| null` | Authenticated user profile |
| `accessToken` | `string \| null` | In-memory only — never persisted |
| `initialized` | `boolean` | Plugin finished the startup check |
| `isAuthenticated` | `computed` | Derived: `!!user` |

Actions: `login`, `register`, `refresh`, `loadMe`, `initialize`, `logout`

**Login** uses `application/x-www-form-urlencoded` (OAuth2 form format required by the backend):
```typescript
const body = new URLSearchParams()
body.append('username', credentials.username)  // email sent as username
body.append('password', credentials.password)
```

**Logout** clears local state even if the network call fails:
```typescript
async function logout() {
  try { await $fetch('/api/v1/auth/logout', ...) }
  finally { user.value = null; accessToken.value = null }
}
```

---

## Client plugin — auth initialization

`app/plugins/auth.client.ts` runs **once** in the browser:

```typescript
export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  await auth.initialize()
})
```

`initialize()` tries to refresh the HTTP-only cookie → if successful, calls `loadMe()` → sets `initialized = true`. This recovers the session after a hard page reload without requiring re-login.

---

## Route middleware

`app/middleware/auth.ts` protects authenticated routes:

```typescript
export default defineNuxtRouteMiddleware((to) => {
  if (import.meta.server) return           // SSR: skip, check runs on client
  const auth = useAuthStore()
  if (!auth.initialized) return            // Plugin still running — wait
  if (!auth.isAuthenticated)
    return navigateTo(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
})
```

Applied to a page with `definePageMeta({ middleware: ['auth'] })`.

**Why client-only?** The access token is in memory. On SSR there is no Pinia state for the user — the server cannot verify auth from a cookie alone in the baseline. The module keeps private pages client-authenticated to avoid SSR hydration mismatches.

**No redirect loop**: `/login` and `/register` pages use inline middleware that redirects AUTHENTICATED users away (not the `auth` middleware, which would loop).

---

## Composable layering

```
Page
  └── useProjects() / useTasks()   ← domain operations
        └── useApi().apiFetch()    ← transport + auth
              └── $fetch           ← ofetch (Nuxt built-in)
```

Pages never call `$fetch` directly. Composables never duplicate bearer injection or retry logic.

---

## Pages wired in this module

| Page | Middleware | Data source | Features |
|---|---|---|---|
| `/login` | Redirect authenticated users to `/dashboard` | `auth.login()` | Form, error display, return-URL redirect |
| `/register` | Redirect authenticated users to `/dashboard` | `auth.register()` | Form, error display, auto-login after register |
| `/dashboard` | `auth` | `listProjects()` on `onMounted` | Shows user name, project list |
| `/projects` | `auth` | `listProjects()` + `createProject()` | List, inline create form, duplicate submit guard |
| `/projects/[id]` | `auth` | `getProject()` + `listTasks()` | Task create, status advance, delete, conflict errors |

---

## Four failure states handled everywhere

```vue
<UiLoadingSpinner v-if="pending" />
<UiErrorAlert v-else-if="fetchError" :message="fetchError" />
<div v-else-if="items.length === 0" class="empty-state">...</div>
<div v-else class="card-grid">...</div>
```

Task operations (advance/delete) also surface errors inline without clearing the existing list.

---

## Quality gate

```bash
npm run lint       # 0 errors
npm run typecheck  # Type check passed, exit 0
npm run build      # Build complete, exit 0
npm test           # vitest run (no tests yet — Module 13 adds them)
```

`vitest` was added in this module; `npm test` exits 0 with no test files.

---

## Packages added

| Package | Version | Purpose |
|---|---|---|
| `pinia` | 4.0.3 | State management |
| `@pinia/nuxt` | 1.0.2 | Nuxt module integration |
| `vitest` | 4.1.11 | Test runner (Module 13 adds test files) |
| `@vue/test-utils` | 2.4.6 | Component testing utilities |
