# Module 13 Summary: Frontend Testing with Vitest

## What I built

Three Vitest test files covering the frontend application's most important contract boundaries:

| File | Tests | Layer |
|---|---|---|
| `tests/unit/utils.test.ts` | 17 | Pure utility functions |
| `tests/unit/api-client.test.ts` | 10 | Transport client (dependency-injected) |
| `tests/components/TaskCard.test.ts` | 14 | Vue component rendering and events |

**Total: 41 tests, all passing. Lint, typecheck, and production build all pass.**

---

## Frontend risk map

I assigned test layers by "lowest useful layer":

| Behavior | Layer assigned |
|---|---|
| Date formatting | Unit |
| Status / priority label mapping | Unit |
| API error normalization | Unit |
| Task card advance event | Component |
| Form disabled while saving | Component |
| API base URL, bearer header, body | API-client unit |
| 401 → one refresh → retry | API-client unit |
| Auth middleware redirect | Nuxt integration (deferred to Module 15) |
| Server-rendered public SEO metadata | Manual / Playwright (Module 15) |
| Complete registration/project/task journey | Playwright E2E (Module 15) |

Rule: **never reach for Playwright for something a fast unit or component test can catch.**

---

## Key design decisions

### 1. `createApiFetch` — testable factory

`app/utils/api-client.ts` exports a factory that accepts a `fetcher` parameter (defaults to `$fetch` in production). Tests pass a fake arrow function:

```ts
const fetcher = vi.fn().mockResolvedValue({ id: 1 })
const api = createApiFetch({ baseURL: '/api', getToken: () => 'tok', fetcher })
```

This gives full control over transport responses without mocking the function under test.

### 2. `_retried` flag prevents infinite 401 loops

The `createApiFetch` factory sets a `_retried` property on the options object before the first retry. On a second 401, it checks `options._retried` and calls `onUnauthenticated` instead of refreshing again. Tests proved this catches the infinite-loop regression.

### 3. `tests/setup.ts` — mocking Nuxt auto-imports

Nuxt auto-imports (`ref`, `computed`, `useRoute`, etc.) don't exist in Vitest's happy-dom environment. The setup file does two things:
- `Object.assign(globalThis, Vue)` — makes Vue reactivity primitives globally available
- Explicit `vi.fn()` stubs for `navigateTo`, `useRoute`, `useRouter`, `useRuntimeConfig`, `definePageMeta`, `useSeoMeta`

This is the minimum required — only mocking what genuinely applies to every test.

### 4. Table-driven utility tests

All pure-function tests use arrays of `[input, expected]` pairs with `it.each`. This documents the contract precisely and makes adding new cases a one-liner.

```ts
it.each([
  ['todo', 'To Do'],
  ['in_progress', 'In Progress'],
  ['done', 'Done'],
  ['cancelled', 'Cancelled'],
])('STATUS_LABELS[%s] === %s', (status, label) => {
  expect(STATUS_LABELS[status as TaskStatus]).toBe(label)
})
```

### 5. Component tests assert visible behavior

`TaskCard.test.ts` mounts with `@vue/test-utils` and asserts:
- Text visible to users (title, description, status badge text, priority, date)
- Button **presence/absence** for valid vs. invalid transitions
- Emitted event **payloads** — `advance` carries the task ID, `remove` carries the task ID

Never tested internal refs or implementation-specific CSS classes.

---

## Bug fixes discovered during testing

| File | Bug | Fix |
|---|---|---|
| `app/types/index.ts` | `LoginRequest` had `username` instead of `email` | Renamed to `email` |
| `app/types/index.ts` | `TaskPriority` missing `'critical'` | Added |
| `app/stores/auth.ts` | `register()` called `login({ username: ... })` | Changed to `email` |
| `app/pages/login.vue` | `{ username: email.value }` in login body | Changed to `{ email: email.value }` |
| `app/components/TaskCard.vue` | `computed` not explicitly imported | Added `import { computed } from 'vue'` |

Tests caught three of these — they would have been silent runtime bugs.

---

## Mutation drill results

| Mutation | Test that caught it |
|---|---|
| Reversed `STATUS_LABELS['todo']` to `'Done'` | `utils.test.ts` STATUS_LABELS table |
| Emitted wrong task ID in `advance` event | `TaskCard.test.ts` — "emits advance with task id" |
| Removed `_retried` guard in `createApiFetch` | `api-client.test.ts` — "does not retry twice on second 401" |

All three mutations were caught immediately. No surviving cases required.

---

## Quality gates

```
npm run lint       ✅  exit 0  (ESLint with @nuxt/eslint)
npm run typecheck  ✅  exit 0  (vue-tsc)
npm test           ✅  exit 0  (41/41 tests, ~350ms execution)
npm run build      ✅  exit 0  (production build, 36.5 MB)
```

---

## Validation checklist

- [x] Risk map separates unit, component, API-client, Nuxt, and E2E responsibilities
- [x] Utility tests protect deterministic contracts (labels, dates, error normalization)
- [x] Component tests assert visible behavior and emitted domain events
- [x] API client tests prove one refresh/retry and no infinite loop
- [x] Three deliberate mutations are detected after improvements
- [x] Lint, typecheck, tests, and production build pass

---

## Key commands

```bash
# Run all tests once
cd frontend
npx vitest run

# Watch mode during development
npx vitest

# Run only a specific file
npx vitest run tests/unit/utils.test.ts

# Full quality gate
npm run lint && npm run typecheck && npm test && npm run build
```

---

## What to avoid

- **Snapshot tests for strings** — they hide the contract; use exact assertions
- **Mocking the function under test** — test the real implementation with fake collaborators
- **Testing only happy path** — null/empty/error states are where integrations break
- **Playwright for everything** — a component test that takes 100ms is better than a browser test that takes 5s for the same coverage
