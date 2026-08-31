# Module 10 — Nuxt, Vue, and TypeScript Foundation

## What this module covers

Module 10 establishes the frontend application structure: Nuxt conventions, Vue Composition API patterns, strict TypeScript contracts for the API, reusable UI components, route-level pages with proper state handling, and accessibility-first markup. The quality gate runs lint, typecheck, and build in sequence.

---

## Application structure after this module

```
frontend/
├── eslint.config.mjs              # ESLint flat config (via @nuxt/eslint)
├── nuxt.config.ts                 # Runtime config, modules, TypeScript settings
├── package.json                   # Added lint script + @nuxt/eslint
└── app/
    ├── app.vue                    # Shell: AppHeader / <NuxtPage /> / AppFooter
    ├── assets/
    │   └── css/main.css           # Design tokens and global primitives
    ├── types/
    │   └── index.ts               # Typed API contracts
    ├── components/
    │   ├── AppHeader.vue          # Sticky header with navigation landmarks
    │   ├── AppFooter.vue          # Footer
    │   ├── ProjectCard.vue        # Project summary card
    │   ├── TaskCard.vue           # Task card with advance/delete emits
    │   └── ui/
    │       ├── LoadingSpinner.vue # ARIA live region loading indicator
    │       ├── ErrorAlert.vue     # role="alert" error display
    │       └── StatusBadge.vue    # Typed task status badge
    └── pages/
        ├── index.vue              # Home / landing
        ├── login.vue              # Login form
        ├── register.vue           # Registration form
        ├── dashboard.vue          # Authenticated dashboard
        └── projects/
            ├── index.vue          # Projects list
            ├── [id].vue           # Project detail + task list
            └── public/
                └── projects/
                    └── [slug].vue # Unauthenticated public project view
```

---

## Nuxt application structure concepts

### File-based routing
Nuxt maps files under `app/pages/` to routes automatically:
- `pages/index.vue` → `/`
- `pages/login.vue` → `/login`
- `pages/projects/[id].vue` → `/projects/:id`
- `pages/public/projects/[slug].vue` → `/public/projects/:slug`

### Runtime configuration split

```typescript
// nuxt.config.ts
runtimeConfig: {
  // Private — server-side only, never sent to browser
  apiInternalBase: process.env.NUXT_API_INTERNAL_BASE || 'http://localhost:8000/api/v1',
  public: {
    // Public — visible in browser JavaScript bundle, MUST NOT contain secrets
    apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1',
  },
},
```

Key rule: anything under `runtimeConfig.public` is bundled into the client. Never put tokens, service account keys, or internal service URLs there.

In Docker Compose the backend is reachable at `http://backend:8000` from within the container network. The private `apiInternalBase` is set to that URL for server-side `useFetch` calls; the browser uses the public host URL.

---

## TypeScript API contracts

`app/types/index.ts` defines the shape of every API resource:

```typescript
export type TaskStatus = 'backlog' | 'in_progress' | 'done' | 'cancelled'
export type TaskPriority = 'low' | 'medium' | 'high'

export interface Task {
  id: number
  title: string
  status: TaskStatus
  priority: TaskPriority
  // ... all other fields
}
```

**Important limitation**: TypeScript types only verify shapes at compile time. If the API returns unexpected JSON at runtime, TypeScript cannot catch it. Backend Pydantic schemas are the authoritative validation boundary. Runtime validation (e.g., Zod) can be added at the API client layer in later modules.

---

## Component patterns

### `defineProps` / `defineEmits` — typed contracts

```typescript
// ProjectCard.vue
defineProps<{ project: Project }>()

// TaskCard.vue
const emit = defineEmits<{
  advance: [taskId: number, toStatus: TaskStatus]
  delete: [taskId: number]
}>()
```

### Network calls belong in composables, not components

`ProjectCard` and `TaskCard` receive data as props and emit events up. They never call `fetch` directly. The parent page owns data fetching.

### Four required states for every data-driven view

Every page that loads from the network must handle all four states:

```vue
<UiLoadingSpinner v-if="pending" label="Loading projects…" />
<UiErrorAlert v-else-if="error" :message="error" />
<div v-else-if="items.length === 0" class="empty-state">...</div>
<div v-else class="card-grid">...</div>
```

Omitting any state leads to visual flashing, blank screens, or unhandled exceptions surfaced to users.

---

## Accessibility rules applied

| Rule | Implementation |
|---|---|
| Navigation landmark | `<nav aria-label="Main navigation">` in AppHeader |
| Link purpose clear | "Sign in" / "Register" / "Get started" — no "click here" |
| Every input has a label | `<label for="email">` → `<input id="email">` |
| Error colors supplemented | Role `alert` + text, not color-only |
| Loading state announced | `role="status" aria-live="polite"` on LoadingSpinner |
| Focus ring visible | `:focus-visible { outline: 2px solid var(--color-brand) }` |
| Void elements not self-closed | `<input …>` not `<input … />` (vue/html-self-closing rule) |

Keyboard walkthrough: Tab through header → nav links → Sign in / Register buttons → form inputs → submit. All elements are reachable and have visible focus rings.

---

## ESLint and quality gate

### Setup

```
@nuxt/eslint 1.17.0
eslint.config.mjs → import withNuxt from './.nuxt/eslint.config.mjs'
```

`@nuxt/eslint` generates a Nuxt-aware flat config that includes `plugin:vue/vue3-recommended` rules.

### Quality gate

```bash
npm run lint       # ESLint — zero errors required
npm run typecheck  # nuxt typecheck (vue-tsc) — zero TS errors required
npm run build      # Nuxt production build — catches SSR-only errors
```

Build is explicitly included because SSR can surface errors (missing API base, server-only code in client context, missing env vars) that client-only dev mode hides.

---

## Known volar warning

```
[Vue] Resolve plugin path failed: vue-router/volar/sfc-route-blocks
```

This is a non-fatal compatibility warning between `vue-tsc 3.2.5` and `vue-router 4.6.4`. The `sfc-route-blocks` plugin adds route-type awareness inside `definePageMeta`. The warning does not prevent typecheck from passing (`Type check passed`, exit 0). It is expected with the current pinned versions.

---

## Page vs component vs composable — responsibility separation

| Layer | Responsibility | Rule |
|---|---|---|
| **Page** (`pages/`) | Route-level layout, data fetch, state management | Owns `useFetch`/`useAsyncData` calls |
| **Component** (`components/`) | Focused, reusable UI with typed props/events | Never calls the network directly |
| **Composable** (`composables/`) | Shared reactive behavior across pages | Added in Module 11 for auth state |

The common mistake is calling `useFetch` inside a display component — this couples the component to a specific endpoint and makes it untestable in isolation.

---

## What Module 11 adds to this foundation

- Auth composable (`useAuth`) — login, register, logout, token refresh
- `useApi` — `$fetch` wrapper applying the Bearer token automatically
- Dashboard and project pages wired to real API responses
- Pinia store for authenticated user state (when shared across multiple components)
