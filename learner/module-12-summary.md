# Module 12 — SSR, SEO, Accessibility, and Performance

## Route rendering and indexing matrix

| Route | Rendering | Auth dependency | Index? | Freshness | 404 behavior |
|---|---|---|---|---|---|
| `/` | Prerendered | None | ✅ index | Static | N/A |
| `/login` | Client | None (redirect if authed) | ❌ noindex | N/A | N/A |
| `/register` | Client | None (redirect if authed) | ❌ noindex | N/A | N/A |
| `/dashboard` | Client | Required (in-memory token) | ❌ noindex | Live | N/A |
| `/projects` | Client | Required | ❌ noindex | Live | N/A |
| `/projects/[id]` | Client | Required | ❌ noindex | Live | N/A |
| `/public/projects/[slug]` | SSR + SWR 60 s | None | ✅ index | 60 s stale | Real HTTP 404 |

**Why protected pages are noindex**: They require in-memory auth state. Crawlers receive the client shell without meaningful content. Indexing shell pages creates unhelpful search results and may expose user-specific URLs.

**Why public pages must not depend on client auth state**: SEO bots execute limited JavaScript. Content that relies on `onMounted` or Pinia stores will be missing from the initial HTML. `useAsyncData` with server-side fetch ensures the project name, description, and task counts exist in the raw HTML response.

---

## Key implementation changes

### `[slug].vue` — server-rendered with real 404

Replaced `useFetch(..., { ignoreResponseError: true })` + template error branch (which returns HTTP 200 with an error message) with:

```typescript
const { data: project, error } = await useAsyncData<PublicProject>(
  `public-project-${slug}`,
  () => $fetch(`/api/v1/projects/public/${slug}`, {
    baseURL: import.meta.server ? config.apiInternalBase : config.public.apiBase,
  }),
)

if (!project.value || error.value) {
  throw createError({ statusCode: 404, statusMessage: 'Project not found' })
}
```

- `import.meta.server` selects the internal Docker network base on the server and the public base on the client — avoids routing requests through the browser for the initial load.
- `createError({ statusCode: 404 })` sends a genuine HTTP 404 to crawlers and browsers. The previous code returned HTTP 200 with an error message on screen, which is a common SSR failure mode.

### Route rules in `nuxt.config.ts`

```typescript
routeRules: {
  '/': { prerender: true },                  // static — built once
  '/public/projects/**': { swr: 60 },        // SSR + 60 s stale-while-revalidate
  '/dashboard': { ssr: false },              // client-only auth state
  '/projects': { ssr: false },
  '/projects/**': { ssr: false },
  '/login': { ssr: false },
  '/register': { ssr: false },
},
```

`swr: 60` means Nuxt caches the server-rendered HTML for 60 seconds. Subsequent requests within that window are served from cache (fast), then revalidated in the background. If the backend is down and a cached page exists, the stale page is served. Document this tradeoff: stale data is visible for up to 60 s after a project update.

### `useSeoMeta` additions

| Page | Changes |
|---|---|
| `/` | Added `ogTitle`, `ogDescription`, `ogType: 'website'` |
| `/login` | Added `robots: 'noindex'` |
| `/register` | Added `robots: 'noindex'` |
| `/dashboard` | Added `robots: 'noindex'` |
| `/projects` | Added `robots: 'noindex'` |
| `/projects/[id]` | Added `robots: 'noindex'` |
| `/public/projects/[slug]` | `ogTitle`, `ogDescription`, `ogType: 'website'`, dynamic description fallback |

### Backend `PublicProjectRead`

Added a new response schema with `task_count` and `done_count` computed from the project's tasks. The public endpoint calls `get_public_by_slug_with_counts` which loads the project and counts tasks in memory.

---

## Accessibility changes

| Change | Where | Benefit |
|---|---|---|
| Skip link (`<a href="#main-content">`) | `app.vue` | Keyboard users bypass the nav on every page |
| `aria-current="page"` on active nav link | `AppHeader.vue` | Screen readers announce the current page |
| `role="alert"` on `UiErrorAlert` | Already present | Error messages announced immediately |
| `role="status" aria-live="polite"` on `UiLoadingSpinner` | Already present | Loading state announced to screen readers |
| `for`/`id` pairs on all form labels | login, register | Every input is programmatically labelled |
| `aria-describedby` for hints | login (email hint), register (password hint) | Hints read alongside the input |

**Focus ring**: The global `:focus-visible` rule in `main.css` provides a 2 px indigo outline on all interactive elements. Buttons and inputs both inherit this.

**Keyboard test results**:
- Tab through home page: brand → register → sign in
- Tab through login form: email → password → submit button
- Tab through header nav: all links reachable, current page has `aria-current`
- Skip link visible on first Tab press, jumps focus to `#main-content`

---

## Performance observation

**Baseline observation**: On the public project page, `useAsyncData` runs on the server. The browser receives pre-rendered HTML including `<title>`, `<meta>`, `<h1>`, and task counts. No additional API call is needed on hydration because Nuxt transfers the payload in `<script id="__NUXT_DATA__">`.

**Identified tradeoff**: The `swr: 60` policy means updated task counts are stale for up to 60 seconds. For a demo/workshop app this is acceptable. A production app would either reduce the TTL or use cache invalidation on write.

**No premature optimization performed**: The home page is prerendered (zero runtime cost). Auth pages are client-only (no unnecessary SSR work). The public page is the only SSR route and its cache policy is documented above.

---

## Quality gates

```
lint:        0 errors
typecheck:   0 errors (exit 0)
build:       Build complete (exit 0)
test:        No test files found, exit 0 (Module 13 adds tests)
backend:     All tests pass (exit 0)
```
