# Module 13 Demo Guide: Frontend Testing with Vitest

## What you're demonstrating

41 Vitest tests across three layers — pure utilities, transport client, and Vue component — all fast, all passing, with lint/typecheck/build green.

---

## Setup (30 seconds)

```powershell
cd frontend
# Ensure dependencies and types are current
npm run postinstall
```

---

## Demo 1: Run all tests and read the output (2 minutes)

```bash
npx vitest run
```

**Expected output:**
```
 Test Files  3 passed (3)
      Tests  41 passed (41)
   Duration  ~5s (tests ~350ms)
```

Point out:
- **3 test files** map exactly to 3 layers of the risk map
- **350ms execution** — fast enough to run on every keystroke in watch mode
- Zero mocking of the function under test in any file

---

## Demo 2: Walk the risk map (3 minutes)

Open `tests/unit/utils.test.ts` and explain:

> These are table-driven tests. Each row is one contract clause. If a PM changes a label, this file breaks before a single user sees it.

Open `tests/unit/api-client.test.ts` and point out the fake fetcher:

```ts
const fetcher = vi.fn().mockResolvedValue({ id: 1 })
const api = createApiFetch({ baseURL: '/api', getToken: () => 'tok', fetcher })
```

> The real `$fetch` never runs. We replaced it with a plain function. This is the minimal boundary mock.

Open `tests/components/TaskCard.test.ts` and show:

```ts
const wrapper = mount(TaskCard, { props: { task } })
expect(wrapper.text()).toContain('Fix login page')
```

> No XPath. No CSS selectors. No snapshot. User-visible text only.

---

## Demo 3: Mutation drill — live (5 minutes)

### Mutation 1 — reverse a status label

In `app/utils/labels.ts`, temporarily change:
```ts
todo: 'To Do'    →    todo: 'Done'
```

Run:
```bash
npx vitest run tests/unit/utils.test.ts
```

Show the failure:
```
expected 'Done' to be 'To Do'
```

Revert. Lesson: **table-driven tests catch label regressions instantly.**

---

### Mutation 2 — emit wrong task ID

In `app/components/TaskCard.vue`, in the `advance` button handler, temporarily change:
```ts
emit('advance', props.task.id)    →    emit('advance', 0)
```

Run:
```bash
npx vitest run tests/components/TaskCard.test.ts
```

Show the failure:
```
expected [ 0 ] to deeply equal [ 1 ]
```

Revert. Lesson: **component tests prove event payloads, not just event names.**

---

### Mutation 3 — remove the infinite-loop guard

In `app/utils/api-client.ts`, remove the `_retried` check inside the 401 handler (the `if (options._retried)` block).

Run:
```bash
npx vitest run tests/unit/api-client.test.ts
```

Show the failure:
```
expected "spy" to be called 2 times, but got called 3 times
```

Revert. Lesson: **transport tests catch recursive retry bugs before they hit production.**

---

## Demo 4: Explain what we deliberately did NOT test here (2 minutes)

| Behavior | Reason skipped in Module 13 |
|---|---|
| Auth middleware redirect | Requires full Nuxt route plugin context — covered in Module 15 |
| Server-rendered meta tags | Needs a real HTTP response head — manual or Playwright |
| Registration form submission | Full stack journey — Playwright E2E in Module 15 |

> Module 13 is intentionally narrow. If it can be caught with a 350ms test, it belongs here. If it requires a browser or a real server, it belongs in Module 15.

---

## Demo 5: Full quality gate (1 minute)

```bash
npm run lint && npm run typecheck && npm test && npm run build
```

All four commands exit 0. Show the final build line:

```
✨ Build complete!
```

---

## Talking points for assessors

1. **Why `createApiFetch` instead of mocking `$fetch` globally?**  
   Global mocking replaces the collaborator with a stub that doesn't reflect real behavior. The factory makes the dependency explicit and testable without patching globals.

2. **Why table-driven tests instead of separate `it()` blocks?**  
   Each row is a contract clause. Adding a new status takes one line. The test name includes the inputs, so failures self-document.

3. **Why happy-dom and not jsdom or a real browser?**  
   happy-dom is faster and sufficient for DOM queries. Real-browser behavior (CSS rendering, focus management) is reserved for Playwright. Using the wrong environment for every test wastes time.

4. **Why assert `wrapper.text()` instead of CSS classes?**  
   Classes are implementation detail. Text is the user-visible contract. Refactoring the component without changing behavior must not break tests.

---

## Files changed in this module

| Path | Change |
|---|---|
| `frontend/vitest.config.ts` | New — Vitest configuration |
| `frontend/tests/setup.ts` | New — global mocks for Nuxt auto-imports |
| `frontend/tests/unit/utils.test.ts` | New — 17 utility tests |
| `frontend/tests/unit/api-client.test.ts` | New — 10 transport tests |
| `frontend/tests/components/TaskCard.test.ts` | New — 14 component tests |
| `frontend/app/utils/api-client.ts` | New — `createApiFetch` factory + `normalizeError` |
| `frontend/app/utils/labels.ts` | New — extracted label maps |
| `frontend/app/utils/formatDate.ts` | New — date formatter |
| `frontend/app/composables/useApi.ts` | Updated — delegates to factory |
| `frontend/app/components/ui/StatusBadge.vue` | Updated — imports labels |
| `frontend/app/components/TaskCard.vue` | Updated — explicit vue import |
| `frontend/app/types/index.ts` | Updated — `email`, `critical`, removed duplicates |
| `frontend/app/stores/auth.ts` | Updated — `email` field |
| `frontend/app/pages/login.vue` | Updated — `email` field |
| `frontend/package.json` | Updated — `@vitejs/plugin-vue`, `happy-dom`, `eslint` |
