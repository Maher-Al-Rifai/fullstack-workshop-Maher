# Module 12: SSR, SEO, accessibility, and performance

**Guided effort:** 8 hours  
**Required branch:** `learning/12-ssr-seo-a11y`  
**Phase:** Frontend

## Objectives

- Explain universal rendering, hydration, prerendering, client rendering, caching, and route rules.
- Deliver a public project page whose meaningful content and metadata exist in initial HTML.
- Implement baseline crawl, canonical, error-status, accessibility, and performance considerations.
- Validate rendered output through source/HTTP and user-oriented checks rather than visual appearance alone.

## Prerequisites

- Modules 10–11 complete.
- At least one public project available from the API.

## Concepts and context

SEO-friendly rendering means accurate, accessible, crawlable content—not a framework checkbox. Nuxt can render HTML on the server, prerender fixed routes, or render on the client. The public project page uses server-side data and contextual metadata; protected dashboard pages can remain client-authenticated and `noindex`.

Hydration requires server and client initial output to match. Random values, current time, browser-only APIs, locale differences, or client-only auth state can cause mismatches. Caching improves performance but introduces freshness and failure tradeoffs.

## Step-by-step lab

### 1. Classify each route

Create a table for home, login, register, dashboard, projects, project detail, and public project:

- intended audience;
- SSR/prerender/client behavior;
- authentication dependency;
- indexing policy;
- freshness requirement;
- failure status.

Justify why protected pages should not be indexed and why public content should not depend on client-only auth state.

### 2. Implement server-rendered public project

In `/public/projects/[slug]`, use `useAsyncData` or an equivalent server-compatible data fetch with `apiInternalBase` on the server and public base in browser contexts. Missing/private resources must produce a real `404`.

Render project name, description, task count, completed count, and completion percentage with semantic content.

### 3. Add page-specific metadata

Use `useSeoMeta` for title, description, Open Graph fields, and appropriate type. Plan canonical URL once a stable public domain exists. Set `robots: noindex` on auth/private pages.

Do not put secrets or private project fields in metadata.

### 4. Configure route rendering/cache

Prerender the static home page. For public projects, use server rendering with a short revalidation/SWR policy only if stale content is acceptable. Document what happens when the backend is down and a cached page exists.

### 5. Validate initial HTML

Use a fresh public slug:

```bash
curl --fail http://localhost:3000/public/projects/<slug> > /tmp/public-project.html
grep -i '<title' /tmp/public-project.html
grep -i 'description' /tmp/public-project.html
grep -i '<h1' /tmp/public-project.html
```

Also use browser “view source,” not only the hydrated Elements tree. Confirm project content is present before client JavaScript.

### 6. Accessibility audit

Keyboard-test public and authenticated journeys. Inspect:

- landmarks and headings;
- input labels and error relationships;
- focus visibility/order;
- link/button names;
- status text independent of color;
- zoom/narrow viewport;
- long names/descriptions;
- reduced motion if animations exist.

Record issues and fix core barriers.

### 7. Performance observation

Use browser performance/network tools or Lighthouse as a diagnostic, not a scoring contest. Record initial document, JS, CSS, API calls, blocking resources, layout shift, and server response. Identify one practical improvement without premature optimization.

### 8. Add SEO/SSR acceptance test plan

Plan or implement checks for:

- real `200` public page and `404` missing page;
- title/description and project content;
- private pages `noindex`;
- no hydration errors;
- public data freshness policy.

## Validation checklist

- [ ] Route rendering/indexing table is complete and reasoned.
- [ ] Public project content and metadata are present in initial HTML.
- [ ] Missing/private public slugs return a real 404.
- [ ] Protected/auth pages are marked noindex.
- [ ] No hydration warning occurs in the normal journey.
- [ ] Keyboard, labels, headings, focus, zoom, and narrow layout are checked.
- [ ] One performance observation led to a justified improvement or documented non-action.

## Independent challenge

Add a generated sitemap and robots configuration that includes only appropriate public URLs. Explain how public projects are discovered, how stale/deleted projects are removed, and how the solution scales beyond a small dataset.

## Common failure modes

- Inspecting only the hydrated DOM and claiming SSR works.
- Using one static title/description for every public page.
- Returning a styled error page with HTTP 200 for missing content.
- Caching without defining acceptable staleness.
- Treating automated Lighthouse/accessibility scores as complete proof.

## Evidence to submit

- Route rendering/indexing matrix.
- Initial HTML excerpts for content and metadata.
- 404 response evidence.
- Accessibility findings and fixes.
- Performance trace/observation and decision.

## Commit checkpoint

```text
feat(web): deliver accessible server-rendered public pages
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [accessibility-and-seo.md](../docs/accessibility-and-seo.md)
- [rendering](https://nuxt.com/docs/guide/concepts/rendering)
- [seo-meta](https://nuxt.com/docs/getting-started/seo-meta)
- [https://www.w3.org/TR/WCAG22/](https://www.w3.org/TR/WCAG22/)
- [javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
