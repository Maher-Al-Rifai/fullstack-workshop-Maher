# Module 10 — Demo Guide: Nuxt, Vue, and TypeScript Foundation

Step-by-step walkthrough for demonstrating Module 10 competency.

---

## 1. Show the folder structure

```powershell
Get-ChildItem frontend/app -Recurse -Filter "*.vue" | Select-Object FullName
Get-ChildItem frontend/app -Recurse -Filter "*.ts"  | Select-Object FullName
```

Point out the three layers:
- `pages/` — route-level, owns data fetching
- `components/` — presentational with typed props/events
- `types/index.ts` — shared contracts

---

## 2. Walk through nuxt.config.ts

Open `frontend/nuxt.config.ts` and explain the runtime config split:

```typescript
runtimeConfig: {
  // Only available on the server — safe for internal service URLs
  apiInternalBase: process.env.NUXT_API_INTERNAL_BASE || '...',
  public: {
    // Bundled into the client — NEVER put secrets here
    apiBase: process.env.NUXT_PUBLIC_API_BASE || '...',
  },
},
```

Ask: "What happens if you put a service account key under `public`?" → It's visible in the browser bundle.

---

## 3. Explain the type contract

Open `frontend/app/types/index.ts`:

```typescript
export type TaskStatus = 'backlog' | 'in_progress' | 'done' | 'cancelled'

export interface Task {
  id: number
  title: string
  status: TaskStatus
  // ...
}
```

Key teaching point: **TypeScript types are compile-time only.** If the backend returns `{ "status": "todo" }` (which isn't a valid `TaskStatus`), TypeScript doesn't catch this at runtime. Backend Pydantic schemas are the true validation boundary.

---

## 4. Show a typed component contract

Open `frontend/app/components/TaskCard.vue`:

```typescript
const props = defineProps<{ task: Task }>()

const emit = defineEmits<{
  advance: [taskId: number, toStatus: TaskStatus]
  delete: [taskId: number]
}>()
```

Then show the parent page (`projects/[id].vue`) using it:

```vue
<TaskCard
  v-for="task in tasks"
  :key="task.id"
  :task="task"
  @advance="handleAdvance"
  @delete="handleDelete"
/>
```

Key point: `TaskCard` never fetches data. It receives `task` as a prop and emits events. The page decides what to do with those events.

---

## 5. Demonstrate the four required states

Open `frontend/app/pages/projects/index.vue` and show:

```vue
<UiLoadingSpinner v-if="pending" label="Loading projects…" />
<UiErrorAlert v-else-if="fetchError" message="Could not load projects." />
<div v-else-if="projects.length === 0" class="empty-state">...</div>
<div v-else class="card-grid">...</div>
```

Explain why each state matters:
- **Loading** — avoids blank screen during fetch
- **Error** — tells the user something went wrong with text (not color-only)
- **Empty** — guides new users who have no data yet
- **Success** — renders the actual content

---

## 6. Accessibility walkthrough

Start the dev server:
```bash
cd frontend
npm run dev
```

Open `http://localhost:3000`. Do the keyboard walkthrough:
1. Press **Tab** — focus should land on the "Workboard" brand link in the header
2. Press **Tab** again — focus moves to "Dashboard" nav link, then "Projects"
3. Continue to "Sign in" button, then "Register" button
4. Navigate to `/login` — Tab through email → password → submit button
5. Inspect: each `<input>` has an explicit `<label for="...">` association

Use browser DevTools → Accessibility inspector to confirm:
- nav landmark is named "Main navigation"
- `<span role="status" aria-live="polite">` exists inside LoadingSpinner
- buttons and links have clear accessible names (not "click here")

---

## 7. Run the quality gate

```bash
cd frontend
npm run lint
```
Expected: no output (clean).

```bash
npm run typecheck
```
Expected: `Type check passed in Xs. Exit: 0`

Note the volar warning about `vue-router/volar/sfc-route-blocks` — explain it's a cosmetic compatibility warning with the pinned `vue-router 4.6.4`, not a failure.

```bash
npm run build
```
Expected: `Build complete!` with bundle sizes. Show that build is important because universal rendering can surface server-only errors that dev mode hides.

---

## 8. Show why build matters for SSR

Mention that if you accidentally access `window` during server rendering, it fails at build time:

```typescript
// This would fail SSR (window is not available on the server)
const token = window.localStorage.getItem('token')

// Correct pattern — client-only plugin or useNuxtApp + onMounted
onMounted(() => {
  const token = localStorage.getItem('token')
})
```

Module 11 handles token storage safely using HTTP-only cookies for the refresh token.

---

## 9. Explain page vs component vs composable

Draw or write the three layers:

```
Page (pages/)
  └── owns useFetch, manages state
      └── Component (components/)
              └── receives props, emits events
Composable (composables/)        ← Module 11
  └── shared reactive behavior (auth state, API wrapper)
```

Common failure mode to name: **calling useFetch inside a component**. This ties the component to a specific URL and makes it impossible to use in other contexts or test in isolation.

---

## Summary checklist for the demo

- [ ] Nuxt file-based routing explained (pages → routes)
- [ ] Private vs public runtime config explained (no secrets in public)
- [ ] `types/index.ts` shown — TypeScript types vs runtime validation boundary
- [ ] `TaskCard` typed props/events demonstrated
- [ ] Four UI states shown in a page (loading, error, empty, success)
- [ ] Accessibility: every input has a label, focus ring visible, nav landmark named
- [ ] `npm run lint` passes with zero errors
- [ ] `npm run typecheck` passes with exit 0
- [ ] `npm run build` succeeds — build complete
- [ ] Page vs component vs composable responsibility explained
