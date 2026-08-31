# Module 12 — Demo Guide: SSR, SEO, Accessibility, and Performance

---

## 1. Start the full stack

```powershell
docker compose up --build -d
docker compose ps   # all healthy
```

---

## 2. Create a public project (needed for SSR demo)

Log in at `http://localhost:3000/login`. Navigate to `/projects`, create a project with **Make this project public** checked. Add 3–4 tasks to it; advance at least one to "done". Note the project's slug from the URL or the detail page.

---

## 3. Verify content is in the initial HTML

Open a new PowerShell window and run:

```powershell
curl http://localhost:3000/public/projects/<your-slug> -UseBasicParsing | Select-Object -ExpandProperty Content | Select-String -Pattern "title|h1|description|task"
```

Or in bash inside the container:

```bash
curl -s http://localhost:3000/public/projects/<your-slug> | grep -iE '<title|<h1|description|task'
```

**What to show**: The project name, `<title>` tag, `<meta name="description">`, and task counts exist in the raw HTML **before** any client JavaScript runs. This is SSR working correctly.

---

## 4. Compare to wrong approach

Open DevTools → Elements. The hydrated DOM also shows the content. Click "View page source" (Ctrl+U). The source must show the same content. If only Elements shows it but source does not, the page is client-rendered (broken for SEO).

---

## 5. Verify real 404 for missing slug

```powershell
curl http://localhost:3000/public/projects/does-not-exist -UseBasicParsing | Select-Object StatusCode
# Should print: 404
```

Show the 404 in the Network tab: status code is 404, not 200 with an error page. This matters for crawlers — a 200 "not found" page gets indexed.

---

## 6. Verify `noindex` on auth pages

Open DevTools → Elements → head while on `/dashboard`:

```html
<meta name="robots" content="noindex">
```

Verify it is absent on `/public/projects/<slug>` (public page should be indexable).

---

## 7. Show OG metadata on the public page

In DevTools → Elements → head on the public project page, show:

```html
<meta property="og:title" content="<project name>">
<meta property="og:description" content="...">
<meta property="og:type" content="website">
```

Paste the URL into a social media preview tool (e.g., `https://www.opengraph.xyz`) to show how it renders when shared.

---

## 8. Keyboard accessibility audit

From the home page, press **Tab** repeatedly:
1. First Tab: skip link appears ("Skip to main content") — press Enter and focus moves to `<main>`
2. Tab again: brand link, then nav links with `aria-current="page"` on the current route
3. Tab to the Register button → activate → Tab through the registration form

On the login form:
- Tab cycles: email → password → submit
- Enter on submit fires the form (keyboard operable)
- After an invalid login, `role="alert"` on `UiErrorAlert` announces the error to screen readers without focus moving

---

## 9. Show SWR caching (route rules)

Explain that `/public/projects/**` is configured with `swr: 60`. Demonstrate:

1. Hit the page — server renders, 200 with full HTML
2. Update the project description in the app
3. Hit the page again within 60 s — old description is served (stale cache)
4. Wait 60 s and hit again — updated description appears

Explain tradeoff: freshness window vs. server load. For a workshop app, 60 s is acceptable.

---

## 10. Show prerendered home page

After `npm run build`, check `.output/public/index.html` exists — the home page was built as static HTML at build time, requiring zero server work per request.

```powershell
Test-Path "frontend/.output/public/index.html"  # should be True
```

---

## 11. Quality gate verification

```powershell
cd frontend
npm run lint        # 0 errors
npm run typecheck   # exit 0
npm run build       # Build complete
npm test            # exit 0 (no tests yet)
```

---

## Summary checklist

- [ ] Public project page content + metadata in initial HTML source
- [ ] Missing slug returns HTTP 404 (verified via curl)
- [ ] `noindex` visible in `<head>` on auth/private pages
- [ ] Skip link appears on first Tab press
- [ ] `aria-current="page"` on active nav link
- [ ] SWR caching behavior explained with tradeoff documented
- [ ] Home page is prerendered (static file exists after build)
- [ ] All quality gates pass
